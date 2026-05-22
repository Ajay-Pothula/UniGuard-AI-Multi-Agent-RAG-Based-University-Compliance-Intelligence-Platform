import fitz  # PyMuPDF
from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.vector_store import add_texts
from app.services.aws_service import upload_file_to_s3

async def process_pdf(file: UploadFile) -> str:
    """
    Reads a raw uploaded PDF file, extracts the text using PyMuPDF,
    chunks the text via LangChain, and inserts the chunks into the Vector Store.
    """
    # 1. Read PDF bytes into memory
    content = await file.read()
    
    # 2. Extract Text and Chunk Page by Page
    all_chunks = []
    all_metadatas = []
    ids = []
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    
    with fitz.open(stream=content, filetype="pdf") as doc:
        for page_num in range(len(doc)):
            page_text = doc[page_num].get_text()
            if page_text.strip():
                page_chunks = text_splitter.split_text(page_text)
                for i, chunk in enumerate(page_chunks):
                    all_chunks.append(chunk)
                    all_metadatas.append({
                        "source": file.filename, 
                        "page": page_num + 1, 
                        "chunk": i
                    })
                    ids.append(f"{file.filename}-p{page_num + 1}-c{i}")
            
    if not all_chunks:
        return "Warning: The PDF appeared to be empty or contained only images."

    # --- NEW: Upload to AWS S3 (for Amazon Portfolio) ---
    s3_url = upload_file_to_s3(content, file.filename)
    if s3_url:
        print(f"File successfully backed up to AWS S3: {s3_url}")
    else:
        print("Warning: AWS S3 upload failed. Check your credentials.")
    
    # Send directly to the vector_store.py service we built
    add_texts(texts=all_chunks, metadatas=all_metadatas, ids=ids)
    
    return f"Successfully processed {file.filename} into {len(all_chunks)} searchable chunks!"

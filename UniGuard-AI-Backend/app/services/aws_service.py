import boto3
import os
from botocore.exceptions import NoCredentialsError

# Load credentials from environment
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

def upload_file_to_s3(file_content, filename):
    """
    Uploads a file to an S3 bucket and returns the S3 URL.
    """
    if not AWS_ACCESS_KEY or not AWS_SECRET_KEY or not AWS_BUCKET_NAME:
        print("Error: AWS credentials or S3 bucket name not set in .env file.")
        return None

    try:
        s3_client.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=filename,
            Body=file_content,
            ContentType="application/pdf"
        )
        s3_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{filename}"
        return s3_url
    except NoCredentialsError:
        return None
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.security import create_access_token
from app.core.config import ADMIN_PIN

router = APIRouter()

class LoginRequest(BaseModel):
    pin: str

@router.post("/auth/login", summary="Admin Login Endpoint")
def login(req: LoginRequest):
    # Instead of hardcoding, we validate against the environment config
    if req.pin == ADMIN_PIN:
        token = create_access_token({"role": "admin"})
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid admin PIN")

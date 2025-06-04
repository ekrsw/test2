from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import uuid4

from app.config import settings
from app.database import get_db
from app.models.user import User
from .redis import is_token_blacklisted

security = HTTPBearer()

def load_private_key() -> str:
    """Load RSA private key from file"""
    try:
        with open(settings.jwt_private_key_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="JWT private key not found"
        )

def load_public_key() -> str:
    """Load RSA public key from file"""
    try:
        with open(settings.jwt_public_key_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="JWT public key not found"
        )

def create_access_token(data: Dict[str, Any]) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({
        "exp": expire,
        "type": "access",
        "jti": str(uuid4())
    })
    
    private_key = load_private_key()
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "jti": str(uuid4())
    })
    
    private_key = load_private_key()
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

async def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token"""
    try:
        public_key = load_public_key()
        payload = jwt.decode(token, public_key, algorithms=[settings.jwt_algorithm])
        
        # Check if token is blacklisted
        jti = payload.get("jti")
        if jti and await is_token_blacklisted(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    payload = await verify_token(credentials.credentials)
    
    # Check token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload invalid"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
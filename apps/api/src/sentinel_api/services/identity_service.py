import pyotp
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
from sentinel_api.config.settings import settings

class IdentityService:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except ValueError:
            return False

    @staticmethod
    def generate_totp_secret() -> str:
        return pyotp.random_base32()

    @staticmethod
    def get_totp_uri(secret: str, email: str, issuer: str = "Sentinel AI") -> str:
        return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)

    @staticmethod
    def verify_totp(secret: str, code: str) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(code)

    @staticmethod
    def create_jwt_tokens(user_id: str, scopes: list[str] = None) -> Tuple[str, str]:
        """Returns (access_token, refresh_token)."""
        now = datetime.utcnow()
        
        # Access Token
        access_payload = {
            "sub": str(user_id),
            "exp": now + timedelta(seconds=settings.JWT_EXPIRES_IN),
            "iat": now,
            "type": "access",
            "scopes": scopes or []
        }
        access_token = jwt.encode(access_payload, settings.JWT_SECRET, algorithm="HS256")
        
        # Refresh Token (valid for 7 days)
        import uuid
        jti = str(uuid.uuid4())
        refresh_payload = {
            "sub": str(user_id),
            "exp": now + timedelta(days=7),
            "iat": now,
            "jti": jti,
            "type": "refresh"
        }
        refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET, algorithm="HS256")
        
        return access_token, refresh_token

    @staticmethod
    def decode_jwt(token: str) -> Dict[str, Any]:
        """Decodes JWT and raises PyJWTError if invalid or expired."""
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])

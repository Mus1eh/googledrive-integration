from pydantic import BaseModel, EmailStr


class GoogleConnectResponse(BaseModel):
    authorization_url: str


class GoogleLoginResponse(BaseModel):
    authorization_url: str


class GoogleUserInfo(BaseModel):
    google_user_id: str
    email: EmailStr
    email_verified: bool

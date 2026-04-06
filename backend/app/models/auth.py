from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    nickname: str = Field(..., min_length=1, max_length=50)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class WechatLoginRequest(BaseModel):
    code: str  # 微信临时登录凭证


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserProfile(BaseModel):
    id: str
    email: str
    nickname: str
    avatar_url: str | None = None

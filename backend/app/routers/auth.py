from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import httpx

from app.config import get_settings
from app.database import get_supabase_admin
from app.models.auth import RegisterRequest, LoginRequest, WechatLoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["认证"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(user_id: str, email: str, settings) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": user_id, "email": email, "exp": expire}
    return jwt.encode(payload, settings.effective_jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, settings=Depends(get_settings)):
    db = get_supabase_admin()

    # 检查邮箱是否已注册
    existing = db.table("users").select("id").eq("email", body.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    hashed_pw = pwd_context.hash(body.password)
    result = db.table("users").insert({
        "email": body.email,
        "password_hash": hashed_pw,
        "nickname": body.nickname,
    }).execute()

    user = result.data[0]
    token = create_token(user["id"], user["email"], settings)
    return TokenResponse(
        access_token=token,
        user={"id": user["id"], "email": user["email"], "nickname": user["nickname"]},
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, settings=Depends(get_settings)):
    db = get_supabase_admin()
    result = db.table("users").select("*").eq("email", body.email).execute()

    if not result.data:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    user = result.data[0]
    if not pwd_context.verify(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    token = create_token(user["id"], user["email"], settings)
    return TokenResponse(
        access_token=token,
        user={"id": user["id"], "email": user["email"], "nickname": user["nickname"]},
    )


@router.post("/wechat", response_model=TokenResponse)
async def wechat_login(body: WechatLoginRequest, settings=Depends(get_settings)):
    """微信小程序登录：用 code 换取 openid"""
    # 需要在 settings 里配置 WECHAT_APPID 和 WECHAT_SECRET
    appid = getattr(settings, "wechat_appid", "")
    secret = getattr(settings, "wechat_secret", "")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.weixin.qq.com/sns/jscode2session",
            params={"appid": appid, "secret": secret, "js_code": body.code, "grant_type": "authorization_code"},
        )
        wx_data = resp.json()

    if "errcode" in wx_data and wx_data["errcode"] != 0:
        raise HTTPException(status_code=400, detail=f"微信登录失败: {wx_data.get('errmsg')}")

    openid = wx_data["openid"]
    db = get_supabase_admin()

    # 查找或创建用户
    existing = db.table("users").select("*").eq("wechat_openid", openid).execute()
    if existing.data:
        user = existing.data[0]
    else:
        result = db.table("users").insert({
            "wechat_openid": openid,
            "nickname": f"用户_{openid[-6:]}",
            "email": f"{openid}@wechat.mindbase",
        }).execute()
        user = result.data[0]

    token = create_token(user["id"], user.get("email", ""), settings)
    return TokenResponse(
        access_token=token,
        user={"id": user["id"], "email": user.get("email", ""), "nickname": user["nickname"]},
    )

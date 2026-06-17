# JWTの生成・検証ユーティリティ
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
import jwt
from app.config import security_settings

APP_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = APP_DIR / "templates"


# JWTトークンを生成して返す
def generate_access_token(
    data: dict,
    expiry: timedelta = timedelta(minutes=15),  # デフォルトの有効期限
) -> str:
    return jwt.encode(
        payload={
            "jti": str(uuid4()),  # ログアウト管理用のユニークID（str()でJSON対応）
            **data,  # 辞書を展開して同じ階層に並べる
            "exp": datetime.now(timezone.utc) + expiry,
        },
        algorithm=security_settings.JWT_ALGORITHM,
        key=security_settings.JWT_SECRET,
    )


# JWTトークンを検証・解読してpayloadを返す
def decode_access_token(token: str) -> dict | None:
    try:  # 不正なトークンが来てもクラッシュしないようにtry/exceptで囲む
        return jwt.decode(
            jwt=token,
            key=security_settings.JWT_SECRET,
            algorithms=[
                security_settings.JWT_ALGORITHM
            ],  # 複数形・リスト形式はjwtのルール
        )
    # ログイン証期限切れの報告
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="expired token",  # 時間経過で期限が切れました
        )
    except jwt.PyJWTError:  # 期限切れ以外のjwt関連エラーをまとめてキャッチ
        return None

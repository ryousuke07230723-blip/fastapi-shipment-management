# JWTをヘッダーから取り出して検証する仕組み
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, OAuth2PasswordBearer

from app.services.utils import decode_access_token

# ログインエンドポイントからトークンを取り出すFastAPI組み込みの仕組み
oauth2_schema_seller = OAuth2PasswordBearer(tokenUrl="/seller/token")

oauth2_schema_partner = OAuth2PasswordBearer(tokenUrl="/partner/token")


# --------------------------------------------------------------------


# リクエストヘッダーからJWTを取り出して検証するクラス
# HTTPBearerを継承してカスタマイズ（OAuth2PasswordBearerより細かい制御が可能）
class AccessTokenBearer(HTTPBearer):
    async def __call__(self, request):
        # 親クラスHTTPBearerにリクエストを渡し、Authorizationヘッダーからトークン部分だけを取り出す
        auth_credentials = await super().__call__(request)
        token = auth_credentials.credentials  # "Bearer xxxxx" の xxxxx 部分を取り出し
        token_data = decode_access_token(token)  # トークンを解読してpayloadを取得

        if token_data is None:
            raise HTTPException(status_code=401, detail="Not Authorized")
        return token_data


access_token_bearer = AccessTokenBearer()

# エンドポイントの引数に書くだけでJWT認証＋payload取得ができる型
TokenDep = Annotated[dict, Depends(access_token_bearer)]

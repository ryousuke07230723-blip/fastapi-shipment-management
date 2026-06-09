# Sellerのエンドポイント（登録・ログイン・ログアウト）
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.schemas.dependencies import SellerServiceDep, get_seller_access_token
from app.api.schemas.seller import SellerCreate, SellerRead
from app.database.redis import add_jwt_to_blacklist

router = APIRouter(prefix="/seller", tags=["Seller"])


# 新規seller登録
# response_modelでレスポンスからパスワードを除いた形に整形
@router.post("/signup", response_model=SellerRead)
async def register_sller(seller: SellerCreate, service: SellerServiceDep):
    return await service.add(seller)


# sellerログイン・JWTトークンを発行して返す
# OAuth2PasswordRequestForm：フォーム形式（JSON以外）でusername/passwordを受け取るFastAPIの仕組み
@router.post("/token")
async def login_seller(
    request_form: Annotated[  # これからアカウント作る
        OAuth2PasswordRequestForm, Depends()
    ],  # OAuth2では username / password が固定のフィールド名
    service: SellerServiceDep,
):

    token = await service.token(
        request_form.username,
        request_form.password,
    )
    return {"access_token": token, "type": "jwt"}


# sellerログアウト・JWTをブラックリストに登録して無効化
@router.get("/logout")
async def logout_seller(
    token_data: Annotated[  # すでにトークン状態を受け取る
        dict, Depends(get_seller_access_token)
    ],  # トークンを解読してjtiを取得
):
    await add_jwt_to_blacklist(token_data["jti"])
    return {
        "detail": "Successfully logged out",
    }

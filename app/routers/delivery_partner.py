# DeliveryPartnerのエンドポイント（登録・ログイン・更新・ログアウト）
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.schemas.delivery_partner import (
    DeliveryPartnerCreate,
    DeliveryPartnerRead,
    DeliveryPartnerUpdate,
)
from app.api.schemas.dependencies import (
    DeliveryPartnerDep,
    DeliveryPartnerServiceDep,
    get_partner_access_token,
)
from app.core.exception import FastShipError
from app.database.redis import add_jwt_to_blacklist

router = APIRouter(prefix="/partner", tags=["Delivery Partner"])


# 新規配達パートナー登録
# response_modelでレスポンスからパスワードを除いた形に整形
@router.post("/signup", response_model=DeliveryPartnerRead)
async def register_delivery_partcner(
    partner: DeliveryPartnerCreate,
    service: DeliveryPartnerServiceDep,
):
    return await service.add(partner)


# 配達パートナーログイン・JWTトークンを発行して返す
# OAuth2PasswordRequestForm：フォーム形式（JSON以外）でusername/passwordを受け取るFastAPIの仕組み
@router.post("/token")
async def login_delivery_partner(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: DeliveryPartnerServiceDep,
):
    token = await service.token(
        request_form.username,  # OAuth2では username / password が固定のフィールド名
        request_form.password,
    )
    return {"access_token": token, "type": "jwt"}


# 配達パートナー情報を更新
# model_dump(exclude_none=True)で送られてきた項目だけを更新対象にする
@router.post("/", response_model=DeliveryPartnerRead)
async def update_delivery_partner(
    partner_update: DeliveryPartnerUpdate,
    partner: DeliveryPartnerDep,
    service: DeliveryPartnerServiceDep,
):
    update = partner_update.model_dump(exclude_none=True)

    if not update:  # 更新データが空なら400エラー
        raise FastShipError
    return await service.update(
        partner.sqlmodel_update(update),
    )


# 配達パートナーログアウト・JWTをブラックリストに登録して無効化
@router.get("/logout")
async def logout_delivery_partner(
    token_data: Annotated[
        dict, Depends(get_partner_access_token)
    ],  # トークンを解読してjtiを取得
):
    await add_jwt_to_blacklist(token_data["jti"])
    return {
        "detail": "Successfully logged out",
    }

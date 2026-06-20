# 各エンドポイントに自動注入するDep型をまとめた場所
from typing import Annotated
from uuid import UUID

from fastapi import BackgroundTasks, Depends, HTTPException, status

from app.core.exception import EntityNotFound, InvalidToken
from app.core.security import oauth2_schema_partner, oauth2_schema_seller
from app.database.models import DeliveryPartner, Seller
from app.database.redis import is_jti_blacklisted
from app.database.session import SessionDep
from app.services.delivery_partner import DeliveryPartnerService
from app.services.seller import SellerService
from app.services.shipment import ShipmentService
from app.services.shipment_event import ShipmentEventService
from app.services.utils import decode_access_token


# トークンを検証してpayloadを返す（ブラックリスト確認も含む）
async def _get_access_token(token: str) -> dict:
    data = decode_access_token(token)

    if data is None or await is_jti_blacklisted(data["jti"]):
        raise InvalidToken
    return data


# seller用トークン取得（oauth2_schema_sellerでヘッダーからトークンを受け取る
async def get_seller_access_token(
    token: Annotated[str, Depends(oauth2_schema_seller)],
) -> dict:
    return await _get_access_token(token)


# 配達員用トークン取得
async def get_partner_access_token(
    token: Annotated[str, Depends(oauth2_schema_partner)],
) -> dict:
    return await _get_access_token(token)


# トークンのpayloadからsellerをDBで検索して返す
async def get_current_seller(
    token_data: Annotated[dict, Depends(get_seller_access_token)],
    session: SessionDep,
):
    # token_data["user"]["id"] にユーザーIDが入っている
    # 例: {"user": {"id": "xxx", ...}, "jti": "...", "exp": ...}
    seller = await session.get(Seller, UUID(token_data["user"]["id"]))
    if seller is None:
        raise EntityNotFound
    return seller


# トークンのpayloadから配達員をDBで検索して返す
async def get_current_partner(
    token_data: Annotated[dict, Depends(get_partner_access_token)],
    session: SessionDep,
):
    partner = await session.get(DeliveryPartner, UUID(token_data["user"]["id"]))
    if partner is None:
        raise EntityNotFound
    return partner


# --------------------------------------------------------------------------


# ServiceにDBセッションを注入して返すファクトリ関数
def get_shipment_service(session: SessionDep, tasks: BackgroundTasks):
    return ShipmentService(
        session, DeliveryPartnerService(session), ShipmentEventService(session, tasks)
    )


def get_seller_service(session: SessionDep):
    return SellerService(session)


def get_delivery_partner_service(session: SessionDep):
    return DeliveryPartnerService(session)


# --------------------------------------------------------------------------

# エンドポイントの引数に書くだけでログイン済みユーザーを自動取得できる型
SellerDep = Annotated[Seller, Depends(get_current_seller)]  # 本人確認

# 本人確認
DeliveryPartnerDep = Annotated[DeliveryPartner, Depends(get_current_partner)]


# serviceへ繋ぐため(案内)
ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]

SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]

DeliveryPartnerServiceDep = Annotated[
    DeliveryPartnerService, Depends(get_delivery_partner_service)
]

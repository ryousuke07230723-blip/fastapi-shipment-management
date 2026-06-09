# Shipmentのエンドポイント（登録・取得・更新・削除）
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.schemas.dependencies import (
    DeliveryPartnerDep,
    SellerDep,
    ShipmentServiceDep,
)
from app.database.models import Shipment
from app.api.schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentUpdate

router = APIRouter(prefix="/shipment", tags=["Shipment"])


# 情報の入手
@router.get("", response_model=Shipment)
async def get_shipment(id: UUID, _: SellerDep, service: ShipmentServiceDep):
    shipment = await service.get(id)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id doesn't exist!",
        )
    return shipment


# 新規登録
@router.post("", response_model=ShipmentRead)
async def submit_shipment(
    seller: SellerDep,  # 荷物に「誰が登録したか」を記録するため
    shipment: ShipmentCreate,
    service: ShipmentServiceDep,
) -> Shipment:
    return await service.add(shipment, seller)


# 一部更新
@router.patch("/", response_model=ShipmentRead)
async def update_shipment(
    id: UUID,
    shipment_update: ShipmentUpdate,
    partner: DeliveryPartnerDep,  # 担当配達員以外は更新不可にするため
    service: ShipmentServiceDep,
):
    update = shipment_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data provided to update",
        )

    return await service.update(id, shipment_update, partner)


# 削除
@router.get("/cancel", response_model=ShipmentRead)
async def cancel_shipment(
    id: UUID,
    service: ShipmentServiceDep,
    seller: SellerDep,  # 荷物を登録した販売者本人だけがキャンセルできる
):
    return await service.cancel(id, seller)

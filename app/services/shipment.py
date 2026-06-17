# BaseServiceを直接継承しつつ、DeliveryPartnerServiceを__init__の引数として受け取る（継承ではなく「コンポジション」という設計パターン）。

from datetime import datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.shipment import ShipmentCreate, ShipmentUpdate
from app.database.models import DeliveryPartner, Seller, Shipment, ShipmentStatus
from app.services.shipment_event import ShipmentEventService

from .base import BaseService
from .delivery_partner import DeliveryPartnerService


class ShipmentService(BaseService[Shipment]):
    def __init__(
        self,
        session: AsyncSession,
        partner_service: DeliveryPartnerService,
        event_service: ShipmentEventService,
    ):
        super().__init__(Shipment, session)
        self.partner_service = partner_service
        self.event_service = event_service

    # 荷物を1件取得
    async def get(self, id: UUID) -> Shipment | None:
        return await self._get(id)

    # 荷物登録＋配達員を自動割当+登録履歴の追加
    async def add(self, shipment_create: ShipmentCreate, seller: Seller) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.now() + timedelta(days=3),  # 配達予定日
            seller_id=seller.id,
        )
        partner = await self.partner_service.assign_shipment(
            new_shipment,
        )
        new_shipment.delivery_partner_id = partner.id

        shipment = await self._add(new_shipment)

        event = await self.event_service.add(
            shipment=shipment,
            location=seller.zip_code,  # 販売者の住所
            status=ShipmentStatus.placed,
            description=f"assigned to {partner.name}",
        )
        shipment.timeline.append(event)  # 返す荷物データのtimelineにも追加

        return shipment

    # 荷物情報の更新
    async def update(
        self, id: UUID, shipment_update: ShipmentUpdate, partner: DeliveryPartner
    ) -> Shipment:
        shipment = await self.get(id)

        if shipment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment not found",
            )
        # 担当配達員以外は更新できない
        if shipment.delivery_partner_id != partner.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized",
            )

        update = shipment_update.model_dump(exclude_none=True)  # Noneの項目を除外
        if shipment_update.estimated_delivery:
            shipment.estimated_delivery = shipment_update.estimated_delivery
        # estimated_deliveryだけの更新は履歴不要（配送状況が変わらないため）
        if len(update) > 1 or not shipment_update.estimated_delivery:
            await self.event_service.add(shipment=shipment, **update)

        return await self._update(shipment)

    # 荷物をキャンセル・荷物を登録したseller本人のみ実行可能
    async def cancel(self, id: UUID, seller: Seller) -> Shipment:
        shipment = await self.get(id)
        if shipment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment not found",
            )
        # 登録したseller本人以外はキャンセルできない
        if shipment.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not Authorized",
            )
        event = await self.event_service.add(
            shipment=shipment,
            status=ShipmentStatus.cancelled,
        )
        shipment.timeline.append(event)  # 返す荷物データのtimelineにも追加
        return shipment

    # 荷物を削除
    async def delete(self, id: UUID) -> None:
        shipment = await self.get(id)
        if shipment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found"
            )

        return await self._delete(shipment)

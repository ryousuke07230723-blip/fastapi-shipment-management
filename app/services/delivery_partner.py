# SellerServiceと同じくUserServiceを継承するが、配達員固有の「郵便番号検索」と「荷物割り当てロジック」が追加される。

from typing import Sequence

from fastapi import HTTPException, status
from sqlmodel import any_, select

from app.api.schemas.delivery_partner import DeliveryPartnerCreate
from app.core.exception import (
    DeliveryPartnerCapacityExceeded,
    DeliveryPartnerNotAvailable,
)
from app.database.models import DeliveryPartner, Shipment

from .user import UserService


class DeliveryPartnerService(UserService[DeliveryPartner]):
    def __init__(self, session):
        super().__init__(DeliveryPartner, session)

    # _add_userを呼ぶ
    async def add(self, delivery_partner: DeliveryPartnerCreate):
        return await self._add_user(delivery_partner.model_dump())

    # 郵便番号で対応配達員を検索
    async def get_partner_by_zipcode(self, zipcode: int) -> Sequence[DeliveryPartner]:
        return (
            await self.session.scalars(
                select(DeliveryPartner).where(
                    zipcode == any_(DeliveryPartner.serviceable_zip_codes)
                )
            )
        ).all()

    # 最適な配達員を荷物に割り当てる
    async def assign_shipment(self, shipment: Shipment):
        eligible_partners = await self.get_partner_by_zipcode(shipment.destination)

        if not eligible_partners:
            raise DeliveryPartnerNotAvailable

        for partner in eligible_partners:
            if partner.current_handling_capacity > 0:
                partner.shipments.append(shipment)
                return partner

        raise DeliveryPartnerCapacityExceeded

    # 情報更新
    async def update(self, partner: DeliveryPartner):
        return await self._update(partner)

    # JWT発行
    async def token(self, email, password) -> str:
        return await self._generate_token(email, password)

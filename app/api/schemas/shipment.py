# routerとAPIの間
# Shipment用のリクエスト/レスポンス型定義
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.database.models import Seller, ShipmentEvent, ShipmentStatus


# 荷物系スキーマの共通フィールド
class BaseShipment(BaseModel):
    content: str
    weight: float = Field(le=25)
    destination: int


# 荷物情報をレスポンスとして返す（seller情報も含む）
class ShipmentRead(BaseShipment):
    id: UUID
    seller: Seller
    timeline: list[ShipmentEvent]
    estimated_delivery: datetime


# 荷物登録時に受け取る（BaseShipmentのフィールドのみ）
class ShipmentCreate(BaseShipment):
    client_contact_email: EmailStr
    client_contact_phone: int | None = Field(default=None)


# 荷物更新時に受け取る（Noneの項目は更新しない）
class ShipmentUpdate(BaseModel):
    location: int | None = Field(default=None)
    status: ShipmentStatus | None = Field(default=None)
    description: str | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)

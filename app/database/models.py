# DBのテーブル定義（カラム・リレーション）
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import ARRAY, INTEGER
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in transit"
    out_for_delivery = "out for delivery"
    delivered = "delivered"
    cancelled = "cancelled"


# 荷物のテーブル
class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,  # 自動でUUIDを生成
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )
    client_contact_email: EmailStr
    client_contect_phone: int | None

    content: str
    weight: float = Field(le=25)  # 25kg上限
    destination: int

    timeline: list["ShipmentEvent"] = Relationship(
        back_populates="shipment",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    estimated_delivery: datetime

    seller_id: UUID = Field(foreign_key="seller.id")
    # Relationshipで紐づけることでPythonからSeller/DeliveryPartnerオブジェクトに直接アクセスできる
    seller: "Seller" = Relationship(
        back_populates="shipments",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    delivery_partner_id: UUID = Field(foreign_key="delivery_partner.id")
    delivery_partner: "DeliveryPartner" = Relationship(
        back_populates="shipments",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    @property
    def status(self):
        if len(self.timeline) > 0:
            return self.timeline[-1].status
        else:
            return None


# -------------------------------------------------
# 配達状況のテーブル
class ShipmentEvent(SQLModel, table=True):
    __tablename__ = "shipment_event"
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )
    location: int
    status: ShipmentStatus
    description: str | None = Field(default=None)

    shipment_id: UUID = Field(foreign_key="shipment.id")
    shipment: Shipment = Relationship(
        back_populates="timeline",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


# --------------------------------------------------------------


# Seller・DeliveryPartner共通フィールドをまとめた基底クラス
class User(SQLModel):
    name: str
    email: EmailStr
    password_hash: str = Field(exclude=True)  # レスポンスに含めない


# 販売者のテーブル
class Seller(User, table=True):
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )
    address: str | None = Field(default=None)
    zip_code: int | None = Field(default=None)
    # 1人のSellerに複数のShipmentが紐づくためlist
    shipments: list[Shipment] = Relationship(
        back_populates="seller",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


# --------------------------------------------------------------


# 配達員のテーブル
class DeliveryPartner(User, table=True):
    __tablename__ = "delivery_partner"
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    # 配達員特有の情報を入れるためのカラム2つ
    serviceable_zip_codes: list[int] = Field(
        sa_column=Column(
            ARRAY(INTEGER)  # 整数の配列をPostgreSQLのARRAY型で保存
        ),
    )
    max_handling_capacity: int

    shipments: list[Shipment] = Relationship(
        back_populates="delivery_partner",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    # 配達中（未完了）の荷物一覧を返す
    @property
    def active_shipment(self):
        return [
            shipment
            for shipment in self.shipments
            if shipment.status != ShipmentStatus.delivered
            or shipment.status != ShipmentStatus.cancelled
        ]

    # 現在の受け入れ可能件数を返す（最大 - 配達中）
    @property
    def current_handling_capacity(self):
        return self.max_handling_capacity - len(self.active_shipment)

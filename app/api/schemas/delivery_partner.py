# DeliveryPartner用のリクエスト/レスポンス型定義
from pydantic import BaseModel, EmailStr


class BaseDeliveryPartner(BaseModel):
    name: str
    email: EmailStr
    serviceable_zip_codes: list[int]
    max_handling_capacity: int


# 客へ返す情報の形を決める人の1人
class DeliveryPartnerRead(BaseDeliveryPartner):
    pass


class DeliveryPartnerUpdate(BaseModel):
    serviceable_zip_codes: list[int]
    max_handling_capacity: int


# DBに入れる形を決める人の1人
class DeliveryPartnerCreate(BaseDeliveryPartner):
    password: str

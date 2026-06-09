# Seller用のリクエスト/レスポンス型定義
from pydantic import BaseModel, EmailStr


class BaseSeller(BaseModel):
    name: str
    email: EmailStr
    zip_code: int
    address: str | None = None


# 客へ返す情報の形を決める人の1人
class SellerRead(BaseSeller):
    pass


# DBに入れる形を決める人の1人
class SellerCreate(BaseSeller):
    password: str

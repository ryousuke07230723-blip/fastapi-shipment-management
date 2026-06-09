# super().__init__(Seller, session)とするだけで、BaseServiceのmodelにSellerがセットされる。
# SellerはUserServiceの全機能を持ちながら、Sellerテーブルに特化した形になる。

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.seller import SellerCreate
from app.database.models import Seller

from app.services.user import UserService


class SellerService(UserService):
    def __init__(self, session: AsyncSession):
        super().__init__(Seller, session)

    # _add_sellerを呼ぶだけ
    async def add(self, seller_create: SellerCreate) -> Seller:
        return await self._add_user(seller_create.model_dump())

    # _generate_tokenを呼ぶだけ
    async def token(self, email, password) -> str:
        return await self._generate_token(email, password)

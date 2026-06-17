# session（DB接続）とmodel（どのテーブルか）を受け取り、全サービスの共通CRUD処理をここに集めた。
# 子クラスはこれを継承するだけで全操作が使えるようになる。

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

T = TypeVar("T",bound=SQLModel)

class BaseService(Generic[T]):
    def __init__(self, model: type[T], session: AsyncSession):
        self.model = model
        self.session = session

    # DBから1件取得
    async def _get(self, id: UUID):
        return await self.session.get(self.model, id)

    # DBに追加してcommit
    async def _add(self, entity: SQLModel):
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    # addを再利用(addと同じ)
    async def _update(self, entity: SQLModel):
        return await self._add(entity)

    # DBから削除
    async def _delete(self, entity: SQLModel):
        await self.session.delete(entity)

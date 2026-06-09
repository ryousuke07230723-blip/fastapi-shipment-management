# SellerもDeliveryPartnerも「ユーザーとしてログインできる」共通機能が必要。それをここに集約。
# メソッドが_始まりなのは「子クラス経由で使う内部メソッド」という慣例。直接インスタンス化しない前提。

from typing import Any

from fastapi import HTTPException, status
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from app.services.utils import generate_access_token

from .base import BaseService

password_context = PasswordHash.recommended()


class UserService(BaseService):
    def __init__(self, model: type[SQLModel], session: AsyncSession):
        super().__init__(model, session)

    # passwordをhash化してしてDBに保存
    async def _add_user(self, data: dict) -> Any:
        user = self.model(
            **data,
            password_hash=password_context.hash(data["password"]),
        )
        return await self._add(user)

    # メールアドレスでユーザー検索
    async def _get_by_email(self, email) -> Any:
        return await self.session.scalar(
            select(self.model).where(self.model.email == email)  # type: ignore
        )

    # パスワード照合後にJWT発行
    async def _generate_token(self, email, password) -> str:
        user = await self._get_by_email(email)

        if user is None or not password_context.verify(
            password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email or password is incorrect",
            )

        return generate_access_token(
            data={
                "user": {
                    "name": user.name,
                    "id": str(user.id),
                },
            }
        )

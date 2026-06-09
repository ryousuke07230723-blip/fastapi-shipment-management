# DBへの接続・セッション管理
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.config import db_settings

# DBへの接続エンジンを作成
engine = create_async_engine(
    url=db_settings.POSTGRES_URL,
    echo=True,
)


# 起動時にテーブルを作成
async def create_db_tables():
    async with engine.begin() as connection:
        from .models import Shipment  # noqa

        await connection.run_sync(SQLModel.metadata.create_all)


# リクエストごとにDBセッションを生成してyieldで渡し、終了後に自動クローズ
async def get_session():
    async_session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session


# エンドポイントの引数に書くだけでDBセッションを自動注入できる型
SessionDep = Annotated[AsyncSession, Depends(get_session)]

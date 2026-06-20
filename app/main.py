# アプリの起動・ルーター登録
from contextlib import asynccontextmanager


from fastapi import BackgroundTasks, FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.database.session import create_db_tables

from app.api.router import master_router
from app.services.notification import NotificationService
from app.core.exception import add_exception_handlers


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield
    print("...stopped")


app = FastAPI(lifespan=lifespan_handler)

app.include_router(master_router)
add_exception_handlers(app)


@app.get("/mail")
async def send_test_email(tasks: BackgroundTasks):
    tasks.add_task(
        NotificationService(tasks).send_email,
        recipients=["ryousuke07230723@gmail.com"],  # type: ignore
        subject="Test Mail Coming Through Once",
        body="You shouldn't be interested in every body...",
    )
    return {"detail": "mail sent"}


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="scalar API")

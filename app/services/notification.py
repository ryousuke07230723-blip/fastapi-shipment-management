# メール送信の処理
from fastapi_mail import NameEmail

from fastapi import BackgroundTasks


from app.config import notification_settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.services.utils import TEMPLATE_DIR


class NotificationService:
    def __init__(self, tasks: BackgroundTasks):
        self.tasks = tasks
        self.fastmail = FastMail(
            ConnectionConfig(
                **notification_settings.model_dump(),
                TEMPLATE_FOLDER=TEMPLATE_DIR,
            )
        )

    async def send_email(
        self,
        recipients: list[NameEmail],
        subject: str,
        body: str,
    ):

        self.tasks.add_task(
            self.fastmail.send_message,
            message=MessageSchema(
                recipients=recipients,
                subject=subject,
                body=body,
                subtype=MessageType.plain,
            ),
        )

    async def senemail_with_template(
        self,
        recipients: list[NameEmail],
        subject: str,
        context: dict,
        template_name: str,
    ):
        self.tasks.add_task(
            self.fastmail.send_message,
            message=MessageSchema(
                recipients=recipients,
                subject=subject,
                template_body=context,
                subtype=MessageType.html,
            ),
            template_name=template_name,
        )

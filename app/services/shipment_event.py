from app.database.models import Shipment, ShipmentEvent, ShipmentStatus
from app.services.base import BaseService
from app.services.notification import NotificationService


class ShipmentEventService(BaseService[ShipmentEvent]):
    def __init__(self, session, tasks):
        super().__init__(
            ShipmentEvent,
            session,
        )
        self.notification_service = NotificationService(tasks)

    async def add(
        self,
        shipment: Shipment,  # 紐付け&能力使用可
        location: int | None = None,  # 場所
        status: ShipmentStatus | None = None,  # 状態
        description: str | None = None,  # メモ
    ) -> ShipmentEvent:
        if not location or not status:
            last_event = await self.get_latest_event(shipment)

            location = location if location else last_event.location
            status = status if status else last_event.status

        new_event = ShipmentEvent(
            shipment_id=shipment.id,
            location=location,
            status=status,
            description=description
            if description
            else self.gnerate_description(status, location),
        )
        await self._notify(shipment, status)  # 状態に応じた通知を送る
        return await self._add(new_event)

    async def get_latest_event(self, shipment: Shipment):  # ラムダ関数↓
        if not shipment.timeline:
            return None

        return sorted(shipment.timeline, key=lambda item: item.created_at)[-1]

    async def gnerate_description(self, status: ShipmentStatus, location: int):
        match status:
            case ShipmentStatus.placed:  # 荷物が登録された
                return "assigned delivery partner"  # 配達員が割り当てられました
            case ShipmentStatus.out_for_delivery:  # 配達員が配達に出発した
                return "shipment out for delivery"  # 配達中です
            case ShipmentStatus.delivered:  # 荷物が届いた
                return "successfully delivered"  # 配達が完了しました
            case ShipmentStatus.cancelled:  # 荷物がキャンセルされた
                return "cancelled by seller"  # 販売者によってキャンセルされました
            case _:  # それ以外 (輸送中・拠点間を移動中)
                return f"scanned at {location}"  # ○○の拠点でスキャンされました

    async def _notify(self, shipment: Shipment, status: ShipmentStatus):

        if status == ShipmentStatus.in_transit:
            return None

        subject: str
        context = {}
        template_name: str

        match status:
            case ShipmentStatus.placed:
                subject = "Your Order is Shipped"
                context["seller"] = shipment.seller.name
                context["partner"] = shipment.delivery_partner.name
                template_name = "mail_placed.html"

            case ShipmentStatus.out_for_delivery:
                subject = "Your Order is Arriving Soon"
                template_name = "mail_out_for_delivery.html"

            case ShipmentStatus.delivered:
                subject = "Your Order is Delivered"
                context["seller"] = shipment.seller.name
                template_name = "mail_delivered.html"

            case ShipmentStatus.cancelled:
                subject = "Your Order is Cancelled"
                template_name = "mail_cancelled.html"

        await self.notification_service.send_email_with_template(
            recipients=[shipment.client_contact_email],
            subject=subject,
            context=context,
            template_name=template_name,
        )

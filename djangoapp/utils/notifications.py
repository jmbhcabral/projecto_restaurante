import logging
from typing import Iterable, List, Optional, Sequence

from django.db.models import QuerySet
from exponent_server_sdk import PushClient, PushMessage

from perfil.models import PushNotificationToken

logger = logging.getLogger(__name__)


def _as_token_list(tokens: Sequence[str]) -> List[str]:
    return [
        token for token in tokens
        if token and token.startswith("ExponentPushToken")
    ]


def _build_messages(tokens: Sequence[str], title: str, body: str, data: Optional[dict]) -> List[PushMessage]:
    payload = data or {}
    return [
        PushMessage(
            to=token,
            title=title,
            body=body,
            data=payload,
            sound="default",
            ttl=3600,
            priority="default",
            badge=None,
            channel_id="default",
            display_in_foreground=True,
            category=None,
            subtitle=None,
            mutable_content=False,
            expiration=None,
        )
        for token in _as_token_list(tokens)
    ]


def _extract_status(ticket) -> Optional[str]:
    if hasattr(ticket, "status"):
        return ticket.status
    if isinstance(ticket, dict):
        return ticket.get("status")
    return None


def _publish(messages: Sequence[PushMessage]) -> dict:
    if not messages:
        return {"sent": 0, "failed": 0, "responses": []}

    push_client = PushClient()
    try:
        responses = push_client.publish_multiple(messages)
    except Exception as exc:  # noqa: BLE001 - we want to log arbitrary SDK errors
        logger.exception("Falha ao enviar notificações push: %s", exc)
        return {"error": str(exc)}

    responses_list = list(responses)
    sent = sum(1 for ticket in responses_list if _extract_status(ticket) == "ok")
    failed = len(messages) - sent

    return {
        "sent": sent,
        "failed": failed,
        "responses": responses_list,
    }


def _normalize_user_ids(users: Iterable) -> List[int]:
    if isinstance(users, QuerySet):
        return list(users.values_list("pk", flat=True))
    normalized: List[int] = []
    for user in users:
        if isinstance(user, int):
            normalized.append(user)
        else:
            pk = getattr(user, "pk", None)
            if pk is not None:
                normalized.append(pk)
    return normalized


def send_push_notification(user, title: str, body: str, data: Optional[dict] = None) -> dict:
    """Envia uma notificação push para todos os tokens associados a um utilizador."""
    if not user:
        return {"error": "Utilizador inválido"}

    tokens = list(
        PushNotificationToken.objects.filter(user=user).values_list("expo_token", flat=True)
    )
    messages = _build_messages(tokens, title, body, data)
    if not messages:
        logger.info("Nenhum token válido encontrado para o utilizador %s", user)
        return {"error": "Nenhum token válido encontrado"}

    return _publish(messages)


def send_push_notifications_to_users(users: Iterable, title: str, body: str, data: Optional[dict] = None) -> dict:
    """Envia notificações push para um conjunto de utilizadores."""
    user_ids = _normalize_user_ids(users)
    if not user_ids:
        return {"sent": 0, "failed": 0, "responses": []}

    tokens = list(
        PushNotificationToken.objects.filter(user_id__in=user_ids).values_list("expo_token", flat=True)
    )
    messages = _build_messages(tokens, title, body, data)
    if not messages:
        return {"error": "Nenhum token válido encontrado"}

    return _publish(messages)


def send_push_notifications_to_all(title: str, body: str, data: Optional[dict] = None) -> dict:
    """Envia notificações push para todos os tokens registados no sistema."""
    tokens = list(PushNotificationToken.objects.values_list("expo_token", flat=True))
    messages = _build_messages(tokens, title, body, data)
    if not messages:
        return {"error": "Nenhum token válido encontrado"}

    return _publish(messages)

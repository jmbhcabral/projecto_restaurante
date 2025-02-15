from exponent_server_sdk import PushClient, PushMessage


def send_push_notification(user, title, message, notification_id=None, data=None):
    """Envia uma notificação push para todos os tokens do utilizador"""

    from perfil.models import (
        NotificationUser,
        NotificationUserSent,
        PushNotificationToken,
    )
    
    print('📩 Tentando enviar notificação para', user)

    # Buscar todos os tokens associados ao user
    tokens = PushNotificationToken.objects.filter(user=user).values_list("expo_token", flat=True)

    if not tokens:
        print("❌ ERRO: Nenhum token válido encontrado para o utilizador")
        return {"error": "Nenhum token válido encontrado"}

    push_client = PushClient()
    messages = [
        PushMessage(
            to=token, 
            title=title, 
            body=message, 
            data=data or {}, 
            sound="default", ttl=3600, 
            priority="default", 
            badge=None, 
            channel_id="default", 
            display_in_foreground=True, 
            category=None, subtitle=None, 
            mutable_content=False, 
            expiration=None)
        for token in tokens
    ]

    try:
        response = push_client.publish_multiple(messages)
        print("📩 Notificação enviada com sucesso. Resposta:", response)

        # Verificar se todos os tickets na resposta têm status "ok"
        all_sent = all(ticket.status == "ok" for ticket in response)

        if all_sent:
            # Buscar a notificação correspondente
            notification = NotificationUser.objects.filter(id=notification_id).first()

            if notification:
                # Atualizar ou criar um registro de envio
                NotificationUserSent.objects.update_or_create(
                    notification=notification,
                    user=user,
                    defaults={"status": "sent"}
                )
                print("✅ Status da notificação atualizado para 'sent'.")
            else:
                print("❌ ERRO: Notificação não encontrada para atualizar.")

        return response
    
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {str(e)}")
        return {"error": str(e)}

def send_push_notifications_to_all(title, message, data=None):
    """Envia uma notificação push para todos os utilizadores e grava os envios no banco de dados"""
    from perfil.models import (
        NotificationAll,
        NotificationAllSent,
        PushNotificationToken,
    )
    push_client = PushClient()
    messages = []
    failed_tokens = []
    success_count = 0

    notification, _ = NotificationAll.objects.get_or_create(
        title=title, message=message, data=data or {}
    )

    for token_obj in PushNotificationToken.objects.all():
        if token_obj.expo_token.startswith("ExponentPushToken"):
            messages.append(
                PushMessage(
                    to=token_obj.expo_token,
                    title=title,
                    body=message,
                    data=data or {},
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
            )

    if messages:
        try:
            response = push_client.publish_multiple(messages)

            # Verifica se todos os envios foram bem-sucedidos
            for index, message_response in enumerate(response):
                if message_response.get("status") == "ok":
                    success_count += 1
                else:
                    failed_tokens.append(messages[index].to)

            # Criar o registo no banco de dados
            status = "sent" if success_count > 0 else "failed"
            NotificationAllSent.objects.create(
                notification=notification,
                status=status
            )

            return {
                "success": success_count,
                "failed": len(failed_tokens),
                "failed_tokens": failed_tokens
            }

        except Exception as e:
            return {"error": str(e)}

    return {"error": "Nenhum token válido encontrado"}
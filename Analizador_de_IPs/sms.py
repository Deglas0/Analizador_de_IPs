import sqlite3
from twilio.rest import Client
from database import DB_NAME

# Função para enviar SMS usando Twilio
def send_sms_twilio(account_sid, auth_token, from_phone, to_phone, message):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=from_phone,
        to=to_phone
    )
    return message.sid

def verificar_erros_e_enviar_sms():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = "SELECT id, nome, ip, status FROM dispositivos WHERE status = 'não respondendo'"
        cursor.execute(query)
        dispositivos = cursor.fetchall()

        account_sid = 'SEU_TWILIO_ACCOUNT_SID'
        auth_token = 'SEU_TWILIO_AUTH_TOKEN'
        from_phone = 'SEU_TWILIO_PHONE_NUMBER'
        to_phone = '+5511999999999'  # Número de telefone de destino

        for id, nome, ip, status in dispositivos:
            message = (
                f"O aparelho com ID {id} de nome {nome} e IP {ip} apresentou erro: {status}"
            )
            sms_sid = send_sms_twilio(account_sid, auth_token, from_phone, to_phone, message)
            print(f"SMS enviado com SID: {sms_sid} para o dispositivo com ID {id}.")
    except sqlite3.Error as err:
        print(f"Erro: {err}")
    finally:
        cursor.close()
        conn.close()

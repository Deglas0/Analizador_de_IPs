from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import sqlite3

TWILIO_ACCOUNT_SID = 'AC0fe8d8ded28fde75016e61e28f1eb2e9'
TWILIO_AUTH_TOKEN = 'd9d7617319d0ecc3cd97a773420815e8'
TWILIO_NUMBER = '+17692103767'
DB_DISPOSITIVOS = 'Dispositivos.db'
DB_TELEFONES = 'Telefones.db'

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
        with sqlite3.connect(DB_DISPOSITIVOS) as conn:
            cursor = conn.cursor()
            query = "SELECT id, nome, ip, status FROM dispositivos WHERE status = 'não respondendo' OR camera = 'Desativa'"
            cursor.execute(query)
            dispositivos = cursor.fetchall()

            for id, nome, ip, status in dispositivos:
                with sqlite3.connect(DB_TELEFONES) as conn_telefone:
                    cursor_telefone = conn_telefone.cursor()
                    query_telefone = "SELECT numero FROM telefones"
                    cursor_telefone.execute(query_telefone)
                    telefones = cursor_telefone.fetchall()

                    for telefone in telefones:
                        to_phone = telefone[0]
                        message = f"Aviso: ID {id} está tendo problemas com {status} (IP: {ip})"
                        try:
                            sms_sid = send_sms_twilio(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER, to_phone,
                                                      message)
                            print(f"SMS enviado com SID: {sms_sid} para o dispositivo com ID {id}.")
                        except TwilioRestException as e:
                            print(f"Erro ao enviar SMS para {to_phone}: {e}")
    except sqlite3.Error as err:
        print(f"Erro: {err}")
import sqlite3
from twilio.rest import Client
from configuration_manager import ConfigurationManager

class TwilioManager:
    @staticmethod
    def send_sms_twilio(account_sid, auth_token, from_phone, to_phone, message):
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone
        )
        return message.sid

    @staticmethod
    def verificar_erros_e_enviar_sms():
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            query = "SELECT id, nome, ip, status FROM dispositivos WHERE status = 'não respondendo' OR camera = 'não operacional'"
            cursor.execute(query)
            dispositivos = cursor.fetchall()

            configuracao_twilio = ConfigurationManager.obter_twilio_configuracao()
            if not configuracao_twilio:
                print("Configurações de SMS não configuradas corretamente.")
                return

            account_sid, auth_token, from_phone = configuracao_twilio[-1][1:4]  # Usar a última configuração válida
            telefone, _ = ConfigurationManager.obter_configuracao()

            if not telefone or not account_sid or not auth_token or not from_phone:
                print("Configurações de SMS não configuradas corretamente.")
                return

            for id, nome, ip, status in dispositivos:
                message = (
                    f"O dispositivo com ID {id}, nome {nome} e IP {ip} está com status de erro: {status}"
                )
                sms_sid = TwilioManager.send_sms_twilio(account_sid, auth_token, from_phone, telefone, message)
                print(f"SMS enviado com SID: {sms_sid} para o dispositivo com ID {id}.")
        except sqlite3.Error as err:
            print(f"Erro: {err}")
        finally:
            cursor.close()
            conn.close()

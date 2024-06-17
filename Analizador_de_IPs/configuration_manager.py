import sqlite3

DB_NAME_SEC = 'configuracoes.db'

class ConfigurationManager:
    @staticmethod
    def criar_tabela_configuracoes():
        conn = sqlite3.connect(DB_NAME_SEC)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telefone TEXT,
            senha TEXT,
            account_sid TEXT,
            auth_token TEXT,
            from_phone TEXT
        )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def inserir_configuracao(telefone, senha):
        try:
            if telefone and senha:  # Certificar que telefone e senha não são nulos
                conn = sqlite3.connect(DB_NAME_SEC)
                cursor = conn.cursor()
                query = "INSERT INTO configuracoes (telefone, senha) VALUES (?, ?)"
                cursor.execute(query, (telefone, senha))
                conn.commit()
                print(f"Configuração inserida: telefone = {telefone}, senha = {senha}")
            else:
                print(f"Erro ao inserir configuração: telefone = {telefone}, senha = {senha}")
        except sqlite3.Error as err:
            print(f"Erro: {err}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obter_configuracao():
        try:
            conn = sqlite3.connect(DB_NAME_SEC)
            cursor = conn.cursor()
            query = "SELECT telefone, senha FROM configuracoes ORDER BY id DESC LIMIT 1"
            cursor.execute(query)
            configuracao = cursor.fetchone()
            return configuracao if configuracao else (None, None)
        except sqlite3.Error as err:
            print(f"Erro: {err}")
            return (None, None)
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obter_twilio_configuracao():
        try:
            conn = sqlite3.connect(DB_NAME_SEC)
            cursor = conn.cursor()
            query = "SELECT id, account_sid, auth_token, from_phone FROM configuracoes ORDER BY id DESC"
            cursor.execute(query)
            configuracoes = cursor.fetchall()
            return configuracoes
        except sqlite3.Error as err:
            print(f"Erro: {err}")
            return []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar_telefone(novo_telefone, senha):
        try:
            if novo_telefone and senha:  # Certificar que novo_telefone e senha não são nulos
                conn = sqlite3.connect(DB_NAME_SEC)
                cursor = conn.cursor()
                query = "UPDATE configuracoes SET telefone = ? WHERE senha = ?"
                cursor.execute(query, (novo_telefone, senha))
                if cursor.rowcount == 0:
                    raise ValueError("Senha incorreta")
                conn.commit()
                print(f"Telefone atualizado: {novo_telefone}")
            else:
                print(f"Erro ao atualizar telefone: novo_telefone = {novo_telefone}, senha = {senha}")
        except sqlite3.Error as err:
            print(f"Erro: {err}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar_senha(nova_senha, telefone):
        try:
            if nova_senha and telefone:  # Certificar que nova_senha e telefone não são nulos
                conn = sqlite3.connect(DB_NAME_SEC)
                cursor = conn.cursor()
                query = "UPDATE configuracoes SET senha = ? WHERE telefone = ?"
                cursor.execute(query, (nova_senha, telefone))
                if cursor.rowcount == 0:
                    raise ValueError("Telefone incorreto")
                conn.commit()
                print(f"Senha atualizada: {nova_senha}")
            else:
                print(f"Erro ao atualizar senha: nova_senha = {nova_senha}, telefone = {telefone}")
        except sqlite3.Error as err:
            print(f"Erro: {err}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar_twilio_config(id_to_use):
        account_sid = entry_account_sid.get()
        auth_token = entry_auth_token.get()
        from_phone = entry_from_phone.get()

        try:
            if account_sid and auth_token and from_phone:  # Certificar que account_sid, auth_token e from_phone não são nulos
                conn = sqlite3.connect(DB_NAME_SEC)
                cursor = conn.cursor()
                query = "UPDATE configuracoes SET account_sid = ?, auth_token = ?, from_phone = ? WHERE id = ?"
                cursor.execute(query, (account_sid, auth_token, from_phone, id_to_use))
                conn.commit()
                messagebox.showinfo("Configuração", "Configurações do Twilio atualizadas com sucesso!")
                janela_twilio.destroy()
                print(f"Twilio configurado: account_sid = {account_sid}, auth_token = {auth_token}, from_phone = {from_phone}")
            else:
                print(f"Erro ao configurar Twilio: account_sid = {account_sid}, auth_token = {auth_token}, from_phone = {from_phone}")
        except sqlite3.Error as err:
            print(f"Erro: {err}")
            messagebox.showerror("Erro", "Erro ao atualizar configurações do Twilio.")
        except Exception as e:
            print(f"Erro inesperado: {e}")
            messagebox.showerror("Erro", "Erro inesperado ao atualizar configurações do Twilio.")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def deletar_twilio_config(id_to_delete):
        try:
            conn = sqlite3.connect(DB_NAME_SEC)
            cursor = conn.cursor()
            delete_query = "DELETE FROM configuracoes WHERE id = ?"
            cursor.execute(delete_query, (id_to_delete,))
            conn.commit()
            ConfigurationManager.reorganizar_indices_twilio(cursor, conn)
            print(f"Registro com ID {id_to_delete} deletado e índices reorganizados.")
        except sqlite3.Error as err:
            print(f"Erro: {err}")
        finally:
            cursor.close()
            conn.close()
            MainApp.atualizar_tabela_twilio()

    @staticmethod
    def reorganizar_indices_twilio(cursor, conn):
        try:
            cursor.execute('''
            CREATE TABLE temp_configuracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telefone TEXT NOT NULL,
                senha TEXT NOT NULL,
                account_sid TEXT,
                auth_token TEXT,
                from_phone TEXT
            )
            ''')
            cursor.execute('''
            INSERT INTO temp_configuracoes (id, telefone, senha, account_sid, auth_token, from_phone)
            SELECT NULL, telefone, senha, account_sid, auth_token, from_phone FROM configuracoes ORDER BY id
            ''')
            cursor.execute('DROP TABLE configuracoes')
            cursor.execute('ALTER TABLE temp_configuracoes RENAME TO configuracoes')
            conn.commit()
        except sqlite3.Error as err:
            print(f"Erro ao reorganizar os índices: {err}")
            conn.rollback()

    @staticmethod
    def usar_twilio_config(id_to_use):
        try:
            conn = sqlite3.connect(DB_NAME_SEC)
            cursor = conn.cursor()
            query = "SELECT account_sid, auth_token, from_phone FROM configuracoes WHERE id = ?"
            cursor.execute(query, (id_to_use,))
            configuracao = cursor.fetchone()
            if configuracao:
                account_sid, auth_token, from_phone = configuracao
                entry_account_sid.delete(0, tk.END)
                entry_account_sid.insert(0, account_sid)
                entry_auth_token.delete(0, tk.END)
                entry_auth_token.insert(0, auth_token)
                entry_from_phone.delete(0, tk.END)
                entry_from_phone.insert(0, from_phone)
                print(f"Usar Twilio configuração: ID = {id_to_use}")
            else:
                messagebox.showerror("Erro", "ID não encontrado.")
                print(f"Erro ao usar Twilio configuração: ID não encontrado = {id_to_use}")
        except sqlite3.Error as err:
            print(f"Erro: {err}")
        finally:
            cursor.close()
            conn.close()

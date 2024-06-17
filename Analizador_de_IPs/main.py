import tkinter as tk
from tkinter import ttk, messagebox
import schedule
import time
import threading
from database_manager import DatabaseManager
from ip_validator import IPValidator
from network import Network
from camera import Camera
from twilio_manager import TwilioManager
from configuration_manager import ConfigurationManager

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gerenciamento de IPs")
        self.root.geometry("800x400")

        self.frame_top = tk.Frame(self.root, bg="black")
        self.frame_top.pack(pady=10)

        self.label_nome = tk.Label(self.frame_top, text="Nome:", bg="black", fg="white")
        self.label_nome.grid(row=0, column=0, padx=5)

        self.entry_nome = tk.Entry(self.frame_top, bg="black", fg="white", insertbackground="white")
        self.entry_nome.grid(row=0, column=1, padx=5)

        self.label_ip = tk.Label(self.frame_top, text="IP:", bg="black", fg="white")
        self.label_ip.grid(row=0, column=2, padx=5)

        self.entry_ip = tk.Entry(self.frame_top, bg="black", fg="white", insertbackground="white")
        self.entry_ip.grid(row=0, column=3, padx=5)

        self.camera_var = tk.IntVar()
        self.camera_check = tk.Checkbutton(self.frame_top, text="É uma câmera?", variable=self.camera_var, bg="black", fg="white", selectcolor="black")
        self.camera_check.grid(row=0, column=4, padx=5)

        self.btn_inserir_ip = tk.Button(self.frame_top, text="Inserir IP", command=self.inserir_ip, bg="black", fg="white")
        self.btn_inserir_ip.grid(row=0, column=5, padx=5)

        self.frame_table = tk.Frame(self.root, bg="black")
        self.frame_table.pack(pady=10)

        columns = ("ID", "Nome", "IP", "Status", "Camera")
        self.tree = ttk.Treeview(self.frame_table, columns=columns, show="headings", style="Custom.Treeview")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(expand=True, fill="both")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Custom.Treeview", background="black", fieldbackground="black", foreground="white")
        self.style.configure("Custom.Treeview.Heading", background="black", foreground="white")

        self.frame_bottom = tk.Frame(self.root, bg="black")
        self.frame_bottom.pack(pady=10)

        self.label_id = tk.Label(self.frame_bottom, text="ID para Deletar:", bg="black", fg="white")
        self.label_id.grid(row=0, column=0, padx=5)

        self.entry_id = tk.Entry(self.frame_bottom, bg="black", fg="white", insertbackground="white")
        self.entry_id.grid(row=0, column=1, padx=5)

        self.btn_deletar_ip = tk.Button(self.frame_bottom, text="Deletar IP", command=self.deletar_ip, bg="black", fg="white")
        self.btn_deletar_ip.grid(row=0, column=2, padx=5)

        self.btn_verificacoes = tk.Menubutton(self.frame_bottom, text="Verificações", relief="raised", bg="black", fg="white")
        verificacoes_menu = tk.Menu(self.btn_verificacoes, tearoff=0)
        verificacoes_menu.add_command(label="Ping Todos os IPs", command=self.pingar_todos_os_ips)
        verificacoes_menu.add_command(label="Verificar Câmeras", command=self.verificar_cameras_button)
        self.btn_verificacoes.config(menu=verificacoes_menu)
        self.btn_verificacoes.grid(row=0, column=3, padx=5)

        self.btn_configurar_tempo = tk.Button(self.frame_bottom, text="Configurar Tempo", command=self.abrir_interface_tempo, bg="black", fg="white")
        self.btn_configurar_tempo.grid(row=0, column=4, padx=5)

        self.btn_fechar = tk.Button(self.frame_bottom, text="Fechar", command=self.fechar_programa, bg="black", fg="white")
        self.btn_fechar.grid(row=0, column=5, padx=5)

        self.criar_botoes_troca_tema()
        self.criar_botoes_contato()

        self.configuracao_inicial()
        thread_ping = threading.Thread(target=self.pingar_ips_em_segundo_plano)
        thread_ping.daemon = True
        thread_ping.start()

        self.mudar_tema_escuro()
        self.atualizar_tabela()
        self.root.mainloop()

    def inserir_ip(self):
        nome_informado = self.entry_nome.get()
        ip_informado = self.entry_ip.get()
        is_camera = self.camera_var.get()
        if nome_informado and ip_informado:
            resultado = IPValidator.teste_de_IPs(ip_informado)
            messagebox.showinfo("Validação de IP", resultado)
            if "IP válido." in resultado:
                DatabaseManager.inserir_no_sqlite(nome_informado, ip_informado, is_camera)
                self.atualizar_tabela()
            else:
                messagebox.showwarning("IP Inválido", f"O IP {ip_informado} não é válido e não foi inserido no banco de dados.")
        else:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos.")

    def deletar_ip(self):
        try:
            id_to_delete = int(self.entry_id.get())
            if id_to_delete:
                DatabaseManager.deletar_ip(id_to_delete)
                self.atualizar_tabela()
                messagebox.showinfo("IP Deletado", f"O IP com ID {id_to_delete} foi deletado.")
        except ValueError:
            messagebox.showerror("Erro", "ID inválido. Por favor, insira um número.")

    def pingar_todos_os_ips(self):
        Network.pingar_ips()
        self.atualizar_tabela()
        messagebox.showinfo("Ping IPs", "Ping realizado em todos os IPs cadastrados.")

    def verificar_cameras_button(self):
        Camera.verificar_cameras()

    def fechar_programa(self):
        self.root.destroy()

    def configuracao_inicial(self):
        DatabaseManager.criar_tabela()
        ConfigurationManager.criar_tabela_configuracoes()
        schedule.every(5).minutes.do(Network.pingar_ips)
        schedule.every(10).minutes.do(Camera.verificar_cameras)
        schedule.every(10).minutes.do(TwilioManager.verificar_erros_e_enviar_sms)

    def pingar_ips_em_segundo_plano(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def atualizar_tabela(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        ips = DatabaseManager.obter_ips()
        for id, nome, ip, status, camera in ips:
            self.tree.insert("", "end", values=(id, nome, ip, status, camera))

    def mudar_tema_claro(self):
        self.root.configure(bg="white")
        self.frame_top.configure(bg="white")
        self.frame_table.configure(bg="white")
        self.frame_bottom.configure(bg="white")
        for widget in self.frame_top.winfo_children():
            widget.configure(bg="white", fg="black")
        for widget in self.frame_bottom.winfo_children():
            widget.configure(bg="white", fg="black")
        self.camera_check.configure(bg="white", fg="black", selectcolor="white")
        self.entry_nome.configure(bg="white", fg="black", insertbackground="black")
        self.entry_ip.configure(bg="white", fg="black", insertbackground="black")
        self.entry_id.configure(bg="white", fg="black", insertbackground="black")
        self.style.configure("Custom.Treeview", background="white", fieldbackground="white", foreground="black")
        self.style.configure("Custom.Treeview.Heading", background="white", foreground="black")
        # Atualizar tema da interface Twilio se estiver aberta
        if 'frame_twilio_top' in globals():
            self.frame_twilio_top.configure(bg="white")
            self.frame_twilio_bottom.configure(bg="white")
            for widget in self.frame_twilio_top.winfo_children():
                widget.configure(bg="white", fg="black")
            for widget in self.frame_twilio_bottom.winfo_children():
                widget.configure(bg="white", fg="black")

    def mudar_tema_escuro(self):
        self.root.configure(bg="black")
        self.frame_top.configure(bg="black")
        self.frame_table.configure(bg="black")
        self.frame_bottom.configure(bg="black")
        for widget in self.frame_top.winfo_children():
            widget.configure(bg="black", fg="white")
        for widget in self.frame_bottom.winfo_children():
            widget.configure(bg="black", fg="white")
        self.camera_check.configure(bg="black", fg="white", selectcolor="black")
        self.entry_nome.configure(bg="black", fg="white", insertbackground="white")
        self.entry_ip.configure(bg="black", fg="white", insertbackground="white")
        self.entry_id.configure(bg="black", fg="white", insertbackground="white")
        self.style.configure("Custom.Treeview", background="black", fieldbackground="black", foreground="white")
        self.style.configure("Custom.Treeview.Heading", background="black", foreground="white")
        # Atualizar tema da interface Twilio se estiver aberta
        if 'frame_twilio_top' in globals():
            self.frame_twilio_top.configure(bg="black")
            self.frame_twilio_bottom.configure(bg="black")
            for widget in self.frame_twilio_top.winfo_children():
                widget.configure(bg="black", fg="white")
            for widget in self.frame_twilio_bottom.winfo_children():
                widget.configure(bg="black", fg="white")

    def criar_botoes_troca_tema(self):
        btn_tema = tk.Menubutton(self.frame_bottom, text="Tema", relief="raised", bg="black", fg="white")
        tema_menu = tk.Menu(btn_tema, tearoff=0)
        tema_menu.add_command(label="Claro", command=self.mudar_tema_claro)
        tema_menu.add_command(label="Escuro", command=self.mudar_tema_escuro)
        btn_tema.config(menu=tema_menu)
        btn_tema.grid(row=0, column=6, padx=5)

    def criar_botoes_contato(self):
        btn_contato = tk.Menubutton(self.frame_bottom, text="Contato", relief="raised", bg="black", fg="white")
        contato_menu = tk.Menu(btn_contato, tearoff=0)
        contato_menu.add_command(label="Configurar Telefone", command=self.abrir_interface_contato)
        contato_menu.add_command(label="Configurar Twilio", command=self.abrir_interface_twilio)
        btn_contato.config(menu=contato_menu)
        btn_contato.grid(row=0, column=7, padx=5)

    def abrir_interface_tempo(self):
        def salvar_tempo():
            try:
                intervalo_ping = int(entry_ping.get())
                intervalo_camera = int(entry_camera.get())
                schedule.clear()
                schedule.every(intervalo_ping).minutes.do(Network.pingar_ips)
                schedule.every(intervalo_camera).minutes.do(Camera.verificar_cameras)
                janela_tempo.destroy()
                messagebox.showinfo("Configuração de Tempo", "Intervalos de tempo atualizados com sucesso!")
            except ValueError:
                messagebox.showerror("Erro", "Por favor, insira valores válidos para os intervalos de tempo.")

        janela_tempo = tk.Toplevel(self.root)
        janela_tempo.title("Configuração de Tempo")

        label_ping = tk.Label(janela_tempo, text="Intervalo de Ping (minutos):")
        label_ping.pack(pady=5)
        entry_ping = tk.Entry(janela_tempo)
        entry_ping.pack(pady=5)

        label_camera = tk.Label(janela_tempo, text="Intervalo de Verificação de Câmera (minutos):")
        label_camera.pack(pady=5)
        entry_camera = tk.Entry(janela_tempo)
        entry_camera.pack(pady=5)

        btn_salvar_tempo = tk.Button(janela_tempo, text="Salvar", command=salvar_tempo, bg="black", fg="white")
        btn_salvar_tempo.pack(pady=10)

    def abrir_interface_contato(self):
        telefone, senha = ConfigurationManager.obter_configuracao()
        if (telefone, senha) != (None, None):
            self.abrir_interface_modificar_telefone()
        else:
            def salvar_configuracao():
                telefone = entry_telefone.get()
                senha = entry_senha.get()
                if telefone and senha:
                    ConfigurationManager.inserir_configuracao(telefone, senha)
                    messagebox.showinfo("Configuração", "Número de telefone e senha salvos com sucesso!")
                    janela_contato.destroy()
                    self.abrir_interface_modificar_telefone()
                else:
                    messagebox.showwarning("Atenção", "Por favor, preencha todos os campos.")
                    print(f"Erro ao salvar configuração: telefone = {telefone}, senha = {senha}")

            janela_contato = tk.Toplevel(self.root)
            janela_contato.title("Configuração de Contato")
            janela_contato.geometry("300x180")  # Interface mais quadrática

            label_telefone = tk.Label(janela_contato, text="Número de Telefone:")
            label_telefone.pack(pady=5)
            entry_telefone = tk.Entry(janela_contato)
            entry_telefone.pack(pady=5)

            label_senha = tk.Label(janela_contato, text="Senha:")
            label_senha.pack(pady=5)
            entry_senha = tk.Entry(janela_contato, show="*")
            entry_senha.pack(pady=5)

            btn_salvar_telefone = tk.Button(janela_contato, text="Salvar", command=salvar_configuracao)
            btn_salvar_telefone.pack(pady=10)

    def abrir_interface_modificar_telefone(self):
        global janela_modificar
        janela_modificar = tk.Toplevel(self.root)
        janela_modificar.title("Modificar Telefone")
        janela_modificar.geometry("300x180")  # Interface mais quadrática

        label_novo_telefone = tk.Label(janela_modificar, text="Novo Número de Telefone:")
        label_novo_telefone.pack(pady=5)
        global entry_novo_telefone
        entry_novo_telefone = tk.Entry(janela_modificar)
        entry_novo_telefone.pack(pady=5)

        label_senha = tk.Label(janela_modificar, text="Senha:")
        label_senha.pack(pady=5)
        global entry_senha_modificar
        entry_senha_modificar = tk.Entry(janela_modificar, show="*")
        entry_senha_modificar.pack(pady=5)

        btn_atualizar_telefone = tk.Button(janela_modificar, text="Atualizar Telefone", command=self.atualizar_telefone_interface)
        btn_atualizar_telefone.pack(pady=10)

    def atualizar_telefone_interface(self):
        novo_telefone = entry_novo_telefone.get()
        senha = entry_senha_modificar.get()
        if novo_telefone and senha:
            try:
                ConfigurationManager.atualizar_telefone(novo_telefone, senha)
                messagebox.showinfo("Configuração", "Número de telefone atualizado com sucesso!")
                janela_modificar.destroy()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))
        else:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos.")
            print(f"Erro ao atualizar telefone: novo_telefone = {novo_telefone}, senha = {senha}")

    def abrir_interface_twilio(self):
        global janela_twilio
        global frame_twilio_top
        global frame_twilio_bottom

        janela_twilio = tk.Toplevel(self.root)
        janela_twilio.title("Configuração Twilio")
        janela_twilio.geometry("840x400")  # Interface maior para incluir a tabela
        janela_twilio.configure(bg="white")

        frame_twilio_top = tk.Frame(janela_twilio, bg="white")
        frame_twilio_top.pack(pady=10)

        label_account_sid = tk.Label(frame_twilio_top, text="Account SID:", bg="white", fg="black")
        label_account_sid.grid(row=0, column=0, padx=5)
        global entry_account_sid
        entry_account_sid = tk.Entry(frame_twilio_top, bg="white", fg="black", insertbackground="black")
        entry_account_sid.grid(row=0, column=1, padx=5)

        label_auth_token = tk.Label(frame_twilio_top, text="Auth Token:", bg="white", fg="black")
        label_auth_token.grid(row=0, column=2, padx=5)
        global entry_auth_token
        entry_auth_token = tk.Entry(frame_twilio_top, bg="white", fg="black", insertbackground="black")
        entry_auth_token.grid(row=0, column=3, padx=5)

        label_from_phone = tk.Label(frame_twilio_top, text="From Phone:", bg="white", fg="black")
        label_from_phone.grid(row=0, column=4, padx=5)
        global entry_from_phone
        entry_from_phone = tk.Entry(frame_twilio_top, bg="white", fg="black", insertbackground="black")
        entry_from_phone.grid(row=0, column=5, padx=5)

        label_id_twilio = tk.Label(frame_twilio_top, text="ID para usar:", bg="white", fg="black")
        label_id_twilio.grid(row=0, column=6, padx=5)
        global entry_id_twilio
        entry_id_twilio = tk.Entry(frame_twilio_top, bg="white", fg="black", insertbackground="black")
        entry_id_twilio.grid(row=0, column=7, padx=5)

        btn_usar_twilio = tk.Button(frame_twilio_top, text="Usar Twilio", command=lambda: ConfigurationManager.usar_twilio_config(entry_id_twilio.get()), bg="white", fg="black")
        btn_usar_twilio.grid(row=0, column=8, padx=5)

        btn_adicionar_twilio = tk.Button(frame_twilio_top, text="Adicionar Twilio", command=self.adicionar_twilio_config, bg="white", fg="black")
        btn_adicionar_twilio.grid(row=0, column=9, padx=5)

        # Tabela para exibir configurações Twilio
        columns_twilio = ("ID", "Account SID", "Auth Token", "From Phone")
        global tree_twilio
        tree_twilio = ttk.Treeview(janela_twilio, columns=columns_twilio, show="headings")
        for col in columns_twilio:
            tree_twilio.heading(col, text=col)
            tree_twilio.column(col, width=150, anchor="center")
        tree_twilio.pack(expand=True, fill="both")

        frame_twilio_bottom = tk.Frame(janela_twilio, bg="white")
        frame_twilio_bottom.pack(pady=10)

        label_delete_id_twilio = tk.Label(frame_twilio_bottom, text="ID para deletar:", bg="white", fg="black")
        label_delete_id_twilio.grid(row=0, column=0, padx=5)
        global entry_delete_id_twilio
        entry_delete_id_twilio = tk.Entry(frame_twilio_bottom, bg="white", fg="black", insertbackground="black")
        entry_delete_id_twilio.grid(row=0, column=1, padx=5)

        btn_deletar_twilio = tk.Button(frame_twilio_bottom, text="Deletar Twilio Config", command=lambda: ConfigurationManager.deletar_twilio_config(entry_delete_id_twilio.get()), bg="white", fg="black")
        btn_deletar_twilio.grid(row=0, column=2, padx=5)

        self.atualizar_tabela_twilio()

    def adicionar_twilio_config(self):
        account_sid = entry_account_sid.get()
        auth_token = entry_auth_token.get()
        from_phone = entry_from_phone.get()

        try:
            if account_sid and auth_token and from_phone:  # Certificar que account_sid, auth_token e from_phone não são nulos
                conn = sqlite3.connect(DB_NAME_SEC)
                cursor = conn.cursor()
                query = "INSERT INTO configuracoes (account_sid, auth_token, from_phone) VALUES (?, ?, ?)"
                cursor.execute(query, (account_sid, auth_token, from_phone))
                conn.commit()
                messagebox.showinfo("Configuração", "Configurações do Twilio adicionadas com sucesso!")
                self.atualizar_tabela_twilio()
            else:
                print(f"Erro ao adicionar Twilio config: account_sid = {account_sid}, auth_token = {auth_token}, from_phone = {from_phone}")
        except sqlite3.Error as err:
            print(f"Erro: {err}")
            messagebox.showerror("Erro", "Erro ao adicionar configurações do Twilio.")
        except Exception as e:
            print(f"Erro inesperado: {e}")
            messagebox.showerror("Erro", "Erro inesperado ao adicionar configurações do Twilio.")
        finally:
            cursor.close()
            conn.close()

    def atualizar_tabela_twilio(self):
        for row in tree_twilio.get_children():
            tree_twilio.delete(row)
        configuracoes = ConfigurationManager.obter_twilio_configuracao()
        for id, account_sid, auth_token, from_phone in configuracoes:
            tree_twilio.insert("", "end", values=(id, account_sid, auth_token, from_phone))

if __name__ == "__main__":
    app = MainApp()

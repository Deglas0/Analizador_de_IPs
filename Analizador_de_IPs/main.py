import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import threading
from sms import send_sms_twilio, verificar_erros_e_enviar_sms, TWILIO_NUMBER, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from validation import pingar_ips, teste_de_IPs, verificar_camera
from database import inserir_telefone,obter_telefones, obter_ips, deletar_ip, criar_tabela_telefone, criar_tabela_dispositivos, inserir_no_sqlite, deletar_telefone, obter_telefone_por_id,  DB_DISPOSITIVOS
import time
import sqlite3
import schedule

def atualizar_tabela_telefones():
    for row in tree_telefones.get_children():
        tree_telefones.delete(row)
    telefones = obter_telefones()
    for id, numero in telefones:
        tree_telefones.insert("", "end", values=(id, numero))

PING_INTERVAL = 5
CAMERA_CHECK_INTERVAL = 10
ERROR_SMS_INTERVAL = 10

def atualizar_tabela():
    for row in tree.get_children():
        tree.delete(row)
    ips = obter_ips()
    for id, nome, ip, status, camera in ips:
        tree.insert("", "end", values=(id, nome, ip, status, camera))

def inserir_ip():
    nome_informado = entry_nome.get()
    ip_informado = entry_ip.get()
    is_camera = camera_var.get()
    if nome_informado and ip_informado:
        resultado = teste_de_IPs(ip_informado)
        messagebox.showinfo("Validação de IP", resultado)
        if "IP válido." in resultado:
            inserir_no_sqlite(nome_informado, ip_informado, is_camera)
            atualizar_tabela()
        else:
            messagebox.showwarning("IP Inválido", f"O IP {ip_informado} não é válido e não foi inserido no banco de dados.")

def verificar_cameras():
    try:
        with sqlite3.connect(DB_DISPOSITIVOS) as conn:
            cursor = conn.cursor()
            query = "SELECT id, ip, camera FROM dispositivos ORDER BY id"
            cursor.execute(query)
            dispositivos = cursor.fetchall()

            threads = []
            for id, ip, camera in dispositivos:
                thread = threading.Thread(target=verificar_camera, args=(ip, id, camera))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            atualizar_tabela()
            messagebox.showinfo("Verificar Câmeras", "Verificação das câmeras concluída.")
    except sqlite3.Error as err:
        print(f"Erro: {err}")


def deletar_ip_button():
    try:
        id_to_delete = int(entry_id.get())
        if id_to_delete:
            deletar_ip(id_to_delete)
            atualizar_tabela()
            messagebox.showinfo("IP Deletado", f"O IP com ID {id_to_delete} foi deletado.")
    except ValueError:
        messagebox.showerror("Erro", "ID inválido. Por favor, insira um número.")


def pingar_todos_os_ips():
    pingar_ips()
    atualizar_tabela()
    messagebox.showinfo("Ping IPs", "Ping realizado em todos os IPs cadastrados.")


def verificar_cameras_button():
    verificar_cameras()

def configuracao_inicial():
    criar_tabela_dispositivos()
    criar_tabela_telefone()
    schedule.every(PING_INTERVAL).minutes.do(pingar_ips)
    schedule.every(CAMERA_CHECK_INTERVAL).minutes.do(verificar_cameras)
    schedule.every(ERROR_SMS_INTERVAL).minutes.do(verificar_erros_e_enviar_sms)


def pingar_ips_em_segundo_plano():
    while True:
        schedule.run_pending()
        time.sleep(1)

def fechar_programa():
    root.destroy()
def abrir_twilio_website():
    webbrowser.open("https://www.twilio.com/lookup")


def mudar_tema_claro():
    global tema
    tema = "claro"
    main_bg_color = "#f0f0f0"
    text_color = "black"

    root.configure(bg=main_bg_color)
    frame_top.configure(bg=main_bg_color)
    frame_table.configure(bg=main_bg_color)
    frame_bottom.configure(bg=main_bg_color)

    for widget in frame_top.winfo_children():
        widget.configure(bg=main_bg_color, fg=text_color)
    for widget in frame_bottom.winfo_children():
        widget.configure(bg=main_bg_color, fg=text_color)
    camera_check.configure(bg=main_bg_color, fg=text_color, selectcolor=main_bg_color)
    entry_nome.configure(bg=main_bg_color, fg=text_color, insertbackground=text_color)
    entry_ip.configure(bg=main_bg_color, fg=text_color, insertbackground=text_color)
    entry_id.configure(bg=main_bg_color, fg=text_color, insertbackground=text_color)

    style_ip_table.configure("Custom.Treeview", background="white", fieldbackground="white", foreground="black")
    style_ip_table.configure("Custom.Treeview.Heading", background="white", foreground="black")

def abrir_interface_tempo():
    def salvar_tempo():
        global PING_INTERVAL, CAMERA_CHECK_INTERVAL, ERROR_SMS_INTERVAL
        try:
            PING_INTERVAL = int(entry_ping.get())
            CAMERA_CHECK_INTERVAL = int(entry_camera.get())
            ERROR_SMS_INTERVAL = int(entry_sms.get())
            schedule.clear()
            schedule.every(PING_INTERVAL).minutes.do(pingar_ips)
            schedule.every(CAMERA_CHECK_INTERVAL).minutes.do(verificar_cameras)
            schedule.every(ERROR_SMS_INTERVAL).minutes.do(verificar_erros_e_enviar_sms)
            messagebox.showinfo("Configuração de Tempo", "Configurações de tempo atualizadas com sucesso!")
            janela_tempo.destroy()
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores válidos para os tempos.")

    janela_tempo = tk.Toplevel(root)
    janela_tempo.title("Configuração de Tempo")
    janela_tempo.geometry("300x200")
    janela_tempo.configure(bg="white")

    label_ping = tk.Label(janela_tempo, text="Ping (minutos):", bg="white", fg="black")
    label_ping.pack(pady=5)
    entry_ping = tk.Entry(janela_tempo, bg="white", fg="black", insertbackground="black")
    entry_ping.pack(pady=5)
    entry_ping.insert(0, str(PING_INTERVAL))

    label_camera = tk.Label(janela_tempo, text="Verificar Câmeras (minutos):", bg="white", fg="black")
    label_camera.pack(pady=5)
    entry_camera = tk.Entry(janela_tempo, bg="white", fg="black", insertbackground="black")
    entry_camera.pack(pady=5)
    entry_camera.insert(0, str(CAMERA_CHECK_INTERVAL))

    label_sms = tk.Label(janela_tempo, text="Verificar Erros e Enviar SMS (minutos):", bg="white", fg="black")
    label_sms.pack(pady=5)
    entry_sms = tk.Entry(janela_tempo, bg="white", fg="black", insertbackground="black")
    entry_sms.pack(pady=5)
    entry_sms.insert(0, str(ERROR_SMS_INTERVAL))

    btn_salvar = tk.Button(janela_tempo, text="Salvar", command=salvar_tempo, bg="white", fg="black")
    btn_salvar.pack(pady=10)


def mudar_tema_escuro():
    global tema
    tema = "escuro"
    main_bg_color = "black"
    text_color = "white"

    root.configure(bg=main_bg_color)
    frame_top.configure(bg=main_bg_color)
    frame_table.configure(bg=main_bg_color)
    frame_bottom.configure(bg=main_bg_color)

    for widget in frame_top.winfo_children():
        widget.configure(bg=main_bg_color, fg=text_color)
    for widget in frame_bottom.winfo_children():
        widget.configure(bg=main_bg_color, fg=text_color)
    camera_check.configure(bg=main_bg_color, fg=text_color, selectcolor=main_bg_color)
    entry_nome.configure(bg=main_bg_color, fg=text_color, insertbackground=text_color)
    entry_ip.configure(bg=main_bg_color, fg=text_color, insertbackground=text_color)
    entry_id.configure(bg=main_bg_color, fg=text_color, insertbackground=text_color)

    style_ip_table.configure("Custom.Treeview", background="black", fieldbackground="black", foreground="white")
    style_ip_table.configure("Custom.Treeview.Heading", background="black", foreground="white")

def criar_botoes_troca_tema():
    btn_tema = tk.Menubutton(frame_bottom, text="Tema", relief="raised", bg="white", fg="black")
    tema_menu = tk.Menu(btn_tema, tearoff=0)
    tema_menu.add_command(label="Claro", command=mudar_tema_claro)
    tema_menu.add_command(label="Escuro", command=mudar_tema_escuro)
    btn_tema.config(menu=tema_menu)
    btn_tema.grid(row=0, column=6, padx=5)


def abrir_interface_telefones():
    def inserir_telefone_button():
        numero = entry_numero.get()
        senha = entry_senha.get()
        if numero and senha:
            inserir_telefone(numero, senha)
            atualizar_tabela_telefones()

    def deletar_telefone_button():
        try:
            id_to_delete = int(entry_id_telefone.get())
            senha = entry_senha_delete.get()
            deletar_telefone(id_to_delete, senha)
            atualizar_tabela_telefones()
        except ValueError:
            messagebox.showerror("Erro", "ID inválido. Por favor, insira um número.")

    def usar_telefone_button():
        try:
            id_to_use = int(entry_id_telefone_uso.get())
            senha = entry_senha_uso.get()
            numero = obter_telefone_por_id(id_to_use, senha)
            if numero:
                send_sms_twilio(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER, numero, "Mensagem de teste.")
                messagebox.showinfo("Sucesso", f"Mensagem enviada com sucesso para {numero}.")
                label_numero_em_uso.config(text=f"Número em uso: {numero}")
            else:
                messagebox.showerror("Erro", "Número de telefone ou senha incorreta.")
        except ValueError:
            messagebox.showerror("Erro", "ID inválido. Por favor, insira um número.")

    janela_telefones = tk.Toplevel(root)
    janela_telefones.title("Gerenciamento de Telefones")
    janela_telefones.geometry("600x400")
    janela_telefones.configure(bg="white")

    frame_telefones_top = tk.Frame(janela_telefones, bg="white")
    frame_telefones_top.pack(pady=10)

    label_numero = tk.Label(frame_telefones_top, text="Número:", bg="white", fg="black")
    label_numero.grid(row=0, column=0, padx=5)
    entry_numero = tk.Entry(frame_telefones_top, bg="white", fg="black", insertbackground="black")
    entry_numero.grid(row=0, column=1, padx=5)

    label_senha = tk.Label(frame_telefones_top, text="Senha:", bg="white", fg="black")
    label_senha.grid(row=0, column=2, padx=5)
    entry_senha = tk.Entry(frame_telefones_top, bg="white", fg="black", insertbackground="black", show="*")
    entry_senha.grid(row=0, column=3, padx=5)

    btn_inserir_telefone = tk.Button(frame_telefones_top, text="Inserir Telefone", command=inserir_telefone_button,
                                     bg="white", fg="black")
    btn_inserir_telefone.grid(row=0, column=4, padx=5)

    frame_telefones_table = tk.Frame(janela_telefones, bg="white")
    frame_telefones_table.pack(pady=10)

    columns_telefones = ("ID", "Número")
    global tree_telefones
    tree_telefones = ttk.Treeview(frame_telefones_table, columns=columns_telefones, show="headings",
                                  style="CustomPhone.Treeview")
    for col in columns_telefones:
        tree_telefones.heading(col, text=col)
        tree_telefones.column(col, width=150, anchor="center")
    tree_telefones.pack(expand=True, fill="both")

    style_phone_table = ttk.Style()
    style_phone_table.theme_use("clam")
    style_phone_table.configure("CustomPhone.Treeview", background="white", fieldbackground="white", foreground="black")
    style_phone_table.configure("CustomPhone.Treeview.Heading", background="white", foreground="black")

    frame_telefones_bottom = tk.Frame(janela_telefones, bg="white")
    frame_telefones_bottom.pack(pady=10)

    label_id_telefone = tk.Label(frame_telefones_bottom, text="ID para Deletar:", bg="white", fg="black")
    label_id_telefone.grid(row=0, column=0, padx=5)
    entry_id_telefone = tk.Entry(frame_telefones_bottom, bg="white", fg="black", insertbackground="black")
    entry_id_telefone.grid(row=0, column=1, padx=5)

    label_senha_delete = tk.Label(frame_telefones_bottom, text="Senha:", bg="white", fg="black")
    label_senha_delete.grid(row=0, column=2, padx=5)
    entry_senha_delete = tk.Entry(frame_telefones_bottom, bg="white", fg="black", insertbackground="black", show="*")
    entry_senha_delete.grid(row=0, column=3, padx=5)

    btn_deletar_telefone = tk.Button(frame_telefones_bottom, text="Deletar Telefone", command=deletar_telefone_button,
                                     bg="white", fg="black")
    btn_deletar_telefone.grid(row=0, column=4, padx=5)

    label_id_telefone_uso = tk.Label(frame_telefones_bottom, text="ID para Usar:", bg="white", fg="black")
    label_id_telefone_uso.grid(row=1, column=0, padx=5)
    entry_id_telefone_uso = tk.Entry(frame_telefones_bottom, bg="white", fg="black", insertbackground="black")
    entry_id_telefone_uso.grid(row=1, column=1, padx=5)

    label_senha_uso = tk.Label(frame_telefones_bottom, text="Senha:", bg="white", fg="black")
    label_senha_uso.grid(row=1, column=2, padx=5)
    entry_senha_uso = tk.Entry(frame_telefones_bottom, bg="white", fg="black", insertbackground="black", show="*")
    entry_senha_uso.grid(row=1, column=3, padx=5)

    btn_usar_telefone = tk.Button(frame_telefones_bottom, text="Usar Telefone", command=usar_telefone_button,
                                  bg="white", fg="black")
    btn_usar_telefone.grid(row=1, column=4, padx=5)

    label_numero_em_uso = tk.Label(frame_telefones_bottom, text="Número em uso: Nenhum", bg="white", fg="black")
    label_numero_em_uso.grid(row=2, columnspan=5, pady=10)

    link_twilio = tk.Label(frame_telefones_bottom, text="Verificar número no Twilio", bg="white", fg="blue", cursor="hand2")
    link_twilio.grid(row=3, columnspan=5, pady=10)
    link_twilio.bind("<Button-1>", lambda e: abrir_twilio_website())

    atualizar_tabela_telefones()
    janelas_secundarias.append(janela_telefones)


# Interface Principal
root = tk.Tk()
root.title("Gerenciamento de IPs")
root.geometry("800x400")
janelas_secundarias = []
tema = "claro"

frame_top = tk.Frame(root, bg="white")
frame_top.pack(pady=10)

label_nome = tk.Label(frame_top, text="Nome:", bg="white", fg="black")
label_nome.grid(row=0, column=0, padx=5)

entry_nome = tk.Entry(frame_top, bg="white", fg="black", insertbackground="black")
entry_nome.grid(row=0, column=1, padx=5)

label_ip = tk.Label(frame_top, text="IP:", bg="white", fg="black")
label_ip.grid(row=0, column=2, padx=5)

entry_ip = tk.Entry(frame_top, bg="white", fg="black", insertbackground="black")
entry_ip.grid(row=0, column=3, padx=5)

camera_var = tk.IntVar()
camera_check = tk.Checkbutton(frame_top, text="É uma câmera?", variable=camera_var, bg="white", fg="black",
                              selectcolor="white")
camera_check.grid(row=0, column=4, padx=5)

btn_inserir_ip = tk.Button(frame_top, text="Inserir IP", command=inserir_ip, bg="white", fg="black")
btn_inserir_ip.grid(row=0, column=5, padx=5)

frame_table = tk.Frame(root, bg="white")
frame_table.pack(pady=10)

columns = ("ID", "Nome", "IP", "Status", "Camera")
tree = ttk.Treeview(frame_table, columns=columns, show="headings", style="Custom.Treeview")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150, anchor="center")
tree.pack(expand=True, fill="both")

style = ttk.Style()
style.theme_use("clam")
style.configure("Custom.Treeview", background="white", fieldbackground="white", foreground="black")
style.configure("Custom.Treeview.Heading", background="white", foreground="black")

style_ip_table = ttk.Style()
style_ip_table.theme_use("clam")
style_ip_table.configure("Custom.Treeview", background="white", fieldbackground="white", foreground="black")
style_ip_table.configure("Custom.Treeview.Heading", background="white", foreground="black")

frame_bottom = tk.Frame(root, bg="white")
frame_bottom.pack(pady=10)

label_id = tk.Label(frame_bottom, text="ID para Deletar:", bg="white", fg="black")
label_id.grid(row=0, column=0, padx=5)
entry_id = tk.Entry(frame_bottom, bg="white", fg="black", insertbackground="black")
entry_id.grid(row=0, column=1, padx=5)
btn_deletar_ip = tk.Button(frame_bottom, text="Deletar IP", command=deletar_ip_button, bg="white", fg="black")
btn_deletar_ip.grid(row=0, column=2, padx=5)

btn_verificacoes = tk.Menubutton(frame_bottom, text="Verificações", relief="raised", bg="white", fg="black")
verificacoes_menu = tk.Menu(btn_verificacoes, tearoff=0)
verificacoes_menu.add_command(label="Ping Todos os IPs", command=pingar_todos_os_ips)
verificacoes_menu.add_command(label="Verificar Câmeras", command=verificar_cameras_button)
btn_verificacoes.config(menu=verificacoes_menu)
btn_verificacoes.grid(row=0, column=3, padx=5)

btn_configurar_tempo = tk.Button(frame_bottom, text="Configurar Tempo", command=abrir_interface_tempo, bg="white",
                                 fg="black")
btn_configurar_tempo.grid(row=0, column=4, padx=5)

btn_gerenciamento = tk.Menubutton(frame_bottom, text="Gerenciamento", relief="raised", bg="white", fg="black")
gerenciamento_menu = tk.Menu(btn_gerenciamento, tearoff=0)
gerenciamento_menu.add_command(label="Gerenciar Telefones", command=abrir_interface_telefones)
btn_gerenciamento.config(menu=gerenciamento_menu)
btn_gerenciamento.grid(row=0, column=5, padx=5)

btn_fechar = tk.Button(frame_bottom, text="Fechar", command=fechar_programa, bg="white", fg="black")
btn_fechar.grid(row=0, column=7, padx=5)

criar_botoes_troca_tema()

configuracao_inicial()
thread_ping = threading.Thread(target=pingar_ips_em_segundo_plano)
thread_ping.daemon = True
thread_ping.start()

mudar_tema_claro()
atualizar_tabela()
root.mainloop()
import sqlite3

# Conectar ao banco de dados ou criar se não existir
conn = sqlite3.connect('analizador_de_IPs.db')

# Criar um cursor para executar comandos SQL
cursor = conn.cursor()

# Criar a tabela "dispositivos"
cursor.execute('''
    CREATE TABLE IF NOT EXISTS dispositivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        nome TEXT
    )
''')

# Commit para salvar as alterações
conn.commit()

# Fechar a conexão
conn.close()

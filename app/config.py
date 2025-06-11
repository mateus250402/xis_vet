import mysql.connector
from mysql.connector import Error

class Config:
    DEBUG = True
    DATABASE_CONFIG = {
        'host': 'localhost',
        'port': '3306',
        'user': 'root',
        'password': '021086Aa!',
        'database': 'vendas'
    }

def criar_conexao():
    try:
        conexao = mysql.connector.connect(**Config.DATABASE_CONFIG) # Conexão com o banco de dados
        # Verifica se a conexão foi bem-sucedida
        if conexao.is_connected():
            print("Conexão com o banco de dados estabelecida com sucesso.")
            return conexao
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None
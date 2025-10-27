"""
Banco de Conexão - SQLAlchemy

Este módulo configura e fornece um engine SQLAlchemy para conectar a um banco de dados PostgreSQL.
As credenciais e parâmetros de conexão são lidos de variáveis de ambiente, carregadas a partir de um arquivo .env.
"""

import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


def obter_engine():
    """
    Cria e retorna um engine SQLAlchemy configurado para o banco de dados PostgreSQL.

    Variáveis de ambiente utilizadas:
        DB_USER: Usuário do banco de dados
        DB_PASSWORD: Senha do banco de dados
        DB_HOST: Host do banco de dados
        DB_PORT: Porta do banco de dados
        DB_NAME: Nome do banco de dados

    O parâmetro DB_PASSWORD é codificado para lidar com caracteres especiais.

    Retorna:
        sqlalchemy.engine.base.Engine: Engine SQLAlchemy para conexão com o banco

    Levanta:
        EnvironmentError: Caso alguma variável de ambiente obrigatória esteja ausente.
    """
    # Carrega variáveis de ambiente
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))  # Codifica caracteres especiais
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    # Verifica se todas as variáveis estão presentes
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        raise EnvironmentError(
            "❌ Variáveis de ambiente do banco estão incompletas. Verifique o arquivo .env"
        )

    # Constrói a URL de conexão
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

    # Cria e retorna o engine SQLAlchemy
    engine = create_engine(DATABASE_URL)
    return engine

"""
Módulo de Qualidade e Inserção de Dados

Este módulo oferece funcionalidades para:
- Analisar a qualidade de datasets (missing values, duplicados, resumo numérico/categórico)
- Converter tipos de colunas
- Remover duplicados
- Inserir dados em um banco de dados PostgreSQL via SQLAlchemy
- Conectar-se ao banco e inserir dados de forma controlada

As funções foram desenhadas para trabalhar com Pandas DataFrames.
"""

import io
import pandas as pd
from banco_conexao import obter_engine


# ------------------ Funções de Apoio ------------------ #


def desenhar_linha(titulo=None):
    """
    Gera uma linha de separação visual para logs e relatórios.

    Args:
        titulo (str, optional): Título centralizado sobre a linha.

    Returns:
        str: Linha de 70 caracteres, opcionalmente com título.
    """
    linha = "=" * 70
    if titulo:
        return f"\n{linha}\n{titulo.center(70)}\n{linha}\n"
    return f"\n{linha}\n"


def resumo_qualidade(dataframe):
    """
    Gera resumo de qualidade dos dados, incluindo nulos e duplicados.

    Args:
        dataframe (pd.DataFrame): DataFrame a ser analisado.

    Returns:
        str: Resumo textual da qualidade dos dados.
    """
    return f"""{desenhar_linha("Qualidade dos Dados")}
Registros Nulos por Coluna:
{dataframe.isnull().sum()}
{desenhar_linha()}
Registros Duplicados: {dataframe.duplicated().sum()}
{desenhar_linha()}"""


def informacoes_dataset(dataframe: pd.DataFrame, nome: str) -> str:
    """
    Retorna informações detalhadas sobre o dataset, incluindo:
    - Info do DataFrame
    - Shape
    - Resumo categórico
    - Resumo numérico
    - Qualidade de dados (nulos e duplicados)

    Args:
        dataframe (pd.DataFrame): DataFrame a ser analisado.
        nome (str): Nome do dataset para identificação.

    Returns:
        str: Texto com o relatório completo do dataset.
    """
    nome = nome.lower().strip()
    buffer = io.StringIO()
    dataframe.info(buf=buffer)
    info_str = buffer.getvalue()

    saida = f"""
{info_str}
{desenhar_linha("Shape")}
{dataframe.shape}
"""

    # Resumo categórico
    cat_cols = dataframe.select_dtypes(include=["object", "category"])
    if not cat_cols.empty:
        saida += f"""{desenhar_linha("Resumo Categórico")}
{cat_cols.describe().transpose()}
"""
    else:
        saida += f"""{desenhar_linha("Resumo Categórico")}
Nenhuma coluna categórica encontrada.
"""

    # Resumo numérico
    num_cols = dataframe.select_dtypes(include=["number"])
    if not num_cols.empty:
        saida += f"""{desenhar_linha("Resumo Numérico")}
{num_cols.describe().transpose()}
"""
    else:
        saida += f"""{desenhar_linha("Resumo Numérico")}
Nenhuma coluna numérica encontrada.
"""

    saida += resumo_qualidade(dataframe)
    return saida


# ------------------ Transformações de Dados ------------------ #


def converter_tipos(df: pd.DataFrame, tipos: dict) -> pd.DataFrame:
    """
    Converte colunas de um DataFrame para tipos especificados.

    Args:
        df (pd.DataFrame): DataFrame a ser convertido.
        tipos (dict): Dicionário {coluna: tipo}.

    Returns:
        pd.DataFrame: DataFrame com colunas convertidas.
    """
    for coluna, tipo in tipos.items():
        if coluna in df.columns:
            try:
                df[coluna] = df[coluna].astype(tipo)
            except ValueError:
                df[coluna] = pd.to_numeric(df[coluna], errors="coerce").astype(tipo)
    return df


def remover_duplicados(df: pd.DataFrame, subset=None, keep="first") -> pd.DataFrame:
    """
    Remove registros duplicados de um DataFrame.

    Args:
        df (pd.DataFrame): DataFrame a ser limpo.
        subset (list, optional): Colunas para considerar duplicados.
        keep (str, optional): Qual registro manter ("first" ou "last").

    Returns:
        pd.DataFrame: DataFrame sem duplicados.
    """
    qtd_antes = len(df)
    df_sem_dup = df.drop_duplicates(subset=subset, keep=keep)
    qtd_depois = len(df_sem_dup)
    removidos = qtd_antes - qtd_depois

    print(desenhar_linha("Remoção de Duplicados"))
    if subset:
        print(f"Colunas consideradas: {subset}")
    print(f"Registros antes: {qtd_antes}")
    print(f"Registros depois: {qtd_depois}")
    print(f"Duplicados removidos: {removidos}")
    print(desenhar_linha())

    return df_sem_dup


# ------------------ Inserção em Banco de Dados ------------------ #


def inserir_dados(dataframe, engine, tabela):
    """
    Insere dados em uma tabela de banco via SQLAlchemy.

    Args:
        dataframe (pd.DataFrame): Dados a serem inseridos.
        engine (Engine): Engine SQLAlchemy.
        tabela (str): Nome da tabela no banco.
    """
    df = dataframe.copy()
    df["inserido_em"] = pd.Timestamp.utcnow()  # controle temporal
    df.to_sql(tabela, engine, if_exists="replace", index=False, method="multi")


def conectar_banco(dataframe, tabela, if_exists="replace"):
    """
    Conecta ao banco e insere dados.

    Args:
        dataframe (pd.DataFrame): Dados a serem inseridos.
        tabela (str): Nome da tabela.
        if_exists (str, optional): Comportamento se a tabela existir ("replace", "append").
    """
    engine = obter_engine()

    try:
        with engine.connect() as connection:
            print("✅ Conexão bem-sucedida")
            inserir_dados(dataframe, engine, tabela)
            print(f"✅ Dados inseridos na tabela {tabela}")
    except Exception as e:
        print("❌ Erro ao conectar ou inserir dados no banco")
        print(type(e).__name__, str(e))

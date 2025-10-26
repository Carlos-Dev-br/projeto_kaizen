import io
import pandas as pd


def desenhar_linha(titulo=None):
    linha = "=" * 70
    if titulo:
        return f"\n{linha}\n{titulo.center(70)}\n{linha}\n"
    return f"\n{linha}\n"


def resumo_qualidade(dataframe):
    return f"""{desenhar_linha("Qualidade dos Dados")}
Registros Nulos por Coluna:
{dataframe.isnull().sum()}

{desenhar_linha()}
Registros Duplicados: {dataframe.duplicated().sum()}
{desenhar_linha()}
"""


def informacoes_dataset(dataframe: pd.DataFrame, nome: str) -> str:
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
{cat_cols.describe(include='all').transpose()}
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


def converter_tipos(df: pd.DataFrame, tipos: dict, verbose=False) -> pd.DataFrame:
    for coluna, tipo in tipos.items():
        if coluna in df.columns:
            try:
                df[coluna] = df[coluna].astype(tipo)
                if verbose:
                    print(f"✔ Coluna '{coluna}' convertida para {tipo}")
            except Exception as e:
                if verbose:
                    print(f"⚠ Erro ao converter '{coluna}': {e}")
                if tipo in [int, float]:
                    df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    return df


def remover_duplicados(df: pd.DataFrame, subset=None, keep="first", verbose=True) -> pd.DataFrame:
    qtd_antes = len(df)
    df_sem_dup = df.drop_duplicates(subset=subset, keep=keep)
    qtd_depois = len(df_sem_dup)
    removidos = qtd_antes - qtd_depois

    msg = f"""{desenhar_linha("Remoção de Duplicados")}
Colunas consideradas: {subset if subset else 'Todas'}
Registros antes: {qtd_antes}
Registros depois: {qtd_depois}
Duplicados removidos: {removidos}
{desenhar_linha()}
"""

    if verbose:
        print(msg)

    return df_sem_dup


if __name__ == "__main__":
    df_pokemons = pd.read_csv("out/pokemons.csv", sep=",", encoding="utf-8")
    df_atributos = pd.read_csv("out/atributos_pokemon.csv", sep=",", encoding="utf-8")
    df_combates = pd.read_csv("out/combates.csv", sep=",", encoding="utf-8")

    print(informacoes_dataset(df_pokemons, "pokemons"))
    print(informacoes_dataset(df_atributos, "atributos_pokemon"))
    print(informacoes_dataset(df_combates, "combates"))

    df_combates = remover_duplicados(df_combates)

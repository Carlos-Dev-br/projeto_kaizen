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
{desenhar_linha()}"""


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

    # Resumo categórico (somente se houver colunas do tipo object/category)
    cat_cols = dataframe.select_dtypes(include=["object", "category"])
    if not cat_cols.empty:
        saida += f"""{desenhar_linha("Resumo Categórico")}
{cat_cols.describe().transpose()}
"""
    else:
        saida += f"""{desenhar_linha("Resumo Categórico")}
Nenhuma coluna categórica encontrada.
"""

    # Resumo numérico (somente se houver colunas numéricas)
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


def converter_tipos(df: pd.DataFrame, tipos: dict) -> pd.DataFrame:
    for coluna, tipo in tipos.items():
        if coluna in df.columns:
            try:
                df[coluna] = df[coluna].astype(tipo)
            except ValueError:
                df[coluna] = pd.to_numeric(df[coluna], errors="coerce").astype(tipo)
    return df

def remover_duplicados(df: pd.DataFrame, subset=None, keep="first") -> pd.DataFrame:
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


if __name__ == "_main_":
    df_pokemons = pd.read_csv("out/pokemons.csv", sep=",", encoding="utf-8")
    df_atributos = pd.read_csv("out/atributos_pokemon.csv", sep=",", encoding="utf-8")
    df_combates = pd.read_csv("out/combates.csv", sep=",", encoding="utf-8")

    print(informacoes_dataset(df_pokemons, "pokemons"))
    print(informacoes_dataset(df_atributos, "atributos_pokemon"))
    print(informacoes_dataset(df_combates, "combates"))

    df_combates = remover_duplicados(df_combates)
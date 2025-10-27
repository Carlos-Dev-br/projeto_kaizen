"""
Dashboard Pokémon - Análise de Combates e Atributos

Este módulo realiza a extração, transformação, análise e visualização de dados
sobre combates de Pokémon. Ele gera dashboards HTML interativos com gráficos
de barras e radar, mostrando as estatísticas do top 10 vencedores e atributos
comparativos com a média geral.

Principais funcionalidades:
- Conexão e leitura de dados do banco de dados
- Combinação de tabelas de combates e atributos
- Cálculo de estatísticas: vitórias, derrotas e taxa de vitória
- Análise do top 10 Pokémon vencedores e derrotados
- Comparação de atributos do top 10 com a média geral
- Geração de gráficos interativos (barras e radar)
- Exportação de dashboard HTML completo
"""

import pandas as pd
from banco_conexao import obter_engine
import plotly.graph_objects as go
import plotly.express as px
import os

# ------------------ Funções de Conexão e Manipulação de Dados ------------------ #


def conectar_banco():
    """
    Conecta ao banco de dados utilizando a função `obter_engine`.

    Retorna:
        engine: SQLAlchemy engine conectado ao banco
    """
    engine = obter_engine()
    return engine


def carregar_tabela(nome_tabela: str) -> pd.DataFrame:
    """
    Carrega uma tabela do banco de dados para um DataFrame do pandas.

    Args:
        nome_tabela (str): Nome da tabela a ser carregada.

    Retorna:
        pd.DataFrame: Dados da tabela ou None em caso de erro.
    """
    engine = conectar_banco()
    try:
        return pd.read_sql(f"SELECT * FROM {nome_tabela}", engine)
    except Exception:
        return None


def salvar_tabela(df: pd.DataFrame, nome_tabela: str):
    """
    Salva um DataFrame em uma tabela do banco de dados, substituindo-a se já existir.

    Args:
        df (pd.DataFrame): DataFrame a ser salvo.
        nome_tabela (str): Nome da tabela no banco.
    """
    engine = conectar_banco()
    df.to_sql(nome_tabela, engine, if_exists="replace", index=False, method="multi")


# ------------------ Pipeline de Processamento ------------------ #


def combinar_tabelas():
    """
    Combina a tabela de combates com os atributos dos Pokémon,
    adicionando os nomes de cada Pokémon envolvido no combate.

    Retorna:
        pd.DataFrame: Combates com nomes dos Pokémon.
    """
    df_attr = carregar_tabela("atributos_pokemon")
    df_combates = carregar_tabela("combates")

    df_merged = (
        df_combates.merge(
            df_attr[["ID", "Nome"]], left_on="first_pokemon", right_on="ID", how="left"
        )
        .rename(columns={"Nome": "nome_first"})
        .drop(columns=["ID"])
        .merge(
            df_attr[["ID", "Nome"]], left_on="second_pokemon", right_on="ID", how="left"
        )
        .rename(columns={"Nome": "nome_second"})
        .drop(columns=["ID"])
        .merge(df_attr[["ID", "Nome"]], left_on="winner", right_on="ID", how="left")
        .rename(columns={"Nome": "nome_winner"})
        .drop(columns=["ID"])
    )

    salvar_tabela(df_merged, "combates_com_nomes")
    return df_merged


def gerar_estatisticas(df: pd.DataFrame):
    """
    Calcula estatísticas de combate para cada Pokémon:
    vitórias, derrotas, número de lutas e taxa de vitória.

    Args:
        df (pd.DataFrame): DataFrame de combates com nomes de Pokémon.

    Retorna:
        pd.DataFrame: Estatísticas de todos os Pokémon.
    """
    vitorias = df["nome_winner"].value_counts().reset_index()
    vitorias.columns = ["Pokemon", "Vitorias"]

    participacoes = (
        pd.concat([df["nome_first"], df["nome_second"]]).value_counts().reset_index()
    )
    participacoes.columns = ["Pokemon", "Lutas"]

    estatisticas = participacoes.merge(vitorias, on="Pokemon", how="left").fillna(0)
    estatisticas["Derrotas"] = estatisticas["Lutas"] - estatisticas["Vitorias"]
    estatisticas["Taxa_Vitoria(%)"] = (
        estatisticas["Vitorias"] / estatisticas["Lutas"] * 100
    ).round(2)

    salvar_tabela(estatisticas, "estatisticas_pokemon")
    return estatisticas


def analisar_top10(df_estatisticas: pd.DataFrame):
    """
    Identifica o top 10 Pokémon por vitórias e derrotas.

    Args:
        df_estatisticas (pd.DataFrame): Estatísticas dos Pokémon.

    Retorna:
        tuple: (top10_vitorias, top10_derrotas) DataFrames.
    """
    top10_vitorias = df_estatisticas.nlargest(10, "Vitorias")
    top10_derrotas = df_estatisticas.nlargest(10, "Derrotas")
    salvar_tabela(top10_vitorias, "top10_vitorias")
    salvar_tabela(top10_derrotas, "top10_derrotas")
    return top10_vitorias, top10_derrotas


def analisar_atributos_top10(top10_vitorias: pd.DataFrame):
    """
    Compara atributos do top 10 vencedores com a média geral dos Pokémon.

    Args:
        top10_vitorias (pd.DataFrame): DataFrame com top 10 vencedores.

    Retorna:
        tuple: (atributos_top10, comparativo, atributos_geral)
    """
    df_attr = carregar_tabela("atributos_pokemon")
    df_top10_attr = df_attr[df_attr["Nome"].isin(top10_vitorias["Pokemon"])]

    colunas_attr = df_attr.select_dtypes(include="number").columns

    medias_top10 = df_top10_attr[colunas_attr].mean().round(2)
    medias_geral = df_attr[colunas_attr].mean().round(2)

    comparativo = pd.DataFrame(
        {
            "Média_Top10": medias_top10,
            "Média_Geral": medias_geral,
            "Diferença": (medias_top10 - medias_geral).round(2),
        }
    ).sort_values(by="Diferença", ascending=False)

    salvar_tabela(df_top10_attr, "atributos_top10_vencedores")

    comparativo_reset = comparativo.reset_index()
    if "index" in comparativo_reset.columns:
        comparativo_reset = comparativo_reset.rename(columns={"index": "Atributo"})
    if comparativo_reset.columns.duplicated().any():
        comparativo_reset = comparativo_reset.loc[
            :, ~comparativo_reset.columns.duplicated()
        ]

    salvar_tabela(comparativo_reset, "comparativo_atributos_top10")
    return df_top10_attr, comparativo_reset, df_attr


# ------------------ Inicialização de Dados ------------------ #


def inicializar_dados():
    """
    Carrega dados processados do banco ou gera-os caso não existam.

    Retorna:
        tuple: DataFrames (top10_vitorias, top10_derrotas, df_top10_attr, comparativo, df_attr_geral)
    """
    comparativo = carregar_tabela("comparativo_atributos_top10")
    df_top10_attr = carregar_tabela("atributos_top10_vencedores")
    df_attr_geral = carregar_tabela("atributos_pokemon")
    top10_vitorias = carregar_tabela("top10_vitorias")
    top10_derrotas = carregar_tabela("top10_derrotas")

    if comparativo is None or df_top10_attr is None:
        df_completo = combinar_tabelas()
        df_estatisticas = gerar_estatisticas(df_completo)
        top10_vitorias, top10_derrotas = analisar_top10(df_estatisticas)
        df_top10_attr, comparativo, df_attr_geral = analisar_atributos_top10(
            top10_vitorias
        )

    return top10_vitorias, top10_derrotas, df_top10_attr, comparativo, df_attr_geral


# ------------------ Visualização ------------------ #


def criar_grafico_barras(comparativo: pd.DataFrame):
    """
    Cria gráfico de barras comparando atributos do Top 10 com a média geral.

    Args:
        comparativo (pd.DataFrame): DataFrame com médias dos atributos.

    Retorna:
        plotly.graph_objects.Figure: Gráfico de barras interativo.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=comparativo["Atributo"],
            y=comparativo["Média_Top10"],
            name="Média Top 10",
            marker_color="#1f77b4",
        )
    )
    fig.add_trace(
        go.Bar(
            x=comparativo["Atributo"],
            y=comparativo["Média_Geral"],
            name="Média Geral",
            marker_color="#ff7f0e",
        )
    )
    fig.update_layout(
        barmode="group",
        title="Comparativo de Atributos: Top 10 vs Média Geral",
        xaxis_title="Atributos",
        yaxis_title="Valor Médio",
        template="plotly_white",
    )
    return fig


def criar_grafico_radar(df_top10_attr: pd.DataFrame, df_attr_geral: pd.DataFrame):
    """
    Cria gráfico radar comparando atributos do Top 10 com a média geral.

    Args:
        df_top10_attr (pd.DataFrame): Atributos dos Top 10 vencedores.
        df_attr_geral (pd.DataFrame): Atributos de todos os Pokémon.

    Retorna:
        plotly.graph_objects.Figure: Gráfico radar interativo.
    """
    colunas_attr = df_top10_attr.select_dtypes(include="number").columns
    media_geral = df_attr_geral[colunas_attr].mean().round(2)
    fig = go.Figure()

    for _, row in df_top10_attr.iterrows():
        fig.add_trace(
            go.Scatterpolar(
                r=row[colunas_attr].values,
                theta=colunas_attr,
                fill="toself",
                name=row["Nome"],
            )
        )

    fig.add_trace(
        go.Scatterpolar(
            r=media_geral.values,
            theta=colunas_attr,
            fill="toself",
            name="Média Geral",
            line=dict(color="black", dash="dash"),
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        title="Radar: Top 10 vs Média Geral",
        template="plotly_white",
    )
    return fig


# ------------------ Dashboard HTML ------------------ #


def gerar_dashboard():
    """
    Gera dashboard HTML completo com tabelas e gráficos,
    salvando-o em 'report/dashboard_pokemon_estilizado.html'.
    """
    top10_vitorias, top10_derrotas, df_top10_attr, comparativo, df_attr_geral = (
        inicializar_dados()
    )
    fig_barras = criar_grafico_barras(comparativo)
    fig_radar = criar_grafico_radar(df_top10_attr, df_attr_geral)

    os.makedirs("report", exist_ok=True)

    html_content = f"""
    <html>
    <head>
        <title>Dashboard Pokémon</title>
        <meta charset="utf-8">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: Arial; background-color: #f5f5f5; margin: 20px; }}
            h1 {{ text-align: center; color: #ff1a1a; }}
            h2 {{ text-align: center; color: #333; margin-top:40px; }}
            table {{ margin-left:auto; margin-right:auto; border-collapse: collapse; width: 80%; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: center; }}
            th {{ background-color: #1f77b4; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .card {{ background-color: white; padding: 20px; margin: 20px auto; width: 80%; box-shadow: 0 0 10px rgba(0,0,0,0.15); border-radius: 10px; }}
        </style>
    </head>
    <body>
        <h1>📊 Dashboard Pokémon - Top 10</h1>
        <div class="card">
            <h2>🏆 Top 10 Vencedores</h2>
            {top10_vitorias.to_html(index=False)}
        </div>
        <div class="card">
            <h2>💀 Top 10 Derrotados</h2>
            {top10_derrotas.to_html(index=False)}
        </div>
        <div class="card">
            <h2>📊 Comparativo de Atributos</h2>
            <div id="grafico_barras"></div>
        </div>
        <div class="card">
            <h2>🕸️ Gráfico Radar - Top 10 vs Média Geral</h2>
            <div id="grafico_radar"></div>
        </div>
        <script>
            Plotly.newPlot('grafico_barras', {fig_barras.to_json()});
            Plotly.newPlot('grafico_radar', {fig_radar.to_json()});
        </script>
    </body>
    </html>
    """

    with open("report/dashboard_pokemon_estilizado.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("✅ Dashboard salvo em 'report/dashboard_pokemon_estilizado.html'.")

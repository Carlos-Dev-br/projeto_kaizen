"""
Dashboard Pokémon - Streamlit

Este módulo cria um dashboard interativo utilizando Streamlit e Plotly.
Permite visualizar:
- Top 10 vencedores e derrotados
- Comparativo de atributos dos Pokémon (Top 10 vs Média Geral)
- Gráficos de barras e radar

Funcionalidades:
1. Conexão com banco de dados PostgreSQL via SQLAlchemy.
2. Carregamento de tabelas essenciais para o dashboard.
3. Criação de gráficos interativos usando Plotly.
4. Formatação condicional para destacar diferenças nos atributos.
"""

import streamlit as st
import pandas as pd
from src.banco_conexao import obter_engine
import plotly.graph_objects as go


# ------------------ Funções de dados ------------------ #
def conectar_banco():
    """
    Cria e retorna uma conexão com o banco de dados via SQLAlchemy.

    Returns:
        Engine: SQLAlchemy Engine conectado ao banco.
    """
    engine = obter_engine()
    return engine


def carregar_tabela(nome_tabela: str) -> pd.DataFrame:
    """
    Carrega uma tabela do banco de dados para um DataFrame.

    Args:
        nome_tabela (str): Nome da tabela a ser carregada.

    Returns:
        pd.DataFrame: Dados da tabela. Retorna DataFrame vazio em caso de erro.
    """
    engine = conectar_banco()
    try:
        return pd.read_sql(f"SELECT * FROM {nome_tabela}", engine)
    except Exception:
        return pd.DataFrame()


# ------------------ Funções de Gráficos ------------------ #
def criar_grafico_barras(comparativo: pd.DataFrame):
    """
    Cria gráfico de barras comparando os atributos do Top 10 Pokémon com a média geral.

    Args:
        comparativo (pd.DataFrame): DataFrame contendo colunas 'Atributo', 'Média_Top10', 'Média_Geral'.

    Returns:
        plotly.graph_objects.Figure: Figura interativa de barras.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=comparativo["Atributo"],
            y=comparativo["Média_Top10"],
            name="Média Top 10",
            marker_color="#1f77b4",
            hovertemplate="%{x}: %{y:.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=comparativo["Atributo"],
            y=comparativo["Média_Geral"],
            name="Média Geral",
            marker_color="#ff7f0e",
            hovertemplate="%{x}: %{y:.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        barmode="group",
        title="Comparativo de Atributos: Top 10 vs Média Geral",
        xaxis_title="Atributos",
        yaxis_title="Valor Médio",
        template="plotly_dark",
        plot_bgcolor="#000000",
        paper_bgcolor="#000000",
        font=dict(color="white"),
    )
    return fig


def criar_grafico_radar(df_top10_attr: pd.DataFrame, df_attr_geral: pd.DataFrame):
    """
    Cria gráfico radar comparando os atributos do Top 10 Pokémon com a média geral.

    Args:
        df_top10_attr (pd.DataFrame): Atributos detalhados do Top 10 Pokémon.
        df_attr_geral (pd.DataFrame): Atributos gerais de todos os Pokémon.

    Returns:
        plotly.graph_objects.Figure: Figura radar interativa.
    """
    colunas_attr = df_top10_attr.select_dtypes(include="number").columns
    df_top10_attr_numeric = df_top10_attr.copy()
    df_top10_attr_numeric[colunas_attr] = (
        df_top10_attr_numeric[colunas_attr]
        .apply(pd.to_numeric, errors="coerce")
        .round(2)
    )
    media_geral = (
        df_attr_geral[colunas_attr]
        .apply(pd.to_numeric, errors="coerce")
        .mean()
        .round(2)
    )

    fig = go.Figure()
    for _, row in df_top10_attr_numeric.iterrows():
        fig.add_trace(
            go.Scatterpolar(
                r=row[colunas_attr].values,
                theta=colunas_attr,
                fill="toself",
                name=row["Nome"],
                hovertemplate="%{theta}: %{r:.2f}<extra></extra>",
            )
        )
    fig.add_trace(
        go.Scatterpolar(
            r=media_geral.values,
            theta=colunas_attr,
            fill="toself",
            name="Média Geral",
            line=dict(color="white", dash="dash"),
            hovertemplate="%{theta}: %{r:.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        title="Radar: Top 10 vs Média Geral",
        template="plotly_dark",
        plot_bgcolor="#000000",
        paper_bgcolor="#000000",
        font=dict(color="white"),
    )
    return fig


# ------------------ Função de destaque condicional ------------------ #
def colorir_diferenca(valor):
    """
    Retorna estilo CSS condicional para a coluna 'Diferença' do comparativo.

    Args:
        valor (float): Valor da diferença.

    Returns:
        str: Estilo CSS aplicável ao dataframe do Streamlit.
    """
    if pd.isna(valor):
        return ""
    elif valor > 0:
        return "color: #2ca02c; font-weight: bold;"  # verde
    elif valor < 0:
        return "color: #d62728; font-weight: bold;"  # vermelho
    else:
        return ""


# ------------------ Streamlit App ------------------ #
def main():
    """
    Função principal que inicializa e exibe o dashboard Streamlit.
    """
    st.set_page_config(page_title="Dashboard Pokémon", layout="wide", page_icon="📊")
    st.title("📊 Dashboard Pokémon - Top 10")
    st.markdown("---")

    # Carregar dados do banco
    top10_vitorias = carregar_tabela("top10_vitorias")
    top10_derrotas = carregar_tabela("top10_derrotas")
    comparativo = carregar_tabela("comparativo_atributos_top10")
    df_top10_attr = carregar_tabela("atributos_top10_vencedores")
    df_attr_geral = carregar_tabela("atributos_pokemon")

    # ------------------ Ajuste de tipos numéricos ------------------ #
    for df in [top10_vitorias, top10_derrotas]:
        for col in df.select_dtypes(include="number").columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

    comparativo = comparativo.drop(
        columns=[c for c in ["ID"] if c in comparativo.columns]
    )
    colunas_numericas_comparativo = [
        c
        for c in ["Média_Top10", "Média_Geral", "Diferença"]
        if c in comparativo.columns
    ]
    for col in colunas_numericas_comparativo:
        comparativo[col] = pd.to_numeric(comparativo[col], errors="coerce").round(2)

    # ------------------ Exibição de Tabelas ------------------ #
    st.subheader("🏆 Top 10 Vencedores")
    st.dataframe(
        top10_vitorias.style.format(
            {
                col: "{:.2f}"
                for col in top10_vitorias.select_dtypes(include="number").columns
            }
        ).set_table_styles(
            [
                {
                    "selector": "thead",
                    "props": [("background-color", "#1f77b4"), ("color", "white")],
                }
            ]
        )
    )

    st.subheader("💀 Top 10 Derrotados")
    st.dataframe(
        top10_derrotas.style.format(
            {
                col: "{:.2f}"
                for col in top10_derrotas.select_dtypes(include="number").columns
            }
        ).set_table_styles(
            [
                {
                    "selector": "thead",
                    "props": [("background-color", "#ff4136"), ("color", "white")],
                }
            ]
        )
    )

    st.subheader("📊 Comparativo de Atributos")
    st.dataframe(
        comparativo.style.format(
            {col: "{:.2f}" for col in colunas_numericas_comparativo}
        )
        .applymap(colorir_diferenca, subset=["Diferença"])
        .set_table_styles(
            [
                {
                    "selector": "thead",
                    "props": [("background-color", "#1f77b4"), ("color", "white")],
                }
            ]
        )
    )

    # ------------------ Gráficos ------------------ #
    st.subheader("📊 Gráfico Comparativo de Atributos")
    st.plotly_chart(criar_grafico_barras(comparativo), use_container_width=True)

    st.subheader("🕸️ Gráfico Radar - Top 10 vs Média Geral")
    st.plotly_chart(
        criar_grafico_radar(df_top10_attr, df_attr_geral), use_container_width=True
    )

    st.markdown("---")
    st.markdown(
        "<p style='color:white;text-align:center;'>Análise Geral dos Dados</p>",
        unsafe_allow_html=True,
    )


# ------------------ Execução ------------------ #
if __name__ == "__main__":
    main()

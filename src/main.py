import pandas as pd
from analisar_dados_banco import gerar_dashboard
from obtencao_dados import (
    verificar_saude,
    obter_token_jwt,
    obter_dados_pokemon,
    obter_atributos_pokemon,
    obter_dados_combate,
    transformar_csv,
)
from tratamento_dados import informacoes_dataset, remover_duplicados, conectar_banco

if __name__ == "__main__":
        response = obter_token_jwt()
        token = response.json().get("access_token") if response else None

        if token:
            verificar_saude(token)
            lista_pokemon = obter_dados_pokemon(token)
            transformar_csv(lista_pokemon, "pokemons")

            lista_atributos = obter_atributos_pokemon(token)
            transformar_csv(lista_atributos, "atributos_pokemon")

            lista_combates = obter_dados_combate(token)
            transformar_csv(lista_combates, "combates")
        else:
            print("❌ Falha ao obter token JWT.")
        
          # Carregar CSVs
        df_pokemons = pd.read_csv("out/pokemons.csv", sep=",", encoding="utf-8")
        df_atributos = pd.read_csv("out/atributos_pokemon.csv", sep=",", encoding="utf-8")
        df_combates = pd.read_csv("out/combates.csv", sep=",", encoding="utf-8")

        # Informações detalhadas dos datasets
        print(informacoes_dataset(df_pokemons, "pokemons"))
        print(informacoes_dataset(df_atributos, "atributos_pokemon"))
        print(informacoes_dataset(df_combates, "combates"))

        # Limpeza de duplicados
        df_combates = remover_duplicados(df_combates)

        # Inserção no banco
        dfs = [df_pokemons, df_atributos, df_combates]
        bancos = ["pokemons", "atributos_pokemon", "combates"]

        for df, banco in zip(dfs, bancos):
            conectar_banco(df, banco)
        
        gerar_dashboard()
    

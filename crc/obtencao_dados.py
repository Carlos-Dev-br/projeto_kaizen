import requests
import csv
import pandas as pd
from time import sleep

BASE_URL = "http://ec2-52-67-119-247.sa-east-1.compute.amazonaws.com:8000"
LOGIN_URL = f"{BASE_URL}/login"
HEALTH_URL = f"{BASE_URL}/health"
POKEMON_URL = f"{BASE_URL}/pokemon"

def get_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def obter_token_jwt():
    credentials = {
        "username": "kaizen-poke",
        "password": "4w9f@D39fkkO"
    }

    response = requests.post(LOGIN_URL, json=credentials)
    print(f"Login realizado com sucesso!\nStatus Code: {response.status_code}")
    return response


def verificar_saude(token):
    headers = get_headers(token)

    try:
        response = requests.get(HEALTH_URL, headers=headers)
        if response.status_code == 200:
            print("Acesso autorizado!\nSaúde da Aplicação:")
            print(response.json())
        else:
            print("Erro ao acessar recurso:", response.status_code)
            print(response.text)
    except requests.exceptions.RequestException as e:
        print("Ocorreu um erro na requisição:", str(e))


def obter_dados_pokemon(token):
    lista_pokemon = []
    headers = get_headers(token)

    print("Iniciando coleta de dados dos Pokémons...\n")
    try:
        for i in range(1, 51):
            response = requests.get(f"{POKEMON_URL}?page={i}&per_page=50", headers=headers)

            if response.status_code != 200:
                print(f"Erro na página {i}: {response.status_code}")
                print(response.text)
                break

            dados = response.json()
            pokemons = dados.get("pokemons", [])

            if not pokemons:
                print("Todos os Pokémons foram obtidos.")
                break

            for p in pokemons:
                id_ = p.get("id")
                nome = (p.get("name") or "").strip()
                lista_pokemon.append((id_, nome))

            sleep(1)

    except requests.exceptions.RequestException as e:
        print("Ocorreu um erro na requisição:", str(e))

    print(f"Total de Pokémons coletados: {len(lista_pokemon)}\n")
    return lista_pokemon


def obter_atributos_pokemon(token):
    lista_atributos_pokemon = []
    headers = get_headers(token)

    try:
        df_id = pd.read_csv("pokemons.csv")
        print(f"{len(df_id)} Pokémons carregados do arquivo CSV.\n")

        for pokemon_id in df_id["ID"]:
            response = requests.get(f"{POKEMON_URL}/{pokemon_id}", headers=headers)

            if response.status_code != 200:
                print(f"Erro ao consultar os Atributos do Pokémon {pokemon_id}: {response.status_code}")
                print(response.text)
                continue  

            dados = response.json()

            id_ = dados.get("id")
            nome = dados.get("name").strip()
            hp = dados.get("hp")
            attack = dados.get("attack")
            defense = dados.get("defense")
            sp_attack = dados.get("sp_attack")
            sp_defense = dados.get("sp_defense")
            speed = dados.get("speed")
            generation = dados.get("generation")
            legendary = dados.get("legendary")
            types = dados.get("types", [])

            lista_atributos_pokemon.append({
                "ID": id_,
                "Nome": nome,
                "Hp": hp,
                "Attack": attack,
                "Defense": defense,
                "Sp_attack": sp_attack,
                "Sp_defense": sp_defense,
                "Speed": speed,
                "Generation": generation,
                "Legendary": legendary,
                "Types": types
            })
            
            sleep(0.5)
        print(f"\nTotal de Pokémons detalhados: {len(lista_atributos_pokemon)}")

    except FileNotFoundError:
        print("Arquivo 'pokemons.csv' não encontrado.")
    except requests.exceptions.RequestException as e:
        print("Erro de conexão com a API:", str(e))
    except Exception as e:
        print("Erro inesperado:", str(e))

    return lista_atributos_pokemon


def transformar_csv(dados, file_):
    if file_ == 'pokemons':
        with open(f"{file_}.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Nome"])
            for id_, nome in dados:
                writer.writerow([id_, nome])
    elif file_ == 'atributos_pokemon':
        with open(f"{file_}.csv", mode="w", newline="", encoding="utf-8") as file:
            fieldnames = ["ID", "Nome", "Hp", "Attack", "Defense", "Sp_attack", "Sp_defense", "Speed", "Generation", "Legendary", "Types"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for item in dados:
                writer.writerow(item)

    print(f"Dados salvos em '{file_}.csv' com sucesso!")


if __name__ == "__main__":
    response = obter_token_jwt()
    token = response.json().get("access_token")

    if token:
        verificar_saude(token)
        lista = obter_dados_pokemon(token)
        transformar_csv(lista, 'pokemons')
        lista_atributos = obter_atributos_pokemon(token)
        transformar_csv(lista_atributos, 'atributos_pokemon')
    else:
        print("Falha ao obter token JWT.")

import requests
import csv
from time import sleep

BASE_URL = "http://ec2-52-67-119-247.sa-east-1.compute.amazonaws.com:8000"
LOGIN_URL = f"{BASE_URL}/login"
HEALTH_URL = f"{BASE_URL}/health"
POKEMON_URL = f"{BASE_URL}/pokemon"


def obter_token_jwt():
    credentials = {
        "username": "kaizen-poke",
        "password": "4w9f@D39fkkO"
    }

    response = requests.post(LOGIN_URL, json=credentials)
    if response.status_code == 200:
        print(f"Login realizado com sucesso! (Status Code: {response.status_code})")
    else:
        print(f"Falha no login. Status Code: {response.status_code}")
        print(response.text)
    return response


def verificar_saude(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

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
    headers = {
        "Authorization": f"Bearer {token}"
    }

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

            sleep(1)  # Evita sobrecarregar o servidor

    except requests.exceptions.RequestException as e:
        print("Ocorreu um erro na requisição:", str(e))

    print(f"Total de Pokémons coletados: {len(lista_pokemon)}\n")
    return lista_pokemon


def transformar_csv(dados):
    with open("pokemons.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Nome"])
        writer.writerows(dados)
    print("Dados salvos em 'pokemons.csv' com sucesso!")


if __name__ == "__main__":
    response = obter_token_jwt()
    token = response.json().get("access_token")

    if token:
        verificar_saude(token)
        lista = obter_dados_pokemon(token)
        transformar_csv(lista)
    else:
        print("Falha ao obter token JWT.")

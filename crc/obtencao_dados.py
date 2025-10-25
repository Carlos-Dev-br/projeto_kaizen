import requests

def obter_token_jwt():
    # URL base da API
    BASE_URL = "http://ec2-52-67-119-247.sa-east-1.compute.amazonaws.com:8000"
    LOGIN_URL = f"{BASE_URL}/login"

    # Credenciais
    credentials = {
        "username": "kaizen-poke",
        "password": "4w9f@D39fkkO"
    }

    # Fazendo login (enviando JSON)
    response = requests.post(LOGIN_URL, json=credentials)
    return response


response = obter_token_jwt()

if response.status_code == 200:
    token = response.json().get("access_token")
    print("✅ Login realizado com sucesso!")
    print("Token JWT:", token)
else:
    print("❌ Erro ao autenticar:", response.status_code)
    print(response.text)
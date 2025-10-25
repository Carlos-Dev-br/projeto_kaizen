import requests

def obter_token_jwt():
    BASE_URL = "http://ec2-52-67-119-247.sa-east-1.compute.amazonaws.com:8000"
    LOGIN_URL = f"{BASE_URL}/login"

    credentials = {
        "username": "kaizen-poke",
        "password": "4w9f@D39fkkO"
    }

    response = requests.post(LOGIN_URL, json=credentials)
    return response

response = obter_token_jwt()
token = response.json().get("access_token")

if token:
    
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get("http://ec2-52-67-119-247.sa-east-1.compute.amazonaws.com:8000/health", headers=headers)

    if response.status_code == 200:
        print("Acesso autorizado!")
        print(response.json())
    else:
        print("Erro ao acessar recurso:", response.status_code)
        print(response.text)

else:
    print("Token não obtido, verifique as credenciais.")

    
    
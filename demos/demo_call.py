import requests

# URL del endpoint POST de tu API
url = 'https://demo-ant-api-b26e14484ab9.herokuapp.com/retrieval_info/'
#url = 'http://127.0.0.1:8000/retrieval_info/'
# Datos que quieres enviar en la solicitud POST
data = {
    "content": "¿Cuáles son las direcciones de correo a las que un estudiante de la Facultad de Ciencias de la Universidad Nacional de Ingeniería debe dirigirse para solicitar constancias de Quinto y/o Tercio Superior?",
    "token_budget": 2500
}

# Enviar la solicitud POST
response = requests.post(url, json=data)

# Verificar el código de estado de la respuesta
if response.status_code == 200:
    # La solicitud fue exitosa, mostrar la respuesta
    print("Respuesta del servidor:", response.json())
else:
    # La solicitud falló, mostrar el código de estado
    print("La solicitud falló con el código de estado:", response.status_code)
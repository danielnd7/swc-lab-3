import requests

url = 'http://127.0.0.1:4001/nuevo?dato=99.2' # Definimos la URL a la que queremos hacer la petición

print("Sending request...")
response = requests.get(url) # Hacemos la petición GET con el parámetro y guardamos la respuesta en una variable
print("URL: " , response.url)
print("status code : " ,response.status_code)
print("text: " , response.text)
print("response: " ,response)



import requests
'''
url = 'http://127.0.0.1:4001/nuevo?dato=99.2' # Definimos la URL a la que queremos hacer la petición

print("Sending request...")
response = requests.get(url) # Hacemos la petición GET con el parámetro y guardamos la respuesta en una variable
print("URL: " , response.url)
print("status code : " ,response.status_code)
print("text: " , response.text)
print("response: " ,response)
'''
from kazoo.client import KazooClient

zk = KazooClient(hosts="127.0.0.1:2181")
zk.start()

try:
    # Ensure a path, create if necessary
    zk.ensure_path("/mediciones")

    # Create a node with data
    zk.create(f"/mediciones/01", ephemeral=True)

    zk.create(f"/mediciones/02", ephemeral=True)

except:
    print('ERROR: Node creation exception (maybe already exists)')

print("Followers values set \n")
zk.set(f"/mediciones/01", str(11).encode("utf-8"))
zk.set(f"/mediciones/02", str(22).encode("utf-8"))


print("LEADER :\n")

# List the children
children = zk.get_children("/mediciones")
# Check :
print("There are %s children with names %s" % (len(children), children))

for child in children:
    value, stats = zk.get(f"/mediciones/{child}")
    print(f"Value of the child {child} : " , value.decode("utf-8"))

from kazoo.client import KazooClient
from kazoo.recipe.election import Election
import threading
import time
import os
import random
import signal
import requests
from kazoo.recipe.watchers import ChildrenWatch
from kazoo.recipe.watchers import DataWatch

# Establecer la direccion de API y ZooKeeper
API_URL = os.getenv('API_URL', "http://127.0.0.1:4001/")
ZK_HOST = os.getenv('ZK_HOST', "127.0.0.1:2181")
SAMPLING_PERIOD = int(os.getenv('SAMPLING_PERIOD', "5"))

# Definir una función que se ejecuta cuando se recibe la señal de interrupción
def interrupt_handler(signal, frame):
    exit(0)

# Registrar la función como el manejador de la señal de interrupción
# So the script exits cleanly when interrupted (Ctrl+C) :
signal.signal(signal.SIGINT, interrupt_handler)

# Crear un identificador para la aplicación
id = input("Introduce un identificador: ")

# Crear un cliente kazoo y conectarlo con el servidor zookeeper
zk = KazooClient(hosts=ZK_HOST)
zk.start()

# Crear una elección entre las aplicaciones y elegir un líder
election = Election(zk, "/election", id)

# WATCHERS PARA TODOS (tanto leaders como followers) -------------------------------
# Asegurar que el nodo existe
zk.ensure_path("/config/sampling_period")
zk.ensure_path("/config/api_url")

# Funcion watcher
def watch_sampling_period(data, stat):
    global SAMPLING_PERIOD # Para que se actualize la variable global
    print("\n-----------WATCHER-----------")
    if data:
        print(f"Nuevo valor de SAMPLING_PERIOD: {data.decode('utf-8')}")
        SAMPLING_PERIOD = int(data.decode('utf-8'))
    else:
        print("Nodo de configuracion eliminado")
    print("-----------------------------\n")
    return True  # Mantener el watcher activo

# Registrar el watcher
DataWatch(zk, "/config/sampling_period", watch_sampling_period)

# LEADER ONLY --------------------------------------------------------------
# Definir una función que se ejecuta cuando una aplicación es elegida líder
def leader_func():

    # WATCHERS PARA LEADERS ------------------------------
    # Funcion watcher
    def watch_api_url(data, stat):
        global API_URL # Para que se actualize la variable global
        print("\n-----------WATCHER-----------")
        if data:
            print(f"Nuevo valor de API_URL: {data.decode('utf-8')}")
            API_URL = data.decode('utf-8')
        else:
            print("Nodo de configuracion eliminado")
        print("-----------------------------\n")
        return True  # Mantener el watcher activo

    # Registrar el watcher
    DataWatch(zk, "/config/api_url", watch_api_url)


    # Funcion watcher
    def children_watcher(all_children):
        print("\n-----------WATCHER-----------")
        print(f"Dispositivos conectados: {all_children}")
        print("-----------------------------\n")
        return True  # Mantener el watcher activo

    # Registrar el watcher
    ChildrenWatch(zk, "/mediciones", children_watcher)


    # LEADER MAIN FUNCTION --------------------------------
    while True:
        print("LEADER :")

        # Listar los hijos
        children = zk.get_children("/mediciones")
        # Check :
        print("Hay %s dispositivos activos: %s" % (len(children), children))

        if len(children) > 0:
            # Obtener valores de cada nodo hijo
            values = []
            for child in children:
                child_value, stats = zk.get(f"/mediciones/{child}")
                values.append(int(child_value.decode("utf-8")))
                print(f"Valor del dispositivo {child} a considerar : ", child_value.decode("utf-8"))

            # Calcular la media de los valores obtenidos
            mean_value = sum(values) / len(values)

            # Mostrar la media por consola
            print("La media es: %s" % mean_value)

        else:
            # En caso de que no haya hijos
            mean_value = 0

        # Enviar la media usando requests
        print("Enviando request...")
        try:
            url = f"{API_URL}nuevo?dato={mean_value}"
            response = requests.get(url)

            if response.status_code == 200:
                print("El nuevo valor fue enviado a la API correctamente!\n")
            else:
                print("ERROR: No se ha podido enviar el valor a la API")

        except Exception as e:
            print("ERROR: No se ha podido enviar el valor a la API : ", e)

        time.sleep(SAMPLING_PERIOD)


# Definir una función que se encarga de lanzar la parte de la elección
def election_func():
    # Participar en la elección con el identificador de la aplicación
    election.run(leader_func)


# Crear un hilo para ejecutar la función election_func:
# daemon=True tells Python: "Do not keep the program alive just for this thread."
# Standard Thread (daemon=False):
# If the main program finishes (e.g., reaches the end of the script),
# Python will wait for this thread to finish before actually closing the process.
election_thread = threading.Thread(target=election_func, daemon=True)

# Iniciar el hilo
election_thread.start()

# FOLLOWERS AND LEADER ------------------------------------------------------------------
try:
    # Ensure a path, create if necessary
    zk.ensure_path("/mediciones")

    # Create a node with data
    zk.create(f"/mediciones/{id}", ephemeral=True)
except:
    print('ERROR: Node creation exception (maybe already exists)')

# Enviar periódicamente un valor a una subruta de /mediciones con el identificador de la aplicación
while True:
    # Generar una nueva medición aleatoria
    value = random.randint(75, 85)

    # Modify the data of a node ...?? -> # Actualizar el valor de /values asociado al nodo
    zk.set(f"/mediciones/{id}", str(value).encode("utf-8"))
    print(f"Node {id}: {value} sent to zk\n")

    # Esperar 5 segundos
    time.sleep(SAMPLING_PERIOD)

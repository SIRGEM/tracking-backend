import meshtastic
import meshtastic.serial_interface
import time
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import uvicorn

global_known_nodes = {'data': None}

class BackgroundTasks(threading.Thread):
    def __init__(self, interface, known_nodes=None):
        threading.Thread.__init__(self)
        self.known_nodes = known_nodes or {}
        self._interface = interface
        self.ininitalized = False

    def run(self, *args, **kwargs):
        while True:
            print('========================================')
            self.task_get_nodes(self._interface)
            # self.task_print_nodes()
            time.sleep(5)
            self.ininitalized = True

    def task_get_nodes(self, interface):
        # Obtain and display a list of known nodes.
        for (node_id, node) in interface.nodes.items():
            self.known_nodes[node_id] = dict(node)
            # print(f"    {node}")

    def task_print_nodes(self):

        if self.known_nodes is None:
            print("No nodes found.")
            return

        for i, (node_id, node) in enumerate(self.known_nodes.items(), start=1):
            if node is None:
                continue
            try:
                position = node['position']
            except KeyError:
                position = None
            print(f"#{i}, Nodo ID: {node_id}, Nombre: {node['user']['longName']}, Posición: {position}")
            # print(f"    {node}")
    
    def get_known_nodes(self):
        response = {'data': None}
        if self.ininitalized:
            response = self.known_nodes
        return response

app = FastAPI()

# By default will try to find a meshtastic device,
# otherwise provide a device path like /dev/ttyUSB0
interface = meshtastic.serial_interface.SerialInterface()

# Start the background thread
t = BackgroundTasks(interface=interface, known_nodes=global_known_nodes)

# allows cross-origin requests from React
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def main():
    t.start()

    interface.close()
    
if __name__ == '__main__':
    # main()

    # Start the API server
    uvicorn.run(app, host="localhost", port=8000)


@app.on_event("startup")
async def startup_event():
    main()


@app.get("/")
async def root():
    return {"message": "Hello World"}

# endpoint to get all nodes
@app.get("/nodes")
async def get_nodes():
    print('get nodes...')
    global_known_nodes = t.get_known_nodes()
    return global_known_nodes
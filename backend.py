import meshtastic
import meshtastic.serial_interface
import time
import threading
from fastapi import FastAPI
import uvicorn

app = FastAPI()


class BackgroundTasks(threading.Thread):
    def __init__(self, interface):
        threading.Thread.__init__(self)
        self.known_nodes = {}
        self._interface = interface

    def run(self, *args, **kwargs):
        while True:
            print('========================================')
            self.task_get_nodes(self._interface)
            self.task_print_nodes()
            time.sleep(5)

    def task_get_nodes(self, interface):
        # Obtain and display a list of known nodes.
        for (node_id, node) in interface.nodes.items():
            self.known_nodes[node_id] = node
            # print(f"    {node}")

    def task_print_nodes(self):
        for i, (node_id, node) in enumerate(self.known_nodes.items(), start=1):
            try:
                position = node['position']
            except KeyError:
                position = None
            print(f"#{i}, Nodo ID: {node_id}, Nombre: {node['user']['longName']}, Posición: {position}")
            # print(f"    {node}")


if __name__ == '__main__':

    # By default will try to find a meshtastic device,
    # otherwise provide a device path like /dev/ttyUSB0
    interface = meshtastic.serial_interface.SerialInterface()

    # Start the background thread
    t = BackgroundTasks(interface=interface)
    t.start()

    # Start the API server
    uvicorn.run(app, host="localhost", port=8000)

    interface.close()

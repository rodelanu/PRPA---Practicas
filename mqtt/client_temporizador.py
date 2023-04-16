
# Realizado por: Rodrigo de la Nuez Moraleda

import paho.mqtt.publish as publish
from time import sleep
import sys

def main(hostname):
    topic = input('topic? ')
    while True:
        wait = input('espera? ')
        data  = input('message? ')
        print(f"Publishing {data} in :{topic}:")
        sleep(float(wait))
        publish.single(topic,  data, hostname=hostname)

if __name__ == "__main__":
    hostname = 'simba.fdi.ucm.es'
    if len(sys.argv)>1:
        hostname = sys.argv[1]
    main(hostname)
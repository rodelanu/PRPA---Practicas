
# Realizado por: Rodrigo de la Nuez Moraleda

from paho.mqtt.client import Client
import sys

def on_connect(mqttc, userdata, flags, rc):
    print("CONNECT:", userdata, flags, rc)

def on_message(mqttc, userdata, msg):
    print(len(messages), "- MESSAGE:", userdata, msg.topic, msg.qos, msg.payload, msg.retain)
    value = float(msg.payload.decode("utf-8"))
    messages.append(value)
    if value.is_integer():
        if is_prime(int(value)):
            print("- El número leído es un entero primo.")
        else:
            print("- El número leído es un entero NO primo.")
    else:
        print("- El número leído es real.")
    integer_frequency = sum(1 for value in messages if value.is_integer())
    float_frequency = sum(1 for value in messages if not value.is_integer())
    print("* Frecuencia de números enteros:", integer_frequency)
    print("* Frecuencia de números reales:", float_frequency)

def on_publish(mqttc, userdata, mid):
    print("PUBLISH:", userdata, mid)

def on_subscribe(mqttc, userdata, mid, granted_qos):
    print("SUBSCRIBED:", userdata, mid, granted_qos)

def on_log(mqttc, userdata, level, string):
    print("LOG", userdata, level, string)

import math
def is_prime(n):
    if n == 1: return False
    for i in range(2,int(math.sqrt(n))+1):
        if (n%i) == 0:
            return False
    return True
    
def main(hostname):
    mqttc = Client(userdata="data (of any type) for user")
    mqttc.enable_logger()

    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    #mqttc.on_log = on_log

    mqttc.connect("simba.fdi.ucm.es")
    mqttc.subscribe('numbers/#')

    mqttc.loop_forever()


if __name__ == '__main__':
    hostname = 'simba.fdi.ucm.es'
    if len(sys.argv)>1:
        hostname = sys.argv[1]
    messages = []
    main(hostname)
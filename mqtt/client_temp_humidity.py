
# Realizado por: Rodrigo de la Nuez Moraleda

from paho.mqtt.client import Client
import sys

def on_connect(mqttc, userdata, flags, rc):
    print("CONNECT:", userdata, flags, rc)

def on_message(mqttc, userdata, msg):
    print("MESSAGE:", userdata, msg.topic, msg.qos, msg.payload, msg.retain)
    if msg.topic == "temperature/t1":
        temperature = float(msg.payload.decode("utf-8"))
        if temperature > K0:
            mqttc.subscribe("humidity/#")
        else:
            mqttc.unsubscribe("humidity/#")
    elif msg.topic == "humidity/#":
        humidity = float(msg.payload.decode("utf-8"))
        if humidity > K1:
            mqttc.unsubscribe("temperature/t1")

def on_publish(mqttc, userdata, mid):
    print("PUBLISH:", userdata, mid)

def on_subscribe(mqttc, userdata, mid, granted_qos):
    print("SUBSCRIBED:", userdata, mid, granted_qos)

def on_log(mqttc, userdata, level, string):
    print("LOG", userdata, level, string)


def main(hostname):
    mqttc = Client(userdata="data (of any type) for user")
    mqttc.enable_logger()

    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.on_log = on_log

    mqttc.connect("simba.fdi.ucm.es")
    mqttc.subscribe('temperature/t1')

    mqttc.loop_forever()

if __name__ == '__main__':
    hostname = 'simba.fdi.ucm.es'
    K0 = 20  # valor límite de temperatura para suscribirse al topic de humedad
    K1 = 50  # valor límite de humedad para dejar de suscribirse al topic de temperatura
    if len(sys.argv)>1:
        hostname = sys.argv[1]
    main(hostname)
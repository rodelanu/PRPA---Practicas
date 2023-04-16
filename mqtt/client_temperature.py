
# Realizado por: Rodrigo de la Nuez Moraleda

from paho.mqtt.client import Client
import sys
import time
import random

def on_connect(mqttc, userdata, flags, rc):
    print("CONNECT:", userdata, flags, rc)

def on_message(mqttc, userdata, msg):
    global startTime, runTime, messages
    print("MESSAGE:", msg.topic, msg.qos, msg.payload, msg.retain)
    subtopic = msg.topic.split("/")[-1]
    value = float(msg.payload.decode("utf-8"))
    if subtopic in subtopics:
        subtopics[subtopic].append(value)
    else:
        subtopics[subtopic] = [value]
        
    messages.append(value)

def total():
    for subtopic in subtopics:
        minimum, maximum, average = get_stats(subtopics[subtopic])
        print(f"Subtopic: {subtopic} - Minimum: {minimum} - Maximum: {maximum} - Average: {average}")
    minimum, maximum, average = get_stats(messages)
    print(f"Recuento total - Minimum: {minimum} - Maximum: {maximum} - Average: {average}")

def on_publish(mqttc, userdata, mid):
    print("PUBLISH:", userdata, mid)

def on_subscribe(mqttc, userdata, mid, granted_qos):
    print("SUBSCRIBED:", userdata, mid, granted_qos)

def on_log(mqttc, userdata, level, string):
    print("LOG", userdata, level, string)

def get_stats(values):
    minimum = min(values)
    maximum = max(values)
    average = sum(values) / len(values)
    return minimum, maximum, average

def main(hostname):
    mqttc = Client(userdata={})
    mqttc.enable_logger()

    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    #mqttc.on_log = on_log

    mqttc.connect(hostname)
    mqttc.subscribe('temperature/#')

    while True:
        mqttc.loop()
        currentTime = time.time()
        if (currentTime - startTime) > runTime:
            break
        
    total()


if __name__ == '__main__':
    hostname = 'simba.fdi.ucm.es'
    if len(sys.argv)>1:
        hostname = sys.argv[1]
    startTime = time.time()
    runTime = random.randint(4, 8)
    messages = []
    subtopics = {}
    main(hostname)
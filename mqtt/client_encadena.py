
# Realizado por: Rodrigo de la Nuez Moraleda

from paho.mqtt.client import Client
import paho.mqtt.publish as publish
import time, sys, math, random

def on_connect(mqttc, userdata, flags, rc):
    print("CONNECT:", userdata, flags, rc)

def temporizador(hostname):
    topic = input('topic? ')
    wait = input('espera? ')
    data  = input('message? ')
    print(f"Publishing {data} in :{topic}:")
    time.sleep(float(wait))
    publish.single(topic,  data, hostname=hostname)

def on_message(mqttc, userdata, msg):
    global startTime, runTime, messages
    print(len(messages), "- MESSAGE:", userdata, msg.topic, msg.qos, msg.payload, msg.retain)
    
    if msg.topic == 'numbers':
        value = float(msg.payload.decode("utf-8"))
        messages.append(value)
        if value.is_integer():
            if is_prime(int(value)):
                mqttc.unsubscribe('numbers/#')
                print("- El número leído es un entero primo.")
                # temporizador(hostname)
                startTime = time.time()
                runTime = random.randint(4, 8)
                mqttc.subscribe('temperature/#')
            else:
                print("- El número leído es un entero NO primo.")
            
        else:
            print("- El número leído es real.")
        integer_frequency = sum(1 for value in messages if value.is_integer())
        float_frequency = sum(1 for value in messages if not value.is_integer())
        print("* Frecuencia de números enteros:", integer_frequency)
        print("* Frecuencia de números reales:", float_frequency)
        
    else:
        subtopic = msg.topic.split("/")[-1]
        value = float(msg.payload.decode("utf-8"))
        if subtopic in subtopics:
            subtopics[subtopic].append(value)
        else:
            subtopics[subtopic] = [value]   
        messages.append(value)
        
        currentTime = time.time()
        if (currentTime - startTime) > runTime:
            total()
            mqttc.unsubscribe('temperature/#')
            # temporizador(hostname)
            mqttc.subscribe('numbers/#')          
    
def total():
    for subtopic in subtopics:
        minimum, maximum, average = get_stats(subtopics[subtopic])
        print(f"Subtopic: {subtopic} - Minimum: {minimum} - Maximum: {maximum} - Average: {average}")
    minimum, maximum, average = get_stats(messages)
    print(f"Recuento total - Minimum: {minimum} - Maximum: {maximum} - Average: {average}")
    
def get_stats(values):
    minimum = min(values)
    maximum = max(values)
    average = sum(values) / len(values)
    return minimum, maximum, average

def on_publish(mqttc, userdata, mid):
    print("PUBLISH:", userdata, mid)

def on_subscribe(mqttc, userdata, mid, granted_qos):
    print("SUBSCRIBED:", userdata, mid, granted_qos)

def on_log(mqttc, userdata, level, string):
    print("LOG", userdata, level, string)

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
    subtopics = {}
    main(hostname)
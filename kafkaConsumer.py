# Código del consumidor

# Librerías
from json import loads
from kafka import KafkaConsumer
from cassandra.cluster import Cluster
import cassandra.auth
from funciones import continentsData, where
from datetime import datetime
import ssl

# Algoritmo

'''
cluster = Cluster()
session= cluster.connect('weather')
'''
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
ssl_context.verify_mode = ssl.CERT_NONE
auth_provider = cassandra.auth.PlainTextAuthProvider(username='climappuser', password='IVuMTDjsjIZZPUeFfgELtPmPWQoPtCk6GkceUD88DMULU2295IikgzibOIyvfdz8Us5mdzJrqXGQACDbPlb4tg==')
cluster = Cluster(['climappuser.cassandra.cosmos.azure.com'], port = '10350', auth_provider=auth_provider,ssl_context=ssl_context)
session = cluster.connect()
continentes=continentsData()
kafka_broker_hostname='localhost'
kafka_consumer_portno='9092'
kafka_broker=kafka_broker_hostname + ':' + kafka_consumer_portno
kafka_topic_input='weather'
# Se define el consumidor que traera los datos del Kafka topic
consumer = KafkaConsumer(kafka_topic_input, value_deserializer=lambda x: loads(x.decode('utf-8')))

# While True, se detiene con ctrl + c
session.execute('USE weather')
#session.execute("INSERT INTO america"+" (id, time,coord, name, country, temp, temp_min, temp_max, pressure, humidity, wind_speed, wind_deg) VALUES (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1);")
while True:
    time = datetime.now()
    print("[",time,"] - CONSUMIENDO DATOS DEL CLIMA...")
    for message in consumer:
        message=message.value
        if(message["cod"] != '404'):
            continente = where(message['name'], continentes)
            if (continente!=False):
                time = datetime.now()
                try:
                    session.execute("INSERT INTO "+ continente +" (id, time,coord, name, country, temp, temp_min, temp_max, pressure, humidity, wind_speed, wind_deg) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (str(message["id"]), str(time),"lon:"+str(message["coord"]["lon"]) + " lat:"+str(message["coord"]["lat"]), message["name"], message["sys"]["country"], str(message["main"]["temp"] -273.15), str(message["main"]["temp_min"] -273.15), str(message["main"]["temp_max"] -273.15), str(message["main"]["pressure"]), str(message["main"]["humidity"]), str(message["wind"]["speed"]), str(message["wind"]["deg"])))
                    
                except Exception as e:
                    time = datetime.now()
                    print("[",time,"] - ERROR AL ACTUALIZAR LA BASE DE DATOS")
        else:
            time = datetime.now()
            print("[",time,"] - " + message['name'] + " response: " + str(message["cod"]))
import serial
import pymysql
import threading
import asyncio
import paho.mqtt.client as mqtt
import json
import time

db_conn = pymysql.connect(host="localhost",user="admin",password="abcd1234", db="sound", port=3306)or die('Could not connect to database')
cursor = db_conn.cursor()
broker_address = "demo.thingsboard.io"
broker_port = 1883
access_token = "YgTyqTJvtypIUQqDcwAp"
mqtt_topic = "v1/devices/me/telemetry"

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(username=access_token)

mqtt_client.connect(broker_address, broker_port)

while True:
    Query = "SELECT sound FROM dbsound ORDER BY id DESC LIMIT 1"
    cursor.execute(Query)
    result = cursor.fetchone()
    sound = result[0]
    payload = {"Sound Level": sound}
    db_conn.commit()
    
    result1 = mqtt_client.publish(mqtt_topic, payload=json.dumps(payload))
    print("Published sound level to ThingsBoard")
    print(sound)

    time.sleep(1)
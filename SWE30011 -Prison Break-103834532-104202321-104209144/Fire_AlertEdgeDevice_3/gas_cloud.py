import serial
import pymysql
import threading
import asyncio
import paho.mqtt.client as mqtt
import json
import time

db_conn = pymysql.connect("localhost", "admin", "", "fire")or die('Could not connect to database')
cursor = db_conn.cursor()
broker_address = "demo.thingsboard.io"
broker_port = 1883
access_token = "B5w5OTDTRwiU65Ypjech"
mqtt_topic = "v1/devices/me/telemetry"

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(username=access_token)

mqtt_client.connect(broker_address, broker_port)

while True:
    Query = "SELECT smoke_level FROM gas ORDER BY id DESC LIMIT 1"
    cursor.execute(Query)
    result = cursor.fetchone()
    smoke = result[0]
    payload = {"Smoke Level": smoke}
    db_conn.commit()
    
    result1 = mqtt_client.publish(mqtt_topic, payload=json.dumps(payload))
    print("Published smoke level to ThingsBoard")
    print(smoke)
    
    query2 = "SELECT MIN(smoke_level), MAX(smoke_level) FROM gas"
    cursor.execute(query2)
    result = cursor.fetchone()
    min_gas = result[0]
    max_gas = result[1]
    
    payload = {
        "Smoke Level": smoke,
        "Min Gas Level": min_gas,
        "Max Gas Level": max_gas
    }
        
    # Publish additional data to ThingsBoard
    mqtt_client.publish(mqtt_topic, payload=json.dumps(payload))
    print("Published data to ThingsBoard:", payload)
    
    db_conn.commit()
    
    

    time.sleep(1)
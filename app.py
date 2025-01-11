import paho.mqtt.client as mqtt
import socket
import time
from flask import Flask, render_template

# Flask setup
app = Flask(__name__)

# MQTT Broker details
BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "iot/gateway/ip"

# Global variable to store the IP address
latest_ip = None

# Function to get the IP address
def get_ip_address():
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception as e:
        print(f"Error retrieving IP address: {e}")
        return None

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        global latest_ip
        latest_ip = get_ip_address()
        if latest_ip:
            print(f"Publishing IP address: {latest_ip}")
            client.publish(TOPIC, latest_ip)
    else:
        print(f"Failed to connect, return code {rc}")

# MQTT on_message callback
def on_message(client, userdata, msg):
    print(f"Message received: {msg.payload.decode()} on topic {msg.topic}")

# MQTT setup and connection
def connect_to_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Retry connection logic
    while True:
        try:
            print("Connecting to MQTT Broker...")
            client.connect(BROKER, PORT)
            client.loop_start()
            break
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    return client

# Flask route to serve the frontend
@app.route("/")
def index():
    return render_template("index.html", ip_address=latest_ip)

if __name__ == "__main__":
    mqtt_client = connect_to_mqtt()
    app.run(host="0.0.0.0", port=5000)
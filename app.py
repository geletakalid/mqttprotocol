import paho.mqtt.client as mqtt
import socket
import time
from flask import Flask, jsonify
from flask_cors import CORS

# Flask Setup
app = Flask(__name__)
CORS(app)

# MQTT Broker Details
BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "iot/gateway/ip"

# Global variable to store the latest IP address
latest_ip = None


# Function to get the IP address assigned to the Raspberry Pi
def get_ip_address():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)  # Get IP assigned by Wi-Fi
        return ip_address
    except Exception as e:
        print(f"Error retrieving IP address: {e}")
        return None


# MQTT Callback for connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        global latest_ip
        latest_ip = get_ip_address()
        if latest_ip:
            print(f"Publishing IP address: {latest_ip}")
            client.publish(TOPIC, latest_ip)  # Publish IP address to MQTT topic
    else:
        print(f"Failed to connect, return code {rc}")


# MQTT Callback for received messages
def on_message(client, userdata, msg):
    print(f"Message received: {msg.payload.decode()} on topic {msg.topic}")


# Function to connect to the MQTT broker
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


# Flask route to serve the frontend with the latest IP address
@app.route('/get_ip', methods=['GET'])
def get_ip():
    if latest_ip:
        return jsonify({'ip_address': latest_ip})  # Return IP address as JSON
    else:
        return jsonify({'error': 'IP address not available'}), 500


if __name__ == "__main__":
    # Start the MQTT connection
    mqtt_client = connect_to_mqtt()

    # Start the Flask app (Running on port 5000)
    app.run(host="0.0.0.0", port=5000)
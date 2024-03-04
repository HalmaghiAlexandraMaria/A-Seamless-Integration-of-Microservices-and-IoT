import time
import random
import paho.mqtt.client as mqtt
from flask import Flask, jsonify
from flask import make_response
import threading
import os

app = Flask(__name__)

mqtt_broker_url = os.environ.get("MQTT_BROKER_URL")
mqtt_broker_port = 8883

sensor_data = {}


def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)


def on_publish(client, userdata, mid, properties=None):
    print("Message published with MID: %s" % mid)


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed to topic: %s with QoS: %s" % (mid, granted_qos))


def on_message(client, userdata, msg):
    global sensor_data
    payload = msg.payload.decode()
    topic_parts = msg.topic.split('/')
    sensor_type = topic_parts[1]
    sensor_id = topic_parts[2]

    sensor_key = f"{sensor_type}/{sensor_id}"
    if sensor_key not in sensor_data:
        sensor_data[sensor_key] = []

    sensor_data[sensor_key].append(payload)
    print(f"Received message: {payload} on topic: {msg.topic}")


client = mqtt.Client(client_id="", userdata=None, protocol=mqtt.MQTTv5)
client.on_connect = on_connect
client.on_message = on_message
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set("alexandra.halmaghi", "AlexandraHalmaghi1") 

try:
    client.connect(mqtt_broker_url, mqtt_broker_port)
except ConnectionRefusedError:
    print("Failed to connect to MQTT broker.")
    time.sleep(5)
    client.connect(mqtt_broker_url, mqtt_broker_port)

mqtt_thread = threading.Thread(target=client.loop_forever, daemon=True)
mqtt_thread.start()

client.subscribe("sensor/+/+", qos=1)


@app.errorhandler(404)
def page_not_found(error):
    return jsonify({"error": "Page not found"}), 404


@app.route('/sensor-data/<sensor_type>/<sensor_id>', methods=['GET'])
def get_sensor_data(sensor_type, sensor_id):
    sensor_key = f"{sensor_type}/{sensor_id}"
    if sensor_key in sensor_data:
        latest_data = sensor_data[sensor_key][-1]
        return jsonify({sensor_key: latest_data})
    return jsonify({"error": "Sensor data not available"}), 404


def sensor_simulator():
    while True:
        # Simulate proximity sensor data
        proximity_distance = random.randint(1, 100)  # Example distance in cm
        proximity_payload = f"Distance: {proximity_distance} cm, Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
        client.publish("sensor/proximity/1", proximity_payload, qos=1)

        # Simulate IR sensor data
        ir_detection = random.choice(['Detected', 'Not Detected'])
        ir_payload = f"Detection: {ir_detection}, Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
        client.publish("sensor/ir/1", ir_payload, qos=1)

        time.sleep(15)


if __name__ == '__main__':
    sensor_simulator_thread = threading.Thread(target=sensor_simulator, daemon=True)
    sensor_simulator_thread.start()
    app.run(debug=True, port=5000, host='0.0.0.0')

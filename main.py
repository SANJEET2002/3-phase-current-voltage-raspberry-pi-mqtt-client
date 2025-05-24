import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

# === MQTT Config ===
MQTT_BROKER = "35.154.183.245"
MQTT_PORT = 1883
MQTT_COMMAND_TOPIC = "67b8a4d9df51108502049083-commands"
MQTT_STATUS_TOPIC = "67b8a4d9df51108502049083-status"

# relay pin 
PIN = 12
LED_PIN  = 10

client = None

def setupPins():
    # === GPIO Setup ===
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN, GPIO.OUT)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(PIN, GPIO.LOW)
    GPIO.output(LED_PIN, GPIO.LOW)

# === MQTT Callback Handlers ===
def on_connect(client, userdata, flags, rc):
    GPIO.output(LED_PIN, GPIO.HIGH)
    print("Connected to MQTT Broker with code:", rc)
    client.subscribe(MQTT_COMMAND_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received message on {msg.topic}: {payload}")

    if msg.topic != MQTT_COMMAND_TOPIC:
        return
    
    if payload.lower() == "on":
        GPIO.output(PIN, GPIO.HIGH)
        print("Pin set to HIGH (ON)")
        client.publish(MQTT_STATUS_TOPIC, "ON")
    elif payload.lower() == "off":
        GPIO.output(PIN, GPIO.LOW)
        print("Pin set to LOW (OFF)")
        client.publish(MQTT_STATUS_TOPIC, "OFF")
    elif payload.lower() == "status":
        print("status-requested")
        current_status = GPIO.input(PIN)
        print(f"current status - {current_status}")
        if current_status == 1:
            client.publish(MQTT_STATUS_TOPIC,"ON")
        elif current_status == 0:
            client.publish(MQTT_STATUS_TOPIC,"OFF")


def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT Broker with result code:", rc)
    if rc != 0:
        print("Unexpected disconnection. Trying to reconnect...")
        try:
            client.reconnect()
        except Exception as e:
            print("Reconnection failed:", str(e))
    GPIO.output(LED_PIN,GPIO.LOW)

def startMqttClient():
    # === MQTT Client Setup ===
    client = mqtt.Client("RPiClient")
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()


while True:
    try:
        GPIO.cleanup()
        setupPins()
        startMqttClient()

    except Exception as e:
        print("Cleaning up GPIO and exiting...")
        GPIO.cleanup()
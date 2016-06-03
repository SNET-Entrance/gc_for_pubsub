import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe(("test/topic", 2))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+": "+str(msg.payload) + " with QoS: " + str(msg.qos))

def on_log(client, userdata, level, buf):
    print("log: " + str(level) + ": " + str(buf));

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_log = on_log

#ssh -N al@me -L 1883/localhost/1883
client.connect("me", 1883, 360)
#client.connect("localhost", 1883, 360)

client.loop_start();
for i in range(0,10):
    client.publish("test/topic", "test: " + str(i), 2);

client.loop_stop();
client.disconnect();

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on 12.06.2015

@author: al
'''
import paho.mqtt.client as mqtt
from charm.toolbox.pairinggroup import PairingGroup
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.core.engine.util import objectToBytes,bytesToObject

class Subscriber(object):
    __client = None
    '''Client:'''
    topic="test/topic"
    '''str: topic'''    
    dek = None
    '''str: the aes-key'''
    
    def __init__(self, cfg):
        self.__client = mqtt.Client()
        self.__client.on_connect = self.on_connect
        self.__client.on_message = self.on_message
        self.__client.on_log = self.on_log
        
        #ssh -N al@me -L 1883/localhost/1883
        self.__client.connect(cfg['host'], int(cfg['port']), int(cfg['keepalive']))
        #client.connect("localhost", 1883, 360)
        if "topic" in cfg:
            self.topic=cfg['topic']
        if "dek" in cfg:
            self.dek=cfg['dek']

    def loop(self):        
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        self.__client.loop_forever()        
        
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        print("subscribing to: " + self.topic)
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe((self.topic, 2))

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        CT = None
        try:
            groupObj = PairingGroup('SS512')
            CT = bytesToObject(msg.payload, groupObj)
        except:
            print(msg.topic+": "+ msg.payload.decode("utf-8") + " with QoS: " + str(msg.qos))
        
        if self.dek is not None and CT is not None:
            m = self.decAes(CT)
            if msg is None:
                print(msg.topic+": (dec failed!), with QoS: " + str(msg.qos))
            else:
                print(msg.topic+": (dec) "+ m.decode('utf-8') + " with QoS: " + str(msg.qos))
            
    def decAes(self, CT):
        if self.dek is None:
            raise Exception('DEK is null, cannot decrypt')
        
        
        a = AuthenticatedCryptoAbstraction(bytes(self.dek, "utf-8"))
        #CT_AES = a.encrypt(message)
        return a.decrypt(CT)

    def on_log(self, client, userdata, level, buf):
        print("log: " + str(level) + ": " + str(buf));

if __name__ == '__main__':
    import sys, os
    
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))    
    from model.config import Config
    
    groupCfg = Config('../conf/gc_config.ini')
    
    sub = Subscriber(groupCfg.getConfig("mqtt_client"))
    sub.loop()

#    client = mqtt.Client()
#    client.on_connect = on_connect
#    client.on_message = on_message
#    client.on_log = on_log
    
    #ssh -N al@me -L 1883/localhost/1883
#    client.connect(cfg['host'], int(cfg['port']), int(cfg['keepalive']))
    #client.connect("localhost", 1883, 360)
    
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
#    client.loop_forever()
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
    _client = None
    '''Client:'''
    topic="test/topic"
    '''str: topic'''
    dek = None
    '''str: the aes-key'''

    def __init__(self, cfg):
        if "client_id" in cfg:
            self._client = mqtt.Client(client_id=str(cfg['client_id']), clean_session=False)
        else:
            self._client = mqtt.Client()
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._client.on_log = self.on_log
        
        #ssh -N al@me -L 1883/localhost/1883
        self._client.connect(host=cfg['host'], port=int(cfg['port']), keepalive=int(cfg['keepalive']))
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
        self._client.loop_forever()    
                    
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

class Publisher(Subscriber):
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
    
    def loop(self):
        self._client.loop_start();

    def publish(self, m):
        if self.dek is not None:
            CT = self.encAES(m)
            self._client.publish(self.topic, CT.decode("utf-8"), 2);
        else:
            self._client.publish(self.topic, m, 2);

    def encAES(self, m):
        if self.dek is None:
            raise Exception('DEK is null, cannot encrypt')

        a = AuthenticatedCryptoAbstraction(bytes(self.dek, "utf-8"))
        CT_AES = a.encrypt(m)
        groupObj = PairingGroup('SS512')

        return objectToBytes(CT_AES, groupObj)

    def loop_end(self):
        self._client.loop_stop();
        self._client.disconnect();
            
                                
if __name__ == '__main__':
    import sys, os

    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
    from model.config import Config

    groupCfg = Config('../conf/gc_config.ini')
    cfg = groupCfg.getConfig("mqtt_client")
    cfg['topic'] = "test/topic"
    pub = Publisher(cfg)
    pub.loop();
    pub.publish("dude");
    pub.loop_end()


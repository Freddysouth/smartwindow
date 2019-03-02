'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json

class MQTTClient:

    myAWSIoTMQTTClient = None

    def __init__(self, clientId, topic, host, rootCA, crtPath, privateKey, port):
        self.clientId = clientId
        self.topic = topic
        self.host = host
        self.rootCA = rootCA
        self.crtPath = crtPath
        self.privateKey = privateKey
        self.port = port

    # Custom MQTT message callback
    def customCallback(client, userdata, message):
        print("Received a new message: ")
        print(message.payload)
        print("from topic: ")
        print(message.topic)
        print("--------------\n\n")

    def ConfigureLogging(): 
        logger = logging.getLogger("AWSIoTPythonSDK.core")
        logger.setLevel(logging.DEBUG)
        streamHandler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamHandler.setFormatter(formatter)
        logger.addHandler(streamHandler)

    def InitClient(self):
        self.myAWSIoTMQTTClient = AWSIoTMQTTClient(self.clientId)
        self.myAWSIoTMQTTClient.configureEndpoint(self.host, self.port)
        self.myAWSIoTMQTTClient.configureCredentials(self.rootCA, self.privateKey, self.crtPath)
        
        # AWSIoTMQTTClient connection configuration
        self.myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        self.myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        self.myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
        
        # Connect and subscribe to AWS IoT
        self.myAWSIoTMQTTClient.connect()
        time.sleep(2)

    def PublishJsonPayload(self, payload):
        self.myAWSIoTMQTTClient.publish(self.topic, payload, 1)
        print('Published topic %s: %s\n' % (self.topic, payload))

    def StartPublish(self):
        # Publish to the same topic in a loop forever
        loopCount = 0
        while True:
            message = {}
            message['device'] = "window_lars"
            message['timestamp'] = str(int(round(time.time() * 1000)))
            message['aq'] = "2"
            messageJson = json.dumps(message)
            self.myAWSIoTMQTTClient.publish(self.topic, messageJson, 1)
            
            print('Published topic %s: %s\n' % (self.topic, messageJson))
            loopCount += 1
            time.sleep(1)

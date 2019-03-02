
from MQTTAQClient import MQTTClient
from aqi import AQIClient

import json, time, sys, struct, serial


 #host = "ad50nqq2ecfo9-ats.iot.us-west-2.amazonaws.com"
#rootCAPath = "../../aws-resources/root-CA.crt"
#certificatePath = "../../aws-resources/RaspPi.cert.pem"
#privateKeyPath = "../../aws-resources/RaspPi.private.key"
#port = 8883
#clientId = "RaspberryPi"
#topic = "pi/measurements/aq"

def main():
	mqtt_client = MQTTClient(
		"RaspberryPi", 
		"pi/measurements/aq",
		"ad50nqq2ecfo9-ats.iot.us-west-2.amazonaws.com",
		"../../aws-resources/root-CA.crt",
		"../../aws-resources/RaspPi.cert.pem",
		"../../aws-resources/RaspPi.private.key",
		8883
		)

	mqtt_client.InitClient()
	#mqtt_client.StartPublish()

	aqi_client = AQIClient(mqtt_client)


	while True:
		aqi_client.cmd_set_sleep(0)
		aqi_client.cmd_set_mode(1)
		for t in range(15):
			values = aqi_client.cmd_query_data()
			if values is not None:
				print("PM2.5: ", values[0], ", PM10: ", values[1])
				time.sleep(2)
		
		# open stored data
		with open('/var/www/html/aqi.json') as json_data:
			data = json.load(json_data)
		
		# check if length is more than 100 and delete first element
		if len(data) > 100:
			data.pop(0)

		# append new values
		data.append({'pm25': values[0], 'pm10': values[1], 'time': time.strftime("%d.%m.%Y %H:%M:%S")})

		# save it
		with open('/var/www/html/aqi.json', 'w') as outfile:
			json.dump(data, outfile)

		print("Going to sleep for 1 sec...")
		aqi_client.cmd_set_mode(0)
		aqi_client.cmd_set_sleep()
		time.sleep(1)

if __name__ == "__main__":
	main()
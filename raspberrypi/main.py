
from MQTTAQClient import MQTTClient
from aqi import AQIClient #comment out if debug mode
from Aggregator import Aggregator

import json, time, sys, struct, socket, fcntl

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def main():

	debug = False
	debug_data = []
	data = []

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

	aqi_client = None
	if not debug:
		aqi_client = AQIClient()

	aggregator = Aggregator()

	while True:

		if debug == True:
			debug_data.append({"pm25": 2, "pm10": 2, "timestamp": str(int(time.time() * 1000))})
			if len(debug_data) > 5:
				aggregate = aggregator.get_mean(debug_data)
				aggregate_json = json.dumps(aggregate)

				mqtt_client.PublishJsonPayload(aggregate_json)
				
				debug_data.clear()

			time.sleep(1)
		else:

			print("Start...")

			aqi_client.cmd_set_sleep(0)
			aqi_client.cmd_set_mode(1)

			#for t in range(5):
			#	print("####for t in range(15)####")
			#	values = aqi_client.cmd_query_data()
			#	if values is not None:
			#		print("PM2.5: ", values[0], ", PM10: ", values[1])
			#		time.sleep(1)
			#print("####Done with for t in range(15)####")
			# open stored data
			#with open('/var/www/html/aqi.json') as json_data:
			#	data = json.load(json_data)
			#print("####open data####")
			#print(data)

			
			if len(data) > 10:
				print("Aggregating and publishing packet...")
				aggregate = aggregator.get_mean(data)
				payload = {
					"device": "window_lars",
					"device_ip": get_ip_address("wlan0"),
					"pm25": aggregate["pm25"],
					"pm10": aggregate["pm10"],
					"timestamp": aggregate["timestamp"]
				}
				payload_json = json.dumps(payload)

				mqtt_client.PublishJsonPayload(payload_json)
				
				data.clear()

			print("Appending values...")
			# append new values
			values = aqi_client.cmd_query_data()
			if values is not None:
				data.append({'pm25': values[0], 'pm10': values[1], 'timestamp': time.strftime("%d.%m.%Y %H:%M:%S")})

			# save it
			#with open('/var/www/html/aqi.json', 'w') as outfile:
			#	json.dump(data, outfile)


			print("Going to sleep for 1 sec...")
			aqi_client.cmd_set_mode(0)
			aqi_client.cmd_set_sleep()
			time.sleep(1)

if __name__ == "__main__":
	main()
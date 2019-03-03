
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

			print("####Starting####")
			aqi_client.cmd_set_sleep(0)
			aqi_client.cmd_set_mode(1)

			for t in range(15):
				print("####for t in range(15)####")
				values = aqi_client.cmd_query_data()
				if values is not None:
					print("PM2.5: ", values[0], ", PM10: ", values[1])
					time.sleep(2)
			print("####Done with for t in range(15)####")
			# open stored data
			with open('/var/www/html/aqi.json') as json_data:
				data = json.load(json_data)
			print("####open data####")
			print(data)

			# check if length is more than 100 and delete first element
			if len(data) > 2:
				print("####Starting publishing process####")
				aggregate = aggregator.get_mean(data)
				prepend = {
					"device": "window_lars",
					"device_ip": get_ip_address("wlan0")
					"pm25": aggregate["pm25"],
					"pm10": aggregate["pm10"],
					"timestamp": aggregate["timestamp"]
				}
				payload = json.dumps(prepend)

				mqtt_client.PublishJsonPayload(payload)
				
				data.clear()


			print("####appending values####")
			# append new values
			data.append({'pm25': values[0], 'pm10': values[1], 'time': time.strftime("%d.%m.%Y %H:%M:%S")})

			# save it
			with open('/var/www/html/aqi.json', 'w') as outfile:
				json.dump(data, outfile)

			print("####just wrote file####")

			print("Going to sleep for 5 sec...")
			aqi_client.cmd_set_mode(0)
			aqi_client.cmd_set_sleep()
			time.sleep(5)

if __name__ == "__main__":
	main()
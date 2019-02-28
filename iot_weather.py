# importing the requests library 
import requests
import json
import pprint

#Get 7-day forcast
response = requests.get("https://weather.cit.api.here.com/weather/1.0/report.json?product=forecast_7days&zipcode=10025&oneobservation=true&app_id=Is7EbpLYqp7H4EUwNyMz&app_code=sdwekigD9nSSWlQBa0pZ3g")
data = response.json()
dumpet = json.dumps(data)

pp = pprint.PrettyPrinter(indent=2)
#pp.pprint(data)

dict1 = data.get("forecasts")
dict2 = dict1.get("forecastLocation")
list1 = dict2.get("forecast")
pp.pprint(list1)

	#print(day["temperature"])

	#weekday
	#localTime
	#rainFall
	#humidity
	#temperature
	#skydescription?
	#temperatureDesc?
	#windSpeed?



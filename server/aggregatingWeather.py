# importing the requests library 
import requests
import json
import pprint
from collections import defaultdict
d = defaultdict(list)

#Get 7-day forcast
response = requests.get("https://weather.cit.api.here.com/weather/1.0/report.json?product=forecast_7days_simple&zipcode=10025&oneobservation=true&app_id=Is7EbpLYqp7H4EUwNyMz&app_code=sdwekigD9nSSWlQBa0pZ3g")
data = response.json()


pp = pprint.PrettyPrinter(indent=2)
#pp.pprint(data)

dict1 = data.get("forecasts")
dict2 = dict1.get("forecastLocation")
list1 = dict2.get("forecast")
#pp.pprint(list1)

#Empty dictionary with keys 1-7
d = {}
newDMean = {}
for i in range(1,8):
	d[i] = {};
	newDMean[i] = {};

keys = ["temperature", "humidity", "rainFall", "windSpeed"]
def makeDict():
	for key in keys:
		for fields in list1:
			if(fields[key] != "*"):
				d[int(fields["dayOfWeek"])].setdefault(key, []).append(fields[key])
			else:
				d[int(fields["dayOfWeek"])].setdefault(key, []).append('0')
def getMean():
	for key in keys:

		for i in range(1,8):
			theSum = 0;
			for number in d[i][key]:
				theSum += float(number);
			avg = theSum/len(d[i][key]);
			if (key=="temperature"):
				fahrenheit = 9/5 * avg + 32;
				newDMean[i].setdefault(key,fahrenheit);
			else:
				newDMean[i].setdefault(key,avg);
makeDict()
getMean()

###backup
def makeDict(keys, weatherList):
	d, out = {}, {}
	for i in range(1,8): d[i], out[i] = {}, {}

	for key in keys:
		for section in weatherList:
			if(section[key] != "*"):
				d[int(section["dayOfWeek"])].setdefault(key, []).append(section[key]);
			else:
				d[int(section["dayOfWeek"])].setdefault(key, []).append('0');
	return meaned(out, d, keys)

def meaned(out, d, keys):
	for key in keys:
		for i in range(1,8):
			theSum = 0;
			for number in d[i][key]:
				theSum += float(number);
			avg = theSum/len(d[i][key]);
			if (key=="temperature"):
				fahrenheit = 9/5 * avg + 32;
				out[i].setdefault(key,fahrenheit);
			else:
				out[i].setdefault(key,avg);
	return out

pp.pprint(d);
pp.pprint(newDMean);

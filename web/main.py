import flask
import requests
import json

import numpy as np

from pandas import read_csv
from pandas import DataFrame
from pandas import concat

import keras.models

from LSTMForecaster import LSTMForecaster
import datetime

app = flask.Flask(__name__)

predictorPM2_5 = None
predictorPM10 = None

DATAFORMATPM2_5 = ['date', 'PM2.5', 'Humidity', 'Windspeed', 'Temperature', 'Precipitation']
DATAFORMATPM10 = ['date', 'PM10', 'Humidity', 'Windspeed', 'Temperature', 'Precipitation']
UNPREDICTED_COLS = [0,7,8,9,10,11]

PM2_5_LOW_POLLUTION_TRESHHOLD = 12
PM2_5_MEDIUM_POLLUTION_TRESHHOLD = 35.4

PM10_LOW_POLLUTION_TRESHHOLD = 50
PM10_MEDIUM_POLLUTION_TRESHHOLD = 100

def toFarenheit(c):
	return 9/5 * c + 32;

#makes a 7day, 2d list of weather parameters: keys
def makeListOfWeatherParams(keys, weatherForecast):
	weekParams = []
	for day in weatherForecast:
		dayParams = []
		for key in keys:
			value = 0
			if key == 'highTemperature':
				avgTemp = (float(day['highTemperature']) + float(day['lowTemperature']))/2
				value = toFarenheit(avgTemp)
			else:
				value = day[key] if day[key] != '*' else 0
			dayParams.append(float(value))
		weekParams.append(dayParams)
	return weekParams


def prepareResponse(predictedPollution, pollutionType):
	lowTreshold = PM2_5_LOW_POLLUTION_TRESHHOLD if pollutionType == "PM2_5" else PM10_LOW_POLLUTION_TRESHHOLD
	mediumTreshold = PM2_5_MEDIUM_POLLUTION_TRESHHOLD if pollutionType == "PM2_5" else PM10_MEDIUM_POLLUTION_TRESHHOLD
	
	response = {"predictedPollution": predictedPollution}
	descriptions = []
	for value in predictedPollution:
		if (value <= lowTreshold):
			descriptions.append(0)
		elif (value <= mediumTreshold):
			descriptions.append(1)
		else:
			descriptions.append(2)
	response["descriptions"] = descriptions
	return response

def getWeather():
	response = requests.get("https://weather.cit.api.here.com/weather/1.0/report.json?product=forecast_7days_simple&zipcode=93117&oneobservation=true&app_id=Is7EbpLYqp7H4EUwNyMz&app_code=sdwekigD9nSSWlQBa0pZ3g")
	data = response.json()

	weatherForecast = data["dailyForecasts"]["forecastLocation"]["forecast"]
	weatherParams = makeListOfWeatherParams(["humidity", "windSpeed", "highTemperature", "rainFall", "dayOfWeek"], weatherForecast)
	print(weatherParams)
	return weatherParams

def prepareWeekdayList(startDay, steps):
	dayList = []
	days = [1, 2, 3, 4, 5, 6, 7]
	for i in range(steps):
		dayList.append(days[((startDay - 1) + i) % 7])
	return dayList

#Make an estimate, based on the previous day's weather, and the previous weekday pollution
def estimateMeanData(lastSevenDays, dayIndex):
	pollution = lastSevenDays[0][0]
	weather = lastSevenDays[6][1: 6]
	newValues = [pollution] + weather
	nextDay = dayIndex + datetime.timedelta(days=1)
	return nextDay, newValues

def fillMissingDates(indexes, values):
	dateFormat = "%Y-%m-%d"
	counter = 1
	newIndexes, newValuesList = indexes, values

	while counter < len(newIndexes):
		delta = datetime.datetime.strptime(newIndexes[counter], dateFormat) - datetime.datetime.strptime(newIndexes[counter - 1], dateFormat)
		if delta.days > 1:
			newIndex, newValues = estimateMeanData(newValuesList[counter - 7: counter], datetime.datetime.strptime(indexes[counter - 1], dateFormat))
			newIndexes.insert(counter, newIndex.strftime(dateFormat))
			newValuesList.insert(counter, newValues)
		else:
			counter += 1
	return newIndexes, newValuesList
	
def prepareData(filePath, dataFormat):
	dataset = read_csv(filePath, header=0, index_col=0, usecols=dataFormat)
	cols = dataset.columns.tolist()
	cols = [cols[-1]] + cols[:-1]
	dataset = dataset[cols]

	newIndexes, newValues = fillMissingDates(dataset.index.tolist(), dataset.values.tolist())
	weeklist = prepareWeekdayList(2, len(newValues))
	for i in range(len(newValues)):
		newValues[i].append(weeklist[i])
	return np.asarray(newValues)

# endpoints
@app.route("/predict/<pollutionType>", methods=["GET"])
def predict(pollutionType):
	predictor = predictorPM2_5 if pollutionType == "PM2_5" else predictorPM10
	
	forecastedWeather = getWeather()
	predictedPollution = predictor.predict(forecastedWeather)
	response = prepareResponse(predictedPollution.tolist(), pollutionType)
	return flask.jsonify(response)
	
@app.route("/", methods=["GET"])
def home():
	return flask.render_template('index.html')

def main():
	global predictorPM2_5, predictorPM10

	print(("* Loading Keras model and Flask starting server..."
	  "please wait until server has fully started"))
	
	dataPM2_5 = prepareData('trainingData/training_PM2_5.csv', DATAFORMATPM2_5)
	dataPM10 = prepareData('trainingData/training_PM10.csv', DATAFORMATPM10)

	predictorPM2_5 = LSTMForecaster(dataPM2_5)
	predictorPM2_5.init('models/model_PM2_5.h5', UNPREDICTED_COLS, True)
	#predictorPM2_5.csvResults('PM2_5_graph_data.csv')

	predictorPM10 = LSTMForecaster(dataPM10)
	predictorPM10.init('models/model_PM10.h5', UNPREDICTED_COLS, True)
	#predictorPM10.csvResults('PM10_graph_data.csv')

	app.run()

if __name__ == "__main__":
	main()



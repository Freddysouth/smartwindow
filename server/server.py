from keras.applications import ResNet50
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
import keras.models
from PIL import Image
import numpy as np
import flask
import io
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
import requests
import json

from LSTMForecast import LSTMForecast


app = flask.Flask(__name__)
model = None


def load_model():
		# load the pre-trained Keras model (here we are using a model
		# pre-trained on ImageNet and provided by Keras, but you can
		# substitute in your own networks just as easily)
		global model
		model = keras.models.load_model("model.h5")


def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
	n_vars = 1 if type(data) is list else data.shape[1]
	df = DataFrame(data)
	cols, names = list(), list()
	# input sequence (t-n, ... t-1)
	for i in range(n_in, 0, -1):
		cols.append(df.shift(i))
		names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
	# forecast sequence (t, t+1, ... t+n)
	for i in range(0, n_out):
		cols.append(df.shift(-i))
		if i == 0:
			names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
		else:
			names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
	# put it all together
	agg = concat(cols, axis=1)
	agg.columns = names
	# drop rows with NaN values
	if dropnan:
		agg.dropna(inplace=True)
	return agg
 


def getWeather():
	response = requests.get("https://weather.cit.api.here.com/weather/1.0/report.json?product=forecast_7days&zipcode=10025&oneobservation=true&app_id=Is7EbpLYqp7H4EUwNyMz&app_code=sdwekigD9nSSWlQBa0pZ3g")
	data = response.json()
	return json.dumps(data)

@app.route("/predict", methods=["POST"])
def predict():
	pass

if __name__ == "__main__":
		print(("* Loading Keras model and Flask starting server..."
				"please wait until server has fully started"))
		dataset = read_csv('pollution.csv', header=0, index_col=0)
	predictor = LSTMForecast(dataset.values)
	predictor.init(True, 'models/model.h5', [4], [9,10,11,12,13,14,15])

		app.run()

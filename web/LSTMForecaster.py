import os
from math import sqrt
import numpy as np

from pandas import read_csv
from pandas import DataFrame
from pandas import concat

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error

import keras.models
from keras.layers import Dense
from keras.layers import LSTM

class LSTMForecaster:

	def __init__(self, values):
		self.values = values
		self.train = []
		self.test = []
		self.trainInput = []
		self.trainOutput = []
		self.testInput = []
		self.testOutput = []
		self.model = None
		self.history = None
		# fit scaler, and normalize input values
		self.originalValues = self.values
		self.scaler = MinMaxScaler(feature_range=(0, 1))
		self.scaler = self.scaler.fit(values)
		self.values = self.values.astype('float32')
		self.values = self.scaler.transform(self.values)
		

	# convert series to supervised learning
	def seriesToSupervised(self, n_in=1, n_out=1, dropnan=True):
		n_vars = 1 if type(self.values) is list else self.values.shape[1]
		df = DataFrame(self.values)
		cols, names = list(), list()
		
		shiftInput = 0
		cols.append(df.shift(shiftInput))
		names += [('var%d(t-%d)' % (j, shiftInput)) for j in range(n_vars)]
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

	def dropColumns(self, columnIndexes):
		reframed = self.seriesToSupervised(1, 1)
		reframed.drop(reframed.columns[columnIndexes], axis=1, inplace=True)
		self.values = reframed.values

	def splitTrainTestSets(self, trainRatio):
		self.train = self.values[:int(len(self.values) * trainRatio), :]
		self.test = self.values[int(len(self.values)* trainRatio):, :]

	def splitInputOutput(self):
		self.trainInput, self.trainOutput = self.train[:, :-1], self.train[:, -1]
		self.testInput, self.testOutput = self.test[:, :-1], self.test[:, -1]

	def reshapeTrainTestInputSetsTo3d(self):
		self.trainInput = self.trainInput.reshape((self.trainInput.shape[0], 1, self.trainInput.shape[1]))
		self.testInput = self.testInput.reshape((self.testInput.shape[0], 1, self.testInput.shape[1]))

	# helper functions for prediction
	def reshapePredictionInputTo3d(self, predictionInput):
		return predictionInput.reshape((predictionInput.shape[0], 1, predictionInput.shape[1]))

	def getNormalizedPrediction(self, predictionInput):
		predictionInput = predictionInput.reshape((predictionInput.shape[0], 1, predictionInput.shape[1]))
		return self.model.predict(predictionInput)
		
	def getActualPrediction(self, predictionInput, prediction):
		actualizedPrediction = np.concatenate((prediction, predictionInput), axis=1)
		actualizedPrediction = self.scaler.inverse_transform(actualizedPrediction)
		return actualizedPrediction

	# predicts pollution based on inputData: [[humidity, windspeed, avg_temp, precipitation]]
	def predict(self, inputData):
		prepend = np.zeros((len(inputData), 1))
		inputData = np.concatenate((prepend, inputData), axis=1)
		
		scaled = self.scaler.transform(inputData)
		scaled = scaled[:, 1:]

		normalizedPrediction = self.getNormalizedPrediction(scaled)
		actualPrediction = self.getActualPrediction(scaled, normalizedPrediction)

		return actualPrediction[:, 0]

	def saveModel(self, filePath):
		self.model.save(filePath)

	def initModel(self):
		self.model = keras.models.Sequential()
		self.model.add(LSTM(50, input_shape=(self.trainInput.shape[1], self.trainInput.shape[2])))
		self.model.add(Dense(1))
		self.model.compile(loss='mae', optimizer='adam')

	def fitModel(self, filePath):
		self.history = self.model.fit(self.trainInput, self.trainOutput, epochs=100, batch_size=72, validation_data=(self.testInput, self.testOutput), verbose=2, shuffle=False)
		self.saveModel(filePath)
		self.model._make_predict_function()

	def trainModel(self, filePath, columnsToDrop):
		self.dropColumns(columnsToDrop)
		# split dataset into train and test sets
		self.splitTrainTestSets(0.9)
		# split train and test sets to representative inputs and outputs
		self.splitInputOutput()
		self.reshapeTrainTestInputSetsTo3d()
		# prepare, fit, and save model
		self.initModel()
		self.fitModel(filePath)

	def init(self, filePath, columnsToDrop, train):
		if train:
			self.trainModel(filePath, columnsToDrop)
		else:
			if os.path.exists(filePath):
				self.model = keras.models.load_model(filePath)
				self.model._make_predict_function()
			else:
				self.trainModel(filePath, columnsToDrop)

	def csvResults(self, filePath):

		inputs = self.values[:, :-1]
		inputShaped = inputs.reshape((inputs.shape[0], 1, inputs.shape[1]))
		predictions = self.model.predict(inputShaped)
		
		predictionsResult = np.concatenate((predictions, inputs), axis=1)
		invertedResults = self.scaler.inverse_transform(predictionsResult)

		labels = self.originalValues[:, 0].tolist()
		predictions = invertedResults[:, 0].tolist()

		results = {"predictions": predictions, "labels": labels}
		print(results)
		r =DataFrame.from_dict(results)
		r.to_csv(filePath, index=False)



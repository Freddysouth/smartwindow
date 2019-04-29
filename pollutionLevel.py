class Pollution:

	@staticmethod
	def getPollutionLevel(input):
		dict = {}
		dict["pollutionValue"] = input;

		list = [];
		for i in input:
			if (i <= 12):
				list.append("low")
			elif (i >12 and i <= 35.4):
				list.append("medium")
			else:
				list.append("high")
		dict["pollutionLevel"] = list
		return dict
import numpy 

#sample_data = [
#    {"pm2.5" : 1, "pm10" : 2, "timestamp" : "s"},
#    {"pm2.5" : 2, "pm10" : 4, "timestamp" : "s"},
#    {"pm2.5" : 3, "pm10" : 2, "timestamp" : "s"},
#    {"pm2.5" : 2, "pm10" : 4, "timestamp" : "last"}
#]

class Aggregator :
    input = []

    def get_mean (self, data):
        
        pm2 = numpy.mean(list(map(lambda d: d["pm25"], data)))
        pm10 = numpy.mean(list(map(lambda d: d["pm10"], data)))
        
        return {"pm25" : pm2, "pm10" : pm10, "timestamp" : data[-1].get("timestamp")}

    def append (self, data):
        input.append(data)

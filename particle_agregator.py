import numpy 
#format {pm2.5, pm10, timestamp}

sample_data = [
    {"pm2.5" : 1, "pm10" : 2, "timestamp" : "s"},
    {"pm2.5" : 2, "pm10" : 4, "timestamp" : "s"},
    {"pm2.5" : 3, "pm10" : 2, "timestamp" : "s"},
    {"pm2.5" : 2, "pm10" : 4, "timestamp" : "last"}
]

class Aggregator :
    input = []


    def get_mean (self, data):
        #pm2_list = []
        #pm10_list = []
        #for entry in data:
            #pm2_list.append(entry.get("pm2.5"))
            #pm10_list.append(entry.get("pm10"))
            
        #pm2 = numpy.mean(pm2_list)
        #pm10 = numpy.mean(pm10_list)

        pm2 = numpy.mean(list(map(lambda d: d["pm2.5"], data)))
        pm10 = numpy.mean(list(map(lambda d: d["pm10"], data)))
        #pm10 = numpy.mean(d['pm10'] for d in data)
        return {"pm2.5" : pm2, "pm10" : pm10, "timestamp" : data[-1].get("timestamp")}

    def append (self, data):
        input.append(data)

#print (d['pm2.5'] for d in sample_data)
print(map(lambda d: d["pm2.5"], sample_data))
a = Aggregator()
print(a.get_mean(sample_data))
    

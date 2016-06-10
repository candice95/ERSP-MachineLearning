#!/usr/bin/python

import gzip
import json
import re
import matplotlib.pyplot as plt

postcodeDict = {}
with gzip.open('./CA_5CoreBusinesses.json.gz','rb') as infile:
	for line in infile:
		bus_obj = json.loads(line)
		address = bus_obj["address"]
		for eachString in address:
			postCode = re.findall(r"CA \d{5}", eachString)
			if postCode:
				if postCode[0][3:] in postcodeDict:
					postcodeDict[postCode[0][3:]].append(bus_obj)
				else:
					postcodeDict[postCode[0][3:]] = []
					postcodeDict[postCode[0][3:]].append(bus_obj)
result = {}
i = 0
for each in postcodeDict:
	if len(postcodeDict[each]) < 5:
		for bus in postcodeDict[each]:
			info = {}
			info['busId'] = bus["id"]
			info['cluster'] = 0
			info['gps'] = bus["gps"]
			result[bus["id"]] = info
	else:
		i += 1 
		for bus in postcodeDict[each]:
			info = {}
			info['busId'] = bus["id"]
			info['cluster'] = i
			info['gps'] = bus["gps"]
			result[bus["id"]] = info
print i
with gzip.open('postcodeCluster.json.gz', 'wb') as f_out:
	for each in result:
		json.dump(result[each],f_out)
		f_out.write("\n")

x = []
y = []
for each in result:
	gps = result[each]['gps']
	if gps[0] > 180 or gps[0] < -180 or gps[1] > 180 or gps[1] < -180:
		continue
	else:
		x.append(gps[0])
		y.append(gps[1])
# visualize
'''h = 0.2
x_min = x[:, 0].min() - 1
x_max = x[:, 0].max() + 1
y_min = y[:, 0].min() - 1
y_max = y[:, 0].max() + 1
plt.plot(x, y)
plt.show()'''

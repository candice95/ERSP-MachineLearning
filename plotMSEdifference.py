#!/usr/bin/python
import matplotlib.pyplot as plt
import numpy as np

x1 = []
y1 = []
x2 = []
y2 = []
x = []
y = []
with open('./freq_mseWithCluster') as fin1:
	for line in fin1:
		parts = line.split(":",1)
		x1.append(parts[0])
		y1.append(parts[1])

with open('./freq_mseWithoutCluster') as fin2:
	for line in fin2:
		parts = line.split(":",1)
		x2.append(parts[0])
		y2.append(parts[1])
for i in range(len(x1)):
	for j in range(len(x2)):
		if x1[i] == x2[j]:
			x.append(int(x1[i]))
			diff = float(y1[i]) - float(y2[j])
			print "x is: " + str(x1[i]) + " y is: " + str(diff)
			y.append(diff)
fig, ax = plt.subplots()
ax.plot(x1, y1, 'ro', label='Model with clusters')
ax.plot(x2, y2, 'bs', label='Model without clusters')
legend = ax.legend(loc='upper right', shadow=True)
for label in legend.get_texts():
	label.set_fontsize("large")
#withCluster = plt.plot(x1, y1, 'ro', label='Model 2')
#withoutCluster = plt.plot(x2, y2, 'bs', label='Model 1')
#plt.plot(x1, y1,'ro', x2, y2, 'bs')
#plt.plot(x, y, "bs")
#z = np.polyfit(x, y, 1)
#p = np.poly1d(z)
#plt.plot(x, p(x), "r-")
plt.ylabel("MSE", fontsize=20)
plt.xlabel("Number of reviews in training set", fontsize=20)
plt.show()

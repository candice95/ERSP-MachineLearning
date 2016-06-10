#!/usr/bin/python

import gzip
import json
from collections import defaultdict
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.feature_extraction import DictVectorizer
import matplotlib.pyplot as plt
import numpy as np
import sys

# step1. build a matrix of geo coordinates
v = DictVectorizer()
a = []
b = []
D = []
buses = []
with gzip.open('CA_5CoreBusinesses.json.gz', 'rb') as f:
	for line in f:
		bus = json.loads(line)
		coordinates = bus["gps"]
		b_id = bus["id"]
		T = {}
		T["x"] = coordinates[0]
		T["y"] = coordinates[1]
		if T["x"] > 50 or T["y"] < -150:
			continue
		a.append(coordinates[0])
		b.append(coordinates[1])
		D.append(T)
		buses.append(b_id)
X = v.fit_transform(D)

# step2. run kmeans  
km = MiniBatchKMeans(init='k-means++', n_clusters=500, tol=1e-7, init_size=1000)
km.fit(X)

# step3. Write to output file
result = {}
for label, busid in zip(km.labels_, buses):
	info = {}
	info['busId'] = busid
	info['cluster'] = int(label)
	result[busid] = info
# these two files are experimental input to heat map
with gzip.open('CA_bus500cluster.json.gz', 'wb') as f_out:
	for each in result:
		json.dump(result[each], f_out)
		f_out.write("\n")

# step4. visualize results
h = .2
x_min = X[:, 0].min() - 1
x_max =  X[:, 0].max() + 1
y_min = X[:, 1].min() - 1
y_max =  X[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
Z = km.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
plt.figure(1)
plt.clf()
plt.imshow(Z, interpolation='nearest',
           extent=(xx.min(), xx.max(), yy.min(), yy.max()),
					 cmap=plt.cm.Paired,
					 aspect='auto', origin='lower')
plt.plot(a, b, 'k.')
centroids = km.cluster_centers_
plt.scatter(centroids[:, 0], centroids[:, 1], marker='x', s=169, linewidths=1, color='r', zorder=10)
with gzip.open('500centroids.json.gz', 'wb') as f_out_2:
  for eachx in centroids[:, 0]:
		json.dump(eachx, f_out_2)
		f_out_2.write("\n")
  for eachy in centroids[:, 1]:
		json.dump(eachy, f_out_2)
		f_out_2.write("\n")
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.show()

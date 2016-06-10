#!/usr/bin/python
import matplotlib.pyplot as plt
import numpy as np
import json
import gzip
import random
from decimal import Decimal
from mpmath import *


freq_mseDict = {}
def getAvg():
	revNums = []
	with gzip.open("./CA_5CoreReviews.json.gz") as rev:
		for review in rev:
			review = eval(review)
			revNums.append(review["rating"]/1000)
	return np.mean(revNums)

def getAvgMSE():
	avgMseSum = []
	avg = getAvg()
	with gzip.open("./CA_5CoreReviews.json.gz") as rev:
		for review in rev:
			review = eval(review)
			avgMseSum.append((review["rating"]/1000 - avg) ** 2)
	return np.mean(avgMseSum)

def getMSE(alpha, userDict, businessDict, clusterDict, busClusts, revs):
	mseSum = []
	freqDict = {}
	dictFreq = {} 
	for review in revs:
		if(review[22:] in busClusts):
			mseSum.append((revs[review]/1000 - (alpha + userDict[review[:21]] + businessDict[review[22:]] + clusterDict[busClusts[review[22:]][0]]))**2)
			if busClusts[review[22:]][1] in freqDict :
				freqDict[busClusts[review[22:]][1]].append((revs[review]/1000 - (alpha + userDict[review[:21]] + businessDict[review[22:]] + clusterDict[busClusts[review[22:]][0]]))**2)
				dictFreq[busClusts[review[22:]][1]] += 1
			else:
				freqDict[busClusts[review[22:]][1]] = [((revs[review]/1000 - (alpha + userDict[review[:21]] + businessDict[review[22:]] + clusterDict[busClusts[review[22:]][0]]))**2)]
				dictFreq[busClusts[review[22:]][1]] = 1

	print "MSEs based on number of training occurrences"
	mses = []
	global freq_mseDict
	for entry in freqDict:
		mse = mpf(np.mean(freqDict[entry]))
		mses.append(mse)
		freq_mseDict[entry] = mse
 		print entry, ": %.20f" % mse, "with", dictFreq[entry], "businesses"
#	plt.plot(freqDict.keys(), mses, 'ro')
#	plt.ylabel("MSE")
#	plt.xlabel("Number of times seen at training")
#	plt.show()
#	print "MSE: %.20f" % mpf(np.mean(mseSum))
	print "Overall mse: %.20f" % mpf(np.mean(mseSum))
	return mpf(np.mean(mseSum))

def writeMSE():
	with open('./freq_mseWithZipCluster', 'w') as outfile:
		for each in freq_mseDict:
			outfile.write('%d:%.20f\n' %(each,freq_mseDict[each]))

def getRandomSample():
	with gzip.open("./CA_5CoreReviews.json.gz") as rev: # ./WY_2CoreReviews.json.gz
		IDs = []
		for review in rev:
			review = eval(review)
			IDs.append(review)
		random.shuffle(IDs)
		returnIDs = {}
		testReturnIDs = {}
		for i in range(0, int(.33*len(IDs))): #.9*
			returnIDs[IDs[i]["pairId"]] = IDs[i]["rating"]
		for i in range(int(.33*len(IDs)), int(.66*len(IDs))):
			testReturnIDs[IDs[i]["pairId"]] = IDs[i]["rating"]
		return [returnIDs, testReturnIDs]

def basicLinReg():
	mp.dps = 1000
	allRevs = getRandomSample()
	revs = allRevs[0]
	testRevs = allRevs[1]
	with gzip.open("./CA_UserDict.json.gz") as USERS: # ./WY_UserDict.json.gz
		with gzip.open("./CA_BusinessDict.json.gz") as BUSINESSES: # ./WY_BusinessDict.json.gz
			with gzip.open("./postcodeCluster.json.gz") as CLUSTERS:
				# usr is a dict mapping each user (user ID is key) to a list of the businesses they have rated
				for x in USERS:
					usr = eval(x)
				# bus is a dict mapping each business (business ID is key) to a list of the users who have rated it
				for y in BUSINESSES:
					bus = eval(y)
				# userDict is the offsets for each user
				userDict = {}
				for key in usr:
					userDict[key] = mpf(0)
				# businessDict is the offsets for each business
				businessDict = {}
				for key in bus:
					businessDict[key] = mpf(0)
				# clusterDict is the offsets for each cluster
				clusterDict = {}
				# clust is a dict mapping each cluster number to a list of the businesses in it
				clust = {}
				# busClusts is a dict mapping each business to its cluster number
				busClusts = {}
				for cluster in CLUSTERS:
					cluster = eval(cluster)
					busClusts[cluster["busId"]] = [cluster["cluster"], 0]
					if cluster["cluster"] in clust:
						clust[cluster["cluster"]].append(cluster["busId"])
					else:
						clust[cluster["cluster"]] = [cluster["busId"]]
						clusterDict[cluster["cluster"]] = 0
				# iters counts the number of iterations the regression algorithm takes to stabilize
				iters = 0
				# l is the regularizer in the formula, can be changed
				l = 5;
				while True:
					iters = iters + 1
					count = 0
					# i will count the number of entries of each type, for averaging
					i = 0
					for entry in revs:
						if entry[22:] in busClusts:
							count += mpf(mpf(revs[entry] / 1000) - (userDict[entry[:21]] + businessDict[entry[22:]] + clusterDict[busClusts[entry[22:]][0]]))
							i += 1
							if(iters == 2):
								busClusts[entry[22:]][1] += 1
					alpha = mpf(count/i)
					# Print the original MSE once with the average rating, for comparisons
#					if (iters == 1):
#						print 'MSE with original (average value) alpha: %.20f' % getMSE(alpha, userDict, businessDict, clusterDict, busClusts, revs)
					# Print the iteration number for marking
					print "On iteration", iters
					# Print alpha value for the current iteration
					if (iters > 1):
						print 'Curent alpha: %.50f' % alpha
					# entry is the user ID
					for entry in userDict:
						count = 0
						i = 0
						# bsns is the corresponding business ID
						for bsns in usr[entry]:
							if (((entry + "," + bsns) in revs) and bsns in busClusts):
								i += 1
								count += mpf(mpf(revs[entry + "," + bsns]/1000) - alpha - businessDict[bsns] - clusterDict[busClusts[bsns][0]])
						if(i > 0):
							userDict[entry] = mpf(count/(l+i))
					# entry is the business ID
					for entry in businessDict:
						count = 0
						i = 0
						# ur is the corresponding user ID
						for ur in bus[entry]:
							if (((ur + "," + entry) in revs) and entry in busClusts):
								i += 1
								count += mpf(mpf(revs[ur + "," + entry]/1000) - alpha - userDict[ur] - clusterDict[busClusts[entry][0]])
						if(i > 0):
							businessDict[entry] = mpf(count/(l+i))
					# entry is the cluster number
					for entry in clust:
						count = 0
						i = 0
						# bsns is the business ID
						for bsns in clust[entry]:
							# ur is the user ID
							for ur in bus[bsns]:
								if ((ur + "," + bsns) in revs):
									i += 1
									count += mpf(mpf(revs[ur + "," + bsns]/1000) - alpha - userDict[ur] - businessDict[bsns])
						if(i > 0):
							clusterDict[entry] = mpf(count/(l+i))
					# for debugging
#					for entry in clusterDict:
#						print "%.5f" % clusterDict[entry]
					if (iters == 1):
						currMSE = getMSE(alpha, userDict, businessDict, clusterDict, busClusts, testRevs)
						#print 'MSE for iteration', str(iters) + ":", "%.20f" % currMSE
						#print 'MSE on test set for iteration', str(iters) + ":", "%.20f" % getMSE(alpha, userDict, businessDict, clusterDict, busClusts, testRevs)
					else:
						tempMSE = getMSE(alpha, userDict, businessDict, clusterDict, busClusts, testRevs)
						#print 'MSE for iteration', str(iters) + ":", " %.20f" % tempMSE
						print 'MSE difference is %.20f' % mpf(currMSE-tempMSE)
						#print 'MSE on test set for iteration', str(iters) + ":", "%.20f" % getMSE(alpha, userDict, businessDict, clusterDict, busClusts, testRevs)
						if (0 < currMSE-tempMSE < 0.001):
							writeMSE()
							break
						currMSE = tempMSE

def main():
#	print "The average rating across all reviews is ", getAvg()
#	print "The overall MSE across all reviews is ", getAvgMSE()
	print "Executing linear regression"
	basicLinReg()

if __name__ == "__main__": main()

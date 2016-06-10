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

def getMSE(alpha, userDict, businessDict, revs):
	mseSum = []
	freqDict = {}
	busesInFreqs = {}
	for review in revs:
			mseSum.append((revs[review]/1000 - (alpha + userDict[review[:21]] + businessDict[review[22:]][0]))**2)
			if businessDict[review[22:]][1] in freqDict :
				freqDict[businessDict[review[22:]][1]].append((revs[review]/1000 - (alpha + userDict[review[:21]] + businessDict[review[22:]][0]))**2)
				busesInFreqs[businessDict[review[22:]][1]] += 1
			else:
				freqDict[businessDict[review[22:]][1]] = [((revs[review]/1000 - (alpha + userDict[review[:21]] + businessDict[review[22:]][0]))**2)]
				busesInFreqs[businessDict[review[22:]][1]] = 1

	print "MSEs based on number of training occurrences"
	global freq_mseDict
	mses = []
	for entry in freqDict:
		mse = mpf(np.mean(freqDict[entry]))
		mses.append(mse)
		freq_mseDict[entry] = mse
		print entry, ": %.20f" % mse, "with", busesInFreqs[entry], "businesses"

#	plt.plot(freqDict.keys(), mses, 'ro')
#	plt.ylabel("MSE")
#	plt.xlabel("Number of times seen at training")
#	plt.show()
	print "Overall mse: %.20f" % mpf(np.mean(mseSum))
	return mpf(np.mean(mseSum))

def writeMSE():
	with open('./freq_mseWithoutCluster', 'w') as outfile:
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

			for x in USERS:
				usr = eval(x)
			for y in BUSINESSES:
				bus = eval(y)
			userDict = {}
			for key in usr:
				userDict[key] = mpf(0)
			businessDict = {}
			for key in bus:
				businessDict[key] = [mpf(0), 0]
			n = len(revs)
			iters = 0
			alpha = 0
			l = 5;
			while True:
				iters = iters + 1
				print "On iteration", iters
				count = 0
				i = 0
				for entry in revs:
					count += mpf(mpf(revs[entry] / 1000) - (userDict[entry[:21]] + businessDict[entry[22:]][0]))
					i += 1
					if (iters ==1):
						businessDict[entry[22:]][1] += 1
				alpha = mpf(count/(i))
				print 'Curent alpha: %.50f' % alpha
				if (iters == 1):
					print 'MSE with original (average value) alpha: %.20f' % getMSE(alpha, userDict, businessDict, revs)
				for entry in userDict:
					count = 0
					i = 0
					for bsns in usr[entry]:
						if ((entry + "," + bsns) in revs):
							i += 1
							count += mpf(mpf(revs[entry + "," + bsns]/1000) - alpha - businessDict[bsns][0])
					if(i > 0):
						userDict[entry] = mpf(count/(l+i))
				for entry in businessDict:
					count = 0
					i = 0
					for ur in bus[entry]:
						if ((ur + "," + entry) in revs):
							i += 1
							count += mpf(mpf(revs[ur + "," + entry]/1000) - alpha - userDict[ur])
					if(i > 0):
						businessDict[entry][0] = mpf(count/(l+i))
				if (iters == 1):
					currMSE = getMSE(alpha, userDict, businessDict, testRevs)
#					print 'MSE for iteration', str(iters) + ":", "%.20f" % currMSE
#					print 'MSE on test set for iteration', str(iters) + ":", "%.20f" % getMSE(alpha, userDict, businessDict, testRevs)
				else:
					tempMSE = getMSE(alpha, userDict, businessDict, testRevs)
#					print 'MSE for iteration', str(iters) + ":", " %.20f" % tempMSE
					print 'MSE difference is %.20f' % mpf(currMSE-tempMSE)
#					print 'MSE on test set for iteration', str(iters) + ":", "%.20f" % getMSE(alpha, userDict, businessDict, testRevs)
					if (currMSE-tempMSE < 0.001):
						writeMSE()
						break
					currMSE = tempMSE

def main():
#	print "The average rating is ", getAvg()
#	print "The overall MSE is ", getAvgMSE()
	print "Executing linear regression"
	basicLinReg()

if __name__ == "__main__": main()

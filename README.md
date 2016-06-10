# ERSP-MachineLearning
This repository contains the source code for linear regression models.
Main Models
getModel.py : script for linear regression model with geographical coordinates.
- can use either k-mean cluster or zipcode cluster as input by using file CA_bus500cluster.json.gz or postcodeCluster.json.gz; changes needed in code
savedGetModel.py : script for linear regression model without geographical coordinates

Complementary scripts
plotMSEdifference.py : visualize the MSE (mean square error) difference between two models by a plotting chart
try_kmean.py : run k-mean algorithm (library function from sklearn) to cluster businesses by their geographical coordiantes; assign each business a cluster id; output produced in a file called CA_bus500cluster.json.gz
clusPostcode.py : cluster business by their zip code; assign each business a cluster id; output produced in a file called postcodeCluster.json.gz


Source data and codes for cleaning up data are not shown here.

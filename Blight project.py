
# ## Project 4 - Understanding and Predicting Property Maintenance Fines
# 
# This projct is based on a data challenge from the Michigan Data Science Team ([MDST](http://midas.umich.edu/mdst/)). 
# 
# The Michigan Data Science Team ([MDST](http://midas.umich.edu/mdst/)) and the Michigan Student Symposium for Interdisciplinary Statistical Sciences ([MSSISS]
#(https://sites.lsa.umich.edu/mssiss/)) have partnered with the City of Detroit #to help solve one of the most pressing problems facing Detroit - blight.
#[Blight violations](http://www.detroitmi.gov/How-Do-I/Report/Blight-Complaint-FAQs) are issued by the city to individuals who allow their properties to remain
# in a deteriorated condition. Every year, the city of Detroit issues millions #of dollars in fines to residents and every year, many of these fines remain
# unpaid. Enforcing unpaid blight fines is a costly and tedious process, #so the city wants to know: how can we increase blight ticket compliance?
# 
# The first step in answering this question is understanding when and why a resident might fail to comply with a blight ticket by predicting whether a given blight ticket will be paid on time.

#Sources of data for thsi project: 
# * [Building Permits](https://data.detroitmi.gov/Property-Parcels/Building-Permits/xw2a-a7tf)
# * [Trades Permits](https://data.detroitmi.gov/Property-Parcels/Trades-Permits/635b-dsgv)
# * [Improve Detroit: Submitted Issues](https://data.detroitmi.gov/Government/Improve-Detroit-Submitted-Issues/fwz3-w3yn)
# * [DPD: Citizen Complaints](https://data.detroitmi.gov/Public-Safety/DPD-Citizen-Complaints-2016/kahe-efs3)
# * [Parcel Map](https://data.detroitmi.gov/Property-Parcels/Parcel-Map/fxkw-udwf)
# 
# ___
# 
# Two data files are provided for use in training and validating models: train.csv and test.csv. Each row in these two files corresponds
#to a single blight ticket, and includes information about when, why, and to whom each ticket was issued. The target variable is compliance,
#which is True if the ticket was paid early, on time, or within one month of the hearing data, False if the ticket was paid after the hearing date
#or not at all, and Null if the violator was found not responsible. Compliance, as well as a handful of other variables that will not be available
#at test-time, are only included in train.csv.
# 
# Note: All tickets where the violators were found not responsible are not considered during evaluation. They are included in the training set
#as an additional source of data for visualization, and to enable unsupervised and semi-supervised approaches. However, they are not included in the test set.
# 
# **File descriptions** 
#     train.csv - the training set (all tickets issued 2004-2011)
#     test.csv - the test set (all tickets issued 2012-2016)
#     addresses.csv & latlons.csv - mapping from ticket id to addresses, and from addresses to lat/lon coordinates. 
#      Note: misspelled addresses may be incorrectly geolocated.
# 
# **Data fields**
# 
# train.csv & test.csv
# 
#     ticket_id - unique identifier for tickets
#     agency_name - Agency that issued the ticket
#     inspector_name - Name of inspector that issued the ticket
#     violator_name - Name of the person/organization that the ticket was issued to
#     violation_street_number, violation_street_name, violation_zip_code - Address where the violation occurred
#     mailing_address_str_number, mailing_address_str_name, city, state, zip_code, non_us_str_code, country - Mailing address of the violator
#     ticket_issued_date - Date and time the ticket was issued
#     hearing_date - Date and time the violator's hearing was scheduled
#     violation_code, violation_description - Type of violation
#     disposition - Judgment and judgement type
#     fine_amount - Violation fine amount, excluding fees
#     admin_fee - $20 fee assigned to responsible judgments
# state_fee - $10 fee assigned to responsible judgments
#     late_fee - 10% fee assigned to responsible judgments
#     discount_amount - discount applied, if any
#     clean_up_cost - DPW clean-up or graffiti removal cost
#     judgment_amount - Sum of all fines and fees
#     grafitti_status - Flag for graffiti violations
#     
# train.csv only
# 
#     payment_amount - Amount paid, if any
#     payment_date - Date payment was made, if it was received
#     payment_status - Current payment status as of Feb 1 2017
#     balance_due - Fines and fees still owed
#     collection_status - Flag for payments in collections
#     compliance [target variable for prediction] 
#      Null = Not responsible
#      0 = Responsible, non-compliant
#      1 = Responsible, compliant
#     compliance_detail - More information on why each ticket was marked compliant or non-compliant
# 
#---
# 
# Project goal: Create a function that trains a model to predict blight ticket compliance in Detroit using `train.csv`.
# Using this model, return a series of length 61001 with the data being the probability that each corresponding ticket from `test.csv` will be paid, and the index being the ticket_id.


import pandas as pd
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MinMaxScaler

#data laoding
train_data = pd.read_csv('train.csv', encoding = 'ISO-8859-1')
test_data = pd.read_csv('test.csv')
train_data = train_data[(train_data['compliance'] == 0) | (train_data['compliance'] == 1)]
    
#data cleansing
    
train_data = train_data[~train_data['hearing_date'].isnull()]
train_data.drop(['balance_due','collection_status','compliance_detail','payment_amount','payment_date','payment_status'], axis=1, inplace=True)
string_list = ['violator_name', 'zip_code', 'country', 'city', 'inspector_name', 'violation_street_number', 
                'violation_street_name', 'violation_zip_code', 'violation_description', 'mailing_address_str_number',
                'mailing_address_str_name', 'non_us_str_code', 'agency_name', 'state', 'disposition','ticket_issued_date', 
                 'hearing_date','grafitti_status', 'violation_code']
train_data.drop(string_list, axis=1, inplace=True)
test_data.drop(string_list, axis=1, inplace=True)
    
    
address =  pd.read_csv('addresses.csv')
latlons = pd.read_csv('latlons.csv')
address = address.set_index('address').join(latlons.set_index('address'), how='left')
train_data = train_data.set_index('ticket_id').join(address.set_index('ticket_id'))
test_data = test_data.set_index('ticket_id').join(address.set_index('ticket_id'))

train_data['lat'].fillna(method='pad', inplace=True)
train_data['lon'].fillna(method='pad', inplace=True)
test_data['lat'].fillna(method='pad', inplace=True)
test_data['lon'].fillna(method='pad', inplace=True)
    
# Training data
    
y_train = train_data.compliance
X_train = train_data.drop('compliance', axis=1)
X_test = test_data
    
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
    
clf = MLPClassifier(hidden_layer_sizes = [100, 10], alpha = 2,
                       random_state = 0, solver='lbfgs', verbose=0)

clf.fit(X_train_scaled, y_train)

test_proba = clf.predict_proba(X_test_scaled)[:,1]

    
test_df = pd.read_csv('test.csv', encoding = "ISO-8859-1")
test_df['compliance'] = test_proba
test_df.set_index('ticket_id', inplace=True)
    
    
blight_model= test_df.compliance

"""
PROBLEM 5 Objective
apply 10-fold-cross-validattion linear regression on three period:
1. Before Feb. 1, 8:00 a.m.
2. Between Feb. 1, 8:00 a.m. and 8:00 p.m.
3. After Feb. 1, 8:00 p.m.

Use the three model obtained an
"""

import json
import datetime
import statsmodels.api as sm
import numpy as np
import help_functions
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold

def predictor_label_extraction(hour_wise_data):
    x, y = [], []

    for prev_hour in hour_wise_data.keys():
        hour = datetime.datetime.strptime(prev_hour, "%Y-%m-%d %H:%M:%S")
        next_hour = unicode(hour + datetime.timedelta(hours=1))

        if next_hour in hour_wise_data.keys():
            y.append(hour_wise_data[next_hour]['tweets_count'])
            x.append(hour_wise_data[prev_hour].values())

    return x, y


def cross_validation(x, y):
    kf = KFold(n_splits=10, random_state=42)

    X, Y = np.array(x), np.array(y)

    for train_index, test_index in kf.split(X):
        train_x, test_x = X[train_index], X[test_index]
        train_y, test_y = Y[train_index], Y[test_index]

        # train_x = sm.add_constant(train_x)
        # model = sm.OLS(train_y, train_x)
        # results = model.fit()

        # random forest
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        results = model.fit(train_x, train_y)

    return results

############# Executing section ################

test_files = ['sample1_period1', 'sample2_period2', 'sample3_period3',
              'sample4_period1', 'sample5_period1', 'sample6_period2',
              'sample7_period3', 'sample8_period1', 'sample9_period2', 'sample10_period3']  # tweet-data file names
input_files = ['gohawks', 'gopatriots', 'nfl', 'patriots', 'sb49', 'superbowl']  # tweet-data file names

for file_name in input_files:
    tweets = open('./tweet_data/tweets_#{0}.txt'.format(file_name), 'rb')
    hour_wise_feature = help_functions.features_extraction(tweets)

    ######### Break hourwise data into three periods #######
    hourwise_period1, hourwise_period2, hourwise_period3 = {}, {}, {}
    break_point1 = datetime.datetime(2015, 2, 1, 8, 0, 0)
    break_point2 = datetime.datetime(2015, 2, 1, 20, 0, 0)

    for i in hour_wise_feature:
        data_time = datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S")
        if data_time < break_point1:
            hourwise_period1[i] = hour_wise_feature[i]
        elif data_time > break_point1 and data_time < break_point2:
            hourwise_period2[i] = hour_wise_feature[i]
        elif data_time > break_point2:
            hourwise_period3[i] = hour_wise_feature[i]

    ######### perform 10-fold-cross-validation #######
    X1, Y1 = predictor_label_extraction(hourwise_period1)
    X2, Y2 = predictor_label_extraction(hourwise_period2)
    X3, Y3 = predictor_label_extraction(hourwise_period3)

    ######### Get OLS model for three periods ########
    p1_model = cross_validation(X1, Y1)
    p2_model = cross_validation(X2, Y2)
    p3_model = cross_validation(X3, Y3)

    for files in test_files:
        new_tweets = open('./test_data/{0}.txt'.format(files), 'rb')
        hour_wise_data_test = help_functions.features_extraction(new_tweets)

        test_x, actual_y, predicted_y = [], [], []

        for prev_hour in hour_wise_data_test.keys():
            hour = datetime.datetime.strptime(prev_hour, "%Y-%m-%d %H:%M:%S")
            next_hour = unicode(hour + datetime.timedelta(hours=1))

            test_x.append(hour_wise_data_test[prev_hour].values())

            if next_hour in hour_wise_data_test.keys():
                # Note len(actual_y) should be len(test_x) - 1
                actual_y.append(hour_wise_data_test[next_hour]['tweets_count'])


        # choose different model for different test period
        if 'period1' in files:
            predicted_y = p1_model.predict(test_x)
        elif 'period2' in files:
            predicted_y = p2_model.predict(test_x)
        elif 'period3' in files:
            predicted_y = p3_model.predict(test_x)

        print('-'*50)
        print('Using model generated by hash tag ' + file_name)
        print('The predict tweet count for ' + files + ' is: ' +
              str(predicted_y))
        print('The actual tweet count for ' + files + ' is: ' +
              str(actual_y))

        error_precentage = abs(actual_y-predicted_y[:-1])/actual_y * 100
        #   predicted values cover hour 2 - 7 (6 hours) while actual_y is 2 - 6 (5 hours)
        print('The predicted error precentage is: ' + str(error_precentage))
        print('The average error precentage is: ' + str(np.mean(error_precentage)))


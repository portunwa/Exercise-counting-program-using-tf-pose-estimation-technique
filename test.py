'''
    this program create the data for train
    a a classofier model in term of csv

    create by Napas vinitnantharat 
        update 27 Nov 2020
'''

import argparse #for line arguement
import logging #loggine to terminal
import time #time control module

import cv2 #module for image processing
import numpy as np #array module
import csv #to write the data to csv file

import tensorflow as tf #machine learning module

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

import os #module operation system


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler

from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score, precision_score, f1_score

# add for gpu
'''
gpus = tf.config.experimental.list_physical_devices('GPU')
print(gpus)
tf.config.experimental.set_memory_growth(gpus[0],True)
'''

part_x = [0]*17
part_y = [0]*17
score_point = [0]*17

df = pd.read_csv('datatrainall.csv')
df_drop = df.drop(columns = ['photopath','label'])

X = df_drop
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2, random_state=300)

clf = MLPClassifier(hidden_layer_sizes=(51, 50),solver = 'sgd').fit(X, y)

fps_time = 0

cam = cv2.VideoCapture(0)

out = []# output prediction

MODEL = 'mobilenet_thin'

e = TfPoseEstimator(get_graph_path(MODEL), target_size=(432, 368))

# count time lunges and squats
count_lunges = 0
count_squats = 0

#current state 
state = 1 
#1 for set
#2 for lunges_down
#3 for squats_down




if __name__ == '__main__':

    while True:

        ret_val, image = cam.read()

        humans = e.inference(image, resize_to_default=False, upsample_size=4)
        image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)

        try:
            #for each person collect all the joint of that person
            for j in range(0,17):
                part_x[j] = humans[0].body_parts[j].x
                part_y[j] = humans[0].body_parts[j].y 
                score_point[j] = humans[0].body_parts[j].score
                total_score =  humans[0].score
        except:
            pass


        out = clf.predict(np.array([part_x + part_y + score_point])) 
        print(str(out[0]),state)
        #print(np.array([part_x + part_y + score_point]))
        

        # finite state 
        #on state set
        if state == 1:
            state = out[0]
        #on state lunges_down
        if state == 2:
            if str(out[0]) == 'set':
                count_lunges += 1
                state = 1
            if str(out[0]) == 'squats_down':
                state = 3
        #on state squats_down
        if state == 3:
            if str(out[0]) == 'set':
                count_squats += 1
                state = 1

        print(count_lunges,count_squats)
        
        cv2.putText(image,
                        "lunges:%d squats:%d" % (count_lunges,count_squats),
                        (10, 20),  cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (0, 255, 0), 2)
        fps_time = time.time()
        cv2.imshow('exercise counting', image)
            
        if cv2.waitKey(1) == 27:
            break





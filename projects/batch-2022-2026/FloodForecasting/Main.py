from tkinter import *
import tkinter
from tkinter import filedialog
import numpy as np
from tkinter.filedialog import askopenfilename
import pandas as pd 
from tkinter import simpledialog
import matplotlib.pyplot as plt
import os
import socket
import json
import base64
from sklearn.metrics import mean_squared_error
import math
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D
from keras.models import Sequential, load_model
from keras.callbacks import ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from keras.layers import  MaxPooling2D


main = tkinter.Tk()
main.title("FFM: Flood Forecasting Model Using Federated Learning")
main.geometry("1000x650")

global filename, dataset
global extension_model
global X, Y, X_train, y_train, X_test, y_test
global accuracy, mse, rmse, norm1, norm2

def uploadDataset():
    global filename, dataset
    filename = filedialog.askopenfilename(initialdir = "Dataset")
    dataset = pd.read_csv(filename)
    dataset.fillna(0, inplace = True)
    text.delete('1.0', END)
    text.insert(END,filename+' Loaded\n\n')
    text.insert(END,str(dataset))

def preprocessDataset():
    global filename, dataset, norm1, norm2, X, Y
    text.delete('1.0', END)
    norm1 = MinMaxScaler(feature_range = (0, 1))
    norm2 = MinMaxScaler(feature_range = (0, 1))
    dataset = dataset.values
    X = dataset[:,2:dataset.shape[1]-1]
    Y = dataset[:,dataset.shape[1]-1]
    indices = np.arange(X.shape[0])
    np.random.shuffle(indices)
    X = X[indices]
    Y = Y[indices]
    Y = Y.reshape(-1, 1)
    X  = norm1.fit_transform(X)
    Y = norm2.fit_transform(Y)
    text.insert(END,"Dataset preprocessing like normalization & Shuffling Completed\n\n")
    text.insert(END,"Normalized Dataset\n\n")
    text.insert(END,str(X))

def datasetSplit():
    global X, Y, X_train, y_train, X_test, y_test
    text.delete('1.0', END)
    text.insert(END,"Dataset Train & Test Split Details\n\n")
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = 0.2)
    text.insert(END,"Total records found in dataset  = "+str(X.shape[0])+"\n")
    text.insert(END,"Total features found in dataset = "+str(X.shape[1])+"\n")
    text.insert(END,"80% dataset for training : "+str(X_train.shape[0])+"\n")
    text.insert(END,"20% dataset for testing  : "+str(X_test.shape[0])+"\n")

#function to calculate MSE and other metrics
def calculateMetrics(algorithm, predict, test_labels):
    predict = norm2.inverse_transform(np.abs(predict))
    test_label = norm2.inverse_transform(test_labels)
    mse_value = mean_squared_error(test_label, predict)
    rmse_value = math.sqrt(mse_value)
    predict = predict.ravel()
    test_label = test_label.ravel()
    acc = 100 - rmse_value
    mse.append(mse_value)
    rmse.append(rmse_value)
    accuracy.append(acc)
    text.insert(END,algorithm+" MSE      : "+str(mse_value)+"\n")
    text.insert(END,algorithm+" RMSE     : "+str(rmse_value)+"\n")
    text.insert(END,algorithm+" Accuracy : "+str(acc)+"\n\n")    
    for i in range(len(predict)):
        text.insert(END,"True Water Level : "+str(test_label[i])+" Predicted Water Level : "+str(predict[i])+"\n")
    plt.plot(test_label, color = 'red', label = 'True Water Level')
    plt.plot(predict, color = 'green', label = 'Predicted Water Level')
    plt.title(algorithm+' Water Level Prediction')
    plt.xlabel('Test Data')
    plt.ylabel('Predicted Water Level')
    plt.legend()
    plt.show()    

def runFFNN():
    global X, Y, X_train, y_train, X_test, y_test
    global accuracy, mse, rmse
    text.delete('1.0', END)
    accuracy = []
    mse = []
    rmse = []
    model = Sequential()
    model.add(Dense(32,  input_shape=(X.shape[1],)))
    model.add(Dense(16, activation="relu"))
    model.add(Dense(units=1))
    model.compile(optimizer = 'adam', loss = 'mean_squared_error')
    if os.path.exists('model/ff_weights.hdf5') == False:
        model_check_point = ModelCheckpoint(filepath='model/ff_weights.hdf5', verbose = 1, save_best_only = True)
        model.fit(X_train, y_train, epochs = 80, batch_size = 2, validation_data=(X_test, y_test), callbacks=[model_check_point], verbose=1)
    else:
        model = load_model('model/ff_weights.hdf5')
    predict = model.predict(X_test)
    calculateMetrics("FFNN", predict, y_test)

def runExtension():
    global X, Y, X_train, y_train, X_test, y_test
    global accuracy, mse, rmse, extension_model
    text.delete('1.0', END)
    X_train1 = X_train.reshape(X_train.shape[0],X_train.shape[1], 1, 1)
    X_test1 = X_test.reshape(X_test.shape[0],X_test.shape[1], 1, 1)

    extension_model = Sequential()
    extension_model.add(Convolution2D(32, 1, 1, input_shape = (X_train1.shape[1], X_train1.shape[2], X_train1.shape[3]), activation = 'relu'))
    extension_model.add(MaxPooling2D(pool_size = (1, 1)))
    extension_model.add(Convolution2D(16, 1, 1, activation = 'relu'))
    extension_model.add(MaxPooling2D(pool_size = (1, 1)))
    extension_model.add(Flatten())
    extension_model.add(Dense(output_dim = 28, activation = 'relu'))
    extension_model.add(Dense(output_dim = 1))
    extension_model.compile(optimizer = 'adam', loss = 'mean_squared_error')
    if os.path.exists('model/extension_weights.hdf5') == False:
        model_check_point = ModelCheckpoint(filepath='model/extension_weights.hdf5', verbose = 1, save_best_only = True)
        extension_model.fit(X_train1, y_train, epochs = 80, batch_size = 2, validation_data=(X_test1, y_test), callbacks=[model_check_point], verbose=1)
    else:
        extension_model = load_model('model/extension_weights.hdf5')
    predict = extension_model.predict(X_test1)
    calculateMetrics("Extension CNN2D", predict, y_test)

def uploadtoServer():
    text.delete('1.0', END)
    station_name = simpledialog.askstring("Enter Station Name to Save Model at Centralozed Server","Enter Station Name to Save Model at Centralozed Server",parent=main)
    with open('model/extension_weights.hdf5', 'rb') as file:
        model = base64.b64encode(file.read())
    file.close()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2222))
    jsondata = json.dumps({"request": 'update_model', "station": station_name, "model": model.decode()})
    message = client.send(jsondata.encode())
    data = client.recv(100)
    data = data.decode()
    text.insert(END,"Server Response : "+data+"\n\n")

def graph():
    df = pd.DataFrame([['Propose FFNN','MSE',mse[0]],['Propose FFNN','RMSE',rmse[0]], ['Propose FFNN','Accuracy',accuracy[0]],
                       ['Extension CNN2D','MSE',mse[1]],['Extension CNN2D','RMSE',rmse[1]],['Extension CNN2D','Accuracy',accuracy[1]],                       
                  ],columns=['Parameters','Algorithms','Value'])
    df.pivot("Parameters", "Algorithms", "Value").plot(kind='bar')
    plt.title("Propose FFNN & Extension CNN2D Performance Graph")
    plt.show()

def predict():
    global norm1, norm2, extension_model
    filename = filedialog.askopenfilename(initialdir = "Dataset")
    #read test data and predict flood
    dataset = pd.read_csv(filename)
    dataset.fillna(0, inplace = True)
    dataset = dataset.values
    X = dataset[:,2:dataset.shape[1]]
    X = norm1.transform(X)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1, 1))
    predict = extension_model.predict(X) #perform flood prediction using extension CNN2D object
    predict = norm2.inverse_transform(predict)
    for i in range(len(predict)):
        text.insert(END,"Test Data = "+str(dataset[i])+"=====> Forecasted Water Level : "+str(predict[i,0])+"\n\n")

       
font = ('times', 15, 'bold')
title = Label(main, text='FFM: Flood Forecasting Model Using Federated Learning', justify=LEFT)
title.config(bg='lavender blush', fg='DarkOrchid1')  
title.config(font=font)           
title.config(height=3, width=120)       
title.place(x=100,y=5)
title.pack()

font1 = ('times', 12, 'bold')
uploadButton = Button(main, text="Upload Flood Dataset", command=uploadDataset)
uploadButton.place(x=10,y=100)
uploadButton.config(font=font1)  

preprocessButton = Button(main, text="Preprocess Dataset", command=preprocessDataset)
preprocessButton.place(x=300,y=100)
preprocessButton.config(font=font1)

rnnButton = Button(main, text="Train & Test Split", command=datasetSplit)
rnnButton.place(x=480,y=100)
rnnButton.config(font=font1)

lstmButton = Button(main, text="Run Feed Forward Neural Network", command=runFFNN)
lstmButton.place(x=670,y=100)
lstmButton.config(font=font1)

ffButton = Button(main, text="Run Extension CNN2D Algorithm", command=runExtension)
ffButton.place(x=10,y=150)
ffButton.config(font=font1)

graphButton = Button(main, text="Upload Federated Model to Server", command=uploadtoServer)
graphButton.place(x=300,y=150)
graphButton.config(font=font1)

predictButton = Button(main, text="Accuracy Comparison Graph", command=graph)
predictButton.place(x=10,y=200)
predictButton.config(font=font1)

topButton = Button(main, text="Flood Forecasting using Test Data", command=predict)
topButton.place(x=300,y=200)
topButton.config(font=font1)

font1 = ('times', 12, 'bold')
text=Text(main,height=20,width=160)
scroll=Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=10,y=250)
text.config(font=font1) 

main.config(bg='light coral')
main.mainloop()

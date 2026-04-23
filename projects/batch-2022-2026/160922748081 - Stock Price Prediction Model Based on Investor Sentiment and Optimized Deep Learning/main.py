from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
import tkinter
from tkinter import filedialog
import matplotlib.pyplot as plt
from tkinter.filedialog import askopenfilename
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split 
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tkinter import *
from tkinter import ttk
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM  #class for LSTM regression
from keras.layers import Dropout
from keras.models import model_from_json
import pickle
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

main = Tk()
main.title("A Stock Price Prediction Model Based on Investor Sentiment and Optimized Deep Learning")
main.geometry("1300x1200")


global filename
global dataset
global X, Y, mse, X_train, X_test, y_train, y_test
sc = MinMaxScaler(feature_range = (0, 1))
global stock_name, stock_list
global dataset_dates


def uploadDataset():
    global filename, stock_name, dataset, stock_list
    text.delete('1.0', END)
    filename = askopenfilename(initialdir = "Dataset")
    fname = os.path.basename(filename)
    stock_name = stock_list.get()
    if fname == 'NSE-Tata-Global-Beverages-Limited.csv':
        dataset = pd.read_csv(filename,usecols=['Date','Open','High','Low','Close'])
        dataset["Date"] = pd.to_datetime(dataset.Date,format="%Y-%m-%d")
        dataset.index = dataset['Date']
        dataset = dataset.sort_index(ascending=True, axis=0)
        dataset.fillna(0, inplace = True)
        stock_name = 'NSE-Tata-Global-Beverages-Limited'
    else:
        dataset = pd.read_csv(filename,usecols=['Date','Open','High','Low','Close','Stock'])
        dataset["Date"] = pd.to_datetime(dataset.Date,format="%Y-%m-%d")
        dataset.index = dataset['Date']
        dataset = dataset.sort_index(ascending=True, axis=0)
        dataset.fillna(0, inplace = True)
        dataset = dataset.loc[dataset['Stock'] == stock_name]    
    tf1.insert(END,str(filename))
    text.insert(END,"Dataset Loaded\n\n")
    text.insert(END,str(dataset.head()))
    tf1.insert(END,str(filename))
    plt.figure(figsize=(10,6), dpi=100)
    plt.plot(dataset.Date[0:20], dataset.Close[0:20], color='tab:red')
    plt.gca().set(title=stock_name+" Closing Price History", xlabel='Date', ylabel="Closing Price")
    plt.show()

def preprocessDataset():
    global stock_name, dataset, sc
    global X_train, X_test, y_train, y_test
    global dataset_dates
    global dataset_dates, dataset_original

    text.delete('1.0', END)

    dataset_dates = dataset.index
    dataset_original = dataset.copy()

    dataset = dataset.values
    Y = dataset[:,4:5]
    X = dataset[:,1:4]
    X = sc.fit_transform(X)
    Y = sc.fit_transform(Y)
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

    text.insert(END,"Dataset Preprocessing Completed\n\n")
    text.insert(END,"Dataset Normalized Values : "+str(X)+"\n\n")

    text.insert(END,"Dataset Train & Test Split. 80% dataset used for training and 20% for testing\n")
    text.insert(END,"80% training size : "+str(X_train.shape[0])+"\n")
    text.insert(END,"20% testing size : "+str(X_test.shape[0])+"\n")


from matplotlib.figure import Figure

def showScrollableGraph():
    global dataset_original, dataset_dates, stock_name

    # ✅ Safety check
    if 'dataset_original' not in globals():
        messagebox.showerror("Error", "Please preprocess dataset first")
        return

    if dataset_original is None or len(dataset_original) == 0:
        messagebox.showerror("Error", "Dataset is empty")
        return

    top = Toplevel()
    top.title("Scrollable Stock Price Graph")
    top.geometry("1000x700")

    fig = Figure(figsize=(10,8))

    # ✅ USE add_subplot (VERY IMPORTANT FIX)
    ax1 = fig.add_subplot(411)
    ax2 = fig.add_subplot(412)
    ax3 = fig.add_subplot(413)
    ax4 = fig.add_subplot(414)

    try:
        ax1.plot(dataset_original['Open'].values)
        ax1.set_title("Open Price")

        ax2.plot(dataset_original['High'].values)
        ax2.set_title("High Price")

        ax3.plot(dataset_original['Low'].values)
        ax3.set_title("Low Price")

        ax4.plot(dataset_original['Close'].values)
        ax4.set_title("Close Price")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    toolbar = NavigationToolbar2Tk(canvas, top)
    toolbar.update()
    canvas.get_tk_widget().pack()

#function to calculate MSE values
def calculateMSE(algorithm, predict, y_test):
    mse_value = mean_squared_error(y_test,predict)
    mse.append(mse_value)

    # ✅ USE SAVED DATASET DATES
    global dataset_dates

    text.insert(END,algorithm+" MSE value : "+str('{:.6f}'.format(mse_value))+"\n")
    text.insert(END,algorithm+" Accuracy  : "+str(1 - mse_value)+"\n\n")
    
    predict = sc.inverse_transform(predict)
    predict = predict.ravel()
    labels = y_test.reshape(y_test.shape[0],1)
    labels = sc.inverse_transform(labels)
    labels = labels.ravel()
    labels = labels[0:100]
    predict = predict[0:100]

    # ✅ SHOW DATE + COMPANY
    for i in range(0,20):
        if i < len(dataset_dates):
            date_val = str(dataset_dates[i])[:10]
        else:
            date_val = "N/A"

        text.insert(END,
            "Company: "+str(stock_name)+
            " | Date: "+date_val+
            " | "+algorithm+" Predicted: "+str(predict[i])+
            " | Original: "+str(labels[i])+"\n"
        )

    # ✅ IMPROVED TIME-LINE GRAPH
    x_axis = dataset_dates[:len(labels)]

    plt.figure(figsize=(12,6))

    # Original (clearly visible)
    plt.plot(x_axis, labels, linestyle='--', linewidth=2, label='Original Stock Price')

    # Predicted
    plt.plot(x_axis, predict, linewidth=1.5, label='Predicted Stock Price')

    plt.title(algorithm+' Predicted Stock Price Graph')
    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

def runANN():
    text.delete('1.0', END)
    global stock_name, dataset, sc, mse
    global X_train, X_test, y_train, y_test
    mse = []
    if os.path.exists('model/ann_model.json'):
        with open('model/ann_model.json', "r") as json_file:
            loaded_model_json = json_file.read()
            ann = model_from_json(loaded_model_json)
        json_file.close()
        ann.load_weights("model/ann_model_weights.h5")
        ann._make_predict_function()   
    else:
        #creating neural object with 50 and 50 neurons and learning rate is 0.005
        ann = Sequential()
        #defining neural network with 50 neurons
        ann.add(Dense(50, activation='relu', input_shape=(X_train.shape[1],)))
        ann.add(Dense(50, activation='relu'))#50 neurons
        ann.add(Dense(1))
        ann.compile(optimizer="adam", loss='mean_squared_error')
        hist = ann.fit(X_train, y_train, epochs = 1, batch_size = 8, validation_data=(X_test, y_test))
        ann.save_weights('model/ann_model_weights.h5')            
        model_json = ann.to_json()
        with open("model/ann_model.json", "w") as json_file:
            json_file.write(model_json)
        json_file.close()
        f = open('model/ann_history.pckl', 'wb')
        pickle.dump(hist.history, f)
        f.close()
    #performing prediction on test data using ANN   
    predict = ann.predict(X_test)
    calculateMSE("ANN", predict, y_test)

def runLSTM():
    text.delete('1.0', END)
    global stock_name, dataset, sc, mse
    global X_train, X_test, y_train, y_test

    X_train1 = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    X_test1 = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    if os.path.exists('model/lstm_model.json'):
        with open('model/lstm_model.json', "r") as json_file:
            loaded_model_json = json_file.read()
            lstm = model_from_json(loaded_model_json)
        json_file.close()
        lstm.load_weights("model/lstm_model_weights.h5")
        lstm._make_predict_function()   
    else:
        #training with LSTM algorithm and saving trained model and LSTM refrence assigned to regression variable
        lstm = Sequential()
        #defining 32 neurons
        lstm.add(LSTM(units = 50, return_sequences = True, input_shape = (X_train1.shape[1], X_train1.shape[2])))
        #0.2 as the drop out
        lstm.add(Dropout(0.2))
        lstm.add(LSTM(units = 50, return_sequences = True)) #16 another layer neurons
        lstm.add(Dropout(0.2))
        lstm.add(LSTM(units = 50, return_sequences = True))
        lstm.add(Dropout(0.2))
        lstm.add(LSTM(units = 50))
        lstm.add(Dropout(0.2))
        lstm.add(Dense(units = 1))
        lstm.compile(optimizer = 'adam', loss = 'mean_squared_error')
        hist = lstm.fit(X_train1, y_train, epochs = 1, batch_size = 8, validation_data=(X_test1, y_test))
        lstm.save_weights('model/lstm_model_weights.h5')            
        model_json = lstm.to_json()
        with open("model/lstm_model.json", "w") as json_file:
            json_file.write(model_json)
        json_file.close()
        f = open('model/lstm_history.pckl', 'wb')
        pickle.dump(hist.history, f)
        f.close()
    #performing prediction on test data    
    predict = lstm.predict(X_test1)
    calculateMSE("LSTM", predict, y_test)


def graph():
    height = mse
    bars = ('ANN MSE','LSTM MSE')
    y_pos = np.arange(len(bars))
    plt.bar(y_pos, height)
    plt.xticks(y_pos, bars)
    plt.title("ANN & LSTM Mean Square Error (MSE) Graph Comparison")
    plt.show()

def close():
    main.destroy()


font = ('times', 15, 'bold')
title = Label(main, text='A Stock Price Prediction Model Based on Investor Sentiment and Optimized Deep Learning')
title.config(bg='HotPink4', fg='yellow2')  
title.config(font=font)           
title.config(height=3, width=120)       
title.place(x=0,y=5)

font1 = ('times', 13, 'bold')
ff = ('times', 12, 'bold')

l1 = Label(main, text='Choose Dataset:')
l1.config(font=font1)
l1.place(x=430,y=100)

tf1 = Entry(main,width=45)
tf1.config(font=font1)
tf1.place(x=580,y=100)

l2 = Label(main, text='Choose Stock:')
l2.config(font=font1)
l2.place(x=50,y=100)

names = ['AAPL', 'FB', 'MSFT', 'TSLA']
stock_list = ttk.Combobox(main, values=names, postcommand=lambda: stock_list.configure(values=names))
stock_list.place(x=210,y=100)
stock_list.current(0)
stock_list.config(font=font1)

uploadButton = Button(main, text="Upload Stock Price Dataset", command=uploadDataset, bg='#ffb3fe')
uploadButton.place(x=1020,y=100)
uploadButton.config(font=font1)

preprocessButton = Button(main, text="Preprocess Dataset", command=preprocessDataset, bg='#ffb3fe')
preprocessButton.place(x=50,y=150)
preprocessButton.config(font=font1)

annButton = Button(main,text="Run ANN Algorithm", command=runANN, bg='#ffb3fe')
annButton.place(x=300,y=150)
annButton.config(font=font1)

lstmButton = Button(main,text="Run LSTM Algorithm", command=runLSTM, bg='#ffb3fe')
lstmButton.place(x=530,y=150)
lstmButton.config(font=font1)

graphButton = Button(main,text="MSE Comparison Graph", command=graph, bg='#ffb3fe')
graphButton.place(x=50,y=200)
graphButton.config(font=font1)

closeButton = Button(main,text="Exit", command=close, bg='#ffb3fe')
closeButton.place(x=550,y=200)
closeButton.config(font=font1)


scrollGraphButton = Button(main, text="View Full Graph (Scroll)", command=showScrollableGraph, bg='#ffb3fe')
scrollGraphButton.place(x=300,y=200)
scrollGraphButton.config(font=font1)

font1 = ('times', 13, 'bold')
text=Text(main,height=20,width=130)
scroll=Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=10,y=300)
text.config(font=font1)

main.config(bg='plum2')
main.mainloop()

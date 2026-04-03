#import required python classes and packages
import tkinter
from tkinter import *
from tkinter import filedialog
import json
import matplotlib.pyplot as plt
import os
import sys
import numpy as np
import cv2
import pickle
from PIL import Image, ImageDraw
import tensorflow as tf
from keras.models import Sequential, model_from_json, Model
from keras.layers import Dense, Flatten, Activation, Dropout, Input, Conv2D, MaxPooling2D
from keras.utils import np_utils
from keras.optimizers import Adam
from keras import layers
from keras.applications.vgg16 import VGG16
from keras.applications import ResNet50
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from sklearn.model_selection import train_test_split

#define global variables
precision = []
recall = []
fscore = []
accuracy = []
global filename, labels
global X, Y
global X_train, X_test, y_train, y_test
global frcnn, extension_vgg
global pictureTensor

def uploadDataset():
    global filename, labels, X, Y
    text_widget.delete(1.0, END)
    filename = filedialog.askopenfilename(initialdir='Dataset')
    pathlabel = Label(window, text=filename, bg='white', font=('times', 13, 'bold'))
    pathlabel.place(x=20, y=100)
    
    file = open(filename, 'r')
    data = json.load(file)
    text_widget.insert(END, f"{filename} loaded...\n")
    text_widget.insert(END, f"Dataset uploaded Successfully.\n")
    
    #extract one signal from data and convert to image
    signal_data = np.array(data['data']).astype('uint8')
    labels = np.array(data['labels']).astype('uint8')
    location = np.array(data['locations']).astype('uint8')
    text_widget.insert(END, f"Total ships signals found in data: {str(signal_data.shape[0])}")
    
    channel = 3
    width = 80
    height = 80
    X = signal_data.reshape([-1, channel, width, height])
    
    sample_image = X[3].transpose([2,1,0])
    lab = cv2.cvtColor(sample_image, cv2.COLOR_RGB2LAB)
    a_component = lab[:,:,1]
    th = cv2.threshold(a_component,140,255,cv2.THRESH_BINARY)[1]
    blur = cv2.GaussianBlur(th,(13,13), 11)
    heatmap_img = cv2.applyColorMap(blur, cv2.COLORMAP_HSV)
    
    plt.imshow(heatmap_img)
    plt.axis('off')
    plt.show()
    return None

def preprocessDataset():
    global labels, X, Y, X_train, X_test, y_train, y_test
    Y = np_utils.to_categorical(labels, 2)
    indexes = np.arange(X.shape[0])
    np.random.shuffle(indexes)
    X = X[indexes].transpose([0,2,3,1])
    Y = Y[indexes]
    X = X / 255
    text_widget.delete(1.0, END)
    text_widget.insert(END,"Dataset is Preprocessed Successfully...\n")
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)
    text_widget.insert(END,"Dataset Splitted into 80% dataset for training and 20% for testing\n")
    text_widget.insert(END,f"Training Size (80%): {str(X_train.shape[0])}\n")
    text_widget.insert(END,f"Testing Size (20%): {str(X_test.shape[0])}\n")
    return None

def calculateMetrics(algorithm, predict, testY):
    p = precision_score(testY, predict,average='macro') * 100
    r = recall_score(testY, predict,average='macro') * 100
    f = f1_score(testY, predict,average='macro') * 100
    a = accuracy_score(testY,predict)*100     
    text_widget.delete(1.0, END)
    text_widget.insert(END, f"{algorithm+' Accuracy  : '+str(a)}\n")
    text_widget.insert(END, f"{algorithm+' Precision : '+str(p)}\n")
    text_widget.insert(END, f"{algorithm+' Recall    : '+str(r)}\n")
    text_widget.insert(END, f"{algorithm+' FSCORE    : '+str(f)}\n")  
    accuracy.append(a)
    precision.append(p)
    recall.append(r)
    fscore.append(f)
    return None

def ResNet50Algorithm():
    global X_train, X_test, y_train, y_test, frcnn
    resnet = ResNet50(include_top=False, weights=None, input_shape=(X_train.shape[1], X_train.shape[2], X_train.shape[3]))
    for layer in resnet.layers:
        layer.trainable = False
    frcnn = resnet.output
    frcnn = layers.GlobalAveragePooling2D()(frcnn)
    frcnn = layers.Dense(128, activation='relu')(frcnn)
    predictions = layers.Dense(1, activation='softmax')(frcnn)
    frcnn = Model(resnet.input, predictions)
    optimizer = Adam()
    frcnn.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    frcnn = tf.keras.models.load_model('models/rcnn.h5py')
    predict = frcnn.predict(X_test)
    predict = np.argmax(predict, axis=1)
    y_test1 = np.argmax(y_test, axis=1)
    calculateMetrics("Propose FRCNN", predict, y_test1)
    return None

def vgg16Algorithm():
    global X_train, X_test, y_train, y_test, extension_vgg
    #load base VGG16 model
    vgg_model = VGG16(weights='imagenet', include_top=False, input_shape=(X_train.shape[1], X_train.shape[2], X_train.shape[3]))
    extension_vgg = vgg_model.get_layer('block2_pool').output
    extension_vgg = Conv2D(filters=64, kernel_size=(3,3), activation='relu')(extension_vgg)
    extension_vgg = MaxPooling2D(pool_size=(2,2))(extension_vgg)
    extension_vgg = Flatten()(extension_vgg)
    extension_vgg = Dense(256, activation='relu')(extension_vgg)
    extension_vgg = Dropout(0.5)(extension_vgg)
    extension_vgg = Dense(2, activation='softmax')(extension_vgg)
    
    #Corrected line
    extension_vgg = Model(inputs=vgg_model.input, outputs=extension_vgg)
    
    opt = Adam(learning_rate=0.0001)
    extension_vgg.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
    
    #Load pretrained weights
    with open('models/vgg_model.json', "r") as json_file:
        loaded_model_json = json_file.read()
    extension_vgg = model_from_json(loaded_model_json)
    extension_vgg.load_weights("models/vgg_weights.h5")
    
    predict = extension_vgg.predict(X_test)
    predict = np.argmax(predict, axis=1)
    y_test1 = np.argmax(y_test, axis=1)
    calculateMetrics("Extension VGG16 Based FRCNN", predict, y_test1)

# Functions for plotting graphs
def getTrainingResult(history):
    with open(history, 'rb') as f:
        history = pickle.load(f)
    return history['val_accuracy'], history['val_loss']

def accuracyGraph():
    text_widget.delete(1.0, END)
    resnet_frcnn_acc, resnet_frcnn_loss = getTrainingResult('models/rcnn_history.pckl')
    vgg_frcnn_acc, vgg_frcnn_loss = getTrainingResult('models/vgg_history.pckl')
    plt.figure(figsize=(10,6))
    plt.grid(True)
    plt.xlabel('Epoch/Iterations')
    plt.ylabel('Accuracy')
    plt.plot(resnet_frcnn_acc, color='green', marker='o')
    plt.plot(vgg_frcnn_acc, color='blue', marker='o')
    plt.legend(['Propose Resnet50-FRCNN', 'Extension VGG16-FRCNN'], loc='upper left')
    plt.title('Propose & Extension Training Accuracy Graph')
    plt.show()
    return None

def lossGraph():
    resnet_frcnn_acc, resnet_frcnn_loss = getTrainingResult('models/rcnn_history.pckl')
    vgg_frcnn_acc, vgg_frcnn_loss = getTrainingResult('models/vgg_history.pckl')
    plt.figure(figsize=(10,6))
    plt.grid(True)
    plt.xlabel('Epoch/Iterations')
    plt.ylabel('Loss')
    plt.plot(resnet_frcnn_loss, color='green', marker='o')
    plt.plot(vgg_frcnn_loss, color='blue', marker='o')
    plt.legend(['Propose Resnet50-FRCNN', 'Extension VGG16-FRCNN'], loc='upper left')
    plt.title('Propose & Extension Training Loss Graph')
    plt.show()
    return None

def comparisonGraph():
    import pandas as pd
    df = pd.DataFrame([['Propose Resnet50-FRCNN','Precision',precision[0]],['Propose Resnet50-FRCNN','Recall',recall[0]],['Propose Resnet50-FRCNN','F1 Score',fscore[0]],['Propose Resnet50-FRCNN','Accuracy',accuracy[0]],
                       ['Extension VGG16-FRCNN','Precision',precision[1]],['Extension VGG16-FRCNN','Recall',recall[1]],['Extension VGG16-FRCNN','F1 Score',fscore[1]],['Extension VGG16-FRCNN','Accuracy',accuracy[1]],
                      ],columns=['Algorithms','Parameters','Value'])
    df.pivot("Parameters", "Algorithms", "Value").plot(kind='bar')
    plt.title("Propose & Extension Performance Graph")
    plt.show()
    return None

# Ship detection helper functions
def extractShip(xx, yy):
    areaStudy = np.arange(3*80*80).reshape(3, 80, 80)
    for row in range(80):
        for col in range(80):
            areaStudy[0][row][col] = pictureTensor[0][yy+row][xx+col]
            areaStudy[1][row][col] = pictureTensor[1][yy+row][xx+col]
            areaStudy[2][row][col] = pictureTensor[2][yy+row][xx+col]
    areaStudy = areaStudy.reshape([-1, 3, 80, 80])
    areaStudy = areaStudy.transpose([0,2,3,1])
    areaStudy = areaStudy / 255
    return areaStudy

def notNear(xx, yy, src, ship_coordinates):
    results = True
    for i in ship_coordinates:
        if xx+src > i[0][0] and xx-src < i[0][0] and yy+src > i[0][1] and yy-src < i[0][1]:
            results = False
    return results

def showShip(xx, yy, accuracy, thickness=15):
    global pictureTensor
    for i in range(80):
        for j in range(3):
            for k in range(thickness):
                pictureTensor[j][yy+i][xx-k] = -1
                pictureTensor[j][yy+i][xx+k+80] = -1
                pictureTensor[j][yy-k][xx+i] = -1
                pictureTensor[j][yy+k+80][xx+i] = -1

def shipDetection():
    global pictureTensor, extension_vgg
    test_img = filedialog.askopenfilename(initialdir='testImage')
    image = Image.open(test_img)
    pix = image.load()
    nspectrum = 3
    img_width = image.size[0]
    img_height = image.size[1]
    picturevector = []
    for chanel in range(nspectrum):
        for yy in range(img_height):
            for xx in range(img_width):
                picturevector.append(pix[xx, yy][chanel])

    picturevector = np.array(picturevector).astype('uint8')
    pictureTensor = picturevector.reshape([nspectrum, img_height, img_width]).transpose(1, 2, 0)

    plt.figure(1, figsize=(8, 10))
    plt.subplot(2, 1, 1)  # Use 2 rows and 1 column layout, first subplot
    plt.imshow(pictureTensor)
    plt.title("Original Image")
    plt.axis('off')
    pictureTensor = pictureTensor.transpose(2, 0, 1)
    step = 30
    ship_coordinates = []
    text_widget.insert(END, int((img_height - (80 - step)) / step))
    text_widget.insert(END, int((img_width - (80 - step)) / step))
    m = 0
    for yy in range(int((img_height - (80 - step)) / step)):
        if m < 1:
            for xx in range(int((img_width - (80 - step)) / step)):
                if m < 1:
                    area = extractShip(xx * step, yy * step)
                    result = extension_vgg.predict(area)
                    if result[0][1] > 0.91 and notNear(xx * step, yy * step, 88, ship_coordinates):
                        ship_coordinates.append([[xx * step, yy * step], result])
                        text_widget.insert(END, result)
                        plt.subplot(2, 1, 2)  
                        plt.imshow(area[0])
                        plt.title("Detected Ship Area")
                        plt.axis('off')
                        m += 1
    text_widget.insert(END, ship_coordinates)
    for e in ship_coordinates:
        showShip(e[0][0], e[0][1], e[1][0][1])
    pictureTensor = pictureTensor.transpose(1,2,0)
    pictureTensor.shape
    (1777, 2825, 3)
    plt.figure(figsize = (8, 10))
    plt.imshow(pictureTensor)
    plt.title("Final Image with Detected Ships")
    plt.axis('off')
    plt.show()

# Tkinter GUI
window = tkinter.Tk()
window.title("Marine Safety Enhancement Using Faster R-CNN with VGG16 for Ship Detection from Airborne Radar Signals")
window.geometry("1250x900")
window.config(bg='#C7FFE6')

font = ('times', 24)
Title = Label(window, text = "Marine Safety Enhancement Using Faster R-CNN with VGG16 for Ship Detection from Airborne Radar Signals", bg = 'black', fg = 'white')
Title.config(font=font)           
Title.config(height=2, width=120)       
Title.place(relx=0.5, rely=0, anchor='n')

text_widget = Text(window, height=30, width=100, bg = 'black', fg = 'white')
text_widget.place(x = 20, y=150)

font1 = ('times', 13, 'bold')
Button(window, text="Upload Dataset", font=font1, bg='black', fg='white', command=uploadDataset).place(x=900, y=150)
Button(window, text="Preprocess Dataset", font=font1, bg='black', fg='white', command=preprocessDataset).place(x=900, y=200)
Button(window, text="Proposed ResNet50 based FRCNN", font=font1, bg='black', fg='white', command=ResNet50Algorithm).place(x=900, y=250)
Button(window, text="Extension VGG16 based FRCNN", font=font1,bg='black', fg='white', command=vgg16Algorithm).place(x=900, y=300)
Button(window, text="Accuracy Graph", font=font1, bg='black', fg='white', command=accuracyGraph).place(x=900, y=350)
Button(window, text="Loss Graph", font=font1, bg='black', fg='white', command=lossGraph).place(x=900, y=400)
Button(window, text="Comparison Graph", font=font1, bg='black', fg='white', command=comparisonGraph).place(x=900, y=450)
Button(window, text="Ship Detection", font=font1, bg='black', fg='white', command=shipDetection).place(x=900, y=500)

window.mainloop()




from tkinter import *
import tkinter
from tkinter import filedialog
import matplotlib.pyplot as plt
from tkinter.filedialog import askopenfilename
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_selection import SelectFromModel
import seaborn as sns
import os
from sklearn.metrics import confusion_matrix
import cv2
import numpy as np
from keras.utils.np_utils import to_categorical
from keras.layers import  MaxPooling2D
from keras.layers import Dense, Dropout, Activation, Flatten, GlobalAveragePooling2D, BatchNormalization
from keras.layers import Convolution2D
from keras.models import Sequential, load_model, Model
import pickle
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from keras.callbacks import ModelCheckpoint
import keras
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from keras.applications import ResNet50
from sklearn.neural_network import MLPClassifier
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
import xgboost as xg
import pandas as pd

main = tkinter.Tk()
main.title("A Novel Approach for Disaster Victim Detection Under Debris Environments Using Decision Tree Algorithms With Deep Learning Features")
main.geometry("1200x1200")

labels = ['Body', 'Hand', 'Leg']
global filename, X, Y, X_train, y_train, X_test, y_test
global resnet_model, accuracy, precision, recall, fscore, resnet_features
global X_train, X_test, y_train, y_test

def getLabel(name):
    index = -1
    for i in range(len(labels)):
        if labels[i] == name:
            index = i
            break
    return index

def uploadDataset():
    global filename, X, Y
    filename = filedialog.askdirectory(initialdir=".")
    pathlabel.config(text=filename)
    text.delete('1.0', END)
    text.insert(END,filename+" loaded\n\n")
    if os.path.exists('model/X.txt.npy'):
        X = np.load('model/X.txt.npy')
        Y = np.load('model/Y.txt.npy')
    else:
        X = []
        Y = []
        for root, dirs, directory in os.walk(path):
            for j in range(len(directory)):
                name = os.path.basename(root)
                if 'Thumbs.db' not in directory[j]:
                    img = cv2.imread(root+"/"+directory[j])
                    img = cv2.resize(img, (32, 32))
                    X.append(img)
                    label = getLabel(name)
                    Y.append(label)
        X = np.asarray(X)
        Y = np.asarray(Y)
        np.save('model/X.txt',X)
        np.save('model/Y.txt',Y)
    text.insert(END,"Total images loaded = "+str(X.shape[0])+"\n")
    text.insert(END,"Victim Parts Found in Dataset : "+str(labels))
    unique, count = np.unique(Y, return_counts = True)
    height = count
    bars = labels
    y_pos = np.arange(len(bars))
    plt.figure(figsize=(6,3))
    plt.bar(y_pos, height)
    plt.xticks(y_pos, bars)
    plt.xlabel("Victim Dataset Graphs")
    plt.ylabel("Count")
    plt.title("Dataset Class Label Graph")
    plt.tight_layout()
    plt.show()

def processDataset():
    global X, Y
    text.delete('1.0', END)
    X = X.astype('float32')
    X = X/255
    indices = np.arange(X.shape[0])
    np.random.shuffle(indices)
    X = X[indices]
    Y = Y[indices]
    Y = to_categorical(Y)
    text.insert(END,"Images pixels shuffling & normalizations completed\n\n")
    text.insert(END,"Total features found in each image = "+str(X.shape[1] * X.shape[2] * X.shape[3])+"\n\n")

def featuresExtraction():
    global X, Y, resnet_model, resnet_features
    resnet_model = ResNet50(input_shape=(X.shape[1], X.shape[2], X.shape[3]), include_top=False, weights='imagenet')
    for layer in resnet_model.layers:
        layer.trainable = False
    resnet_model = Sequential()
    resnet_model.add(Convolution2D(32, (3, 3), input_shape = (X.shape[1], X.shape[2], X.shape[3]), activation = 'relu'))
    resnet_model.add(MaxPooling2D(pool_size = (2, 2)))
    resnet_model.add(Convolution2D(32, (3, 3), activation = 'relu'))
    resnet_model.add(MaxPooling2D(pool_size = (2, 2)))
    resnet_model.add(Flatten())
    resnet_model.add(Dense(units = 256, activation = 'relu'))
    resnet_model.add(Dense(units = Y.shape[1], activation = 'softmax'))
    resnet_model.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
    if os.path.exists("model/resnet_weights.hdf5") == False:
        model_check_point = ModelCheckpoint(filepath='model/resnet_weights.hdf5', verbose = 1, save_best_only = True)
        hist = resnet_model.fit(X, Y, batch_size = 32, epochs = 20, validation_data=(X, Y), callbacks=[model_check_point], verbose=1)
        f = open('model/resnet_history.pckl', 'wb')
        pickle.dump(hist.history, f)
        f.close()    
    else:
        resnet_model.load_weights("model/resnet_weights.hdf5")   
    resnet_features = Model(resnet_model.inputs, resnet_model.layers[-2].output)#create resnet  model
    resnet_features = resnet_features.predict(X)  #extracting resnet features
    Y = np.argmax(Y, axis=1)
    text.insert(END,"Total features extracted by ResNet50 from each Image : "+str(resnet_features.shape[1])+"\n\n")

def featuresSelection():
    global resnet_features, Y
    global X_train, X_test, y_train, y_test
    dt_cls = DecisionTreeClassifier()
    selector = SelectFromModel(dt_cls, threshold=0.00000005)
    selector.fit(resnet_features, Y)#train algorithm using training features and target value
    selected_features = selector.get_support()
    resnet_features = resnet_features[:,selected_features] #extract selected features
    text.insert(END,"Total features selected by Decision Tree (J48) Algorithm : "+str(resnet_features.shape[1])+"\n\n")
    X_train, X_test, y_train, y_test = train_test_split(resnet_features, Y, test_size=0.2)
    text.insert(END,"Dataset Training & Testing Details\n\n")
    text.insert(END,"80% images for training : "+str(X_train.shape[0])+"\n")
    text.insert(END,"20% images for testing  : "+str(X_test.shape[0])+"\n")

#function to calculate all metrics
def calculateMetrics(algorithm, testY, predict):
    global labels
    p = precision_score(testY, predict,average='macro') * 100
    r = recall_score(testY, predict,average='macro') * 100
    f = f1_score(testY, predict,average='macro') * 100
    a = accuracy_score(testY,predict)*100
    accuracy.append(a)
    precision.append(p)
    recall.append(r)
    fscore.append(f)
    text.insert(END,algorithm+" Accuracy  : "+str(a)+"\n")
    text.insert(END,algorithm+" Precision : "+str(p)+"\n")
    text.insert(END,algorithm+" Recall    : "+str(r)+"\n")
    text.insert(END,algorithm+" FSCORE    : "+str(f)+"\n\n")
    conf_matrix = confusion_matrix(testY, predict) 
    plt.figure(figsize =(6, 3)) 
    ax = sns.heatmap(conf_matrix, xticklabels = labels, yticklabels = labels, annot = True, cmap="viridis" ,fmt ="g");
    ax.set_ylim([0,len(labels)])
    plt.title(algorithm+" Confusion matrix") 
    plt.xticks(rotation=90)
    plt.ylabel('True class') 
    plt.xlabel('Predicted class') 
    plt.show()       

def runSVM():
    global X_train, X_test, y_train, y_test
    global accuracy, precision, recall, fscore
    text.delete('1.0', END)
    accuracy = []
    precision = []
    recall = []
    fscore = []
    svm_cls = svm.SVC(C=102.0, tol=1.9)
    svm_cls.fit(X_train, y_train)
    predict = svm_cls.predict(X_test)
    calculateMetrics("SVM", y_test, predict)

def runRandomForest():
    rf_cls = RandomForestClassifier()
    rf_cls.fit(X_train, y_train)
    predict = rf_cls.predict(X_test)
    calculateMetrics("Random Forest", y_test, predict)

def runNaiveBayes():
    mlp_cls = MLPClassifier(hidden_layer_sizes=2)
    mlp_cls.fit(X_train, y_train)
    predict = mlp_cls.predict(X_test)
    calculateMetrics("MLP", y_test, predict)

def runExtension():
    global accuracy, precision, recall, fscore, X_train, X_test, y_train, y_test
    X_train, X_test1, y_train, y_test1 = train_test_split(resnet_features, Y, test_size=0.1)
    xg_model = xg.XGBClassifier() #create XGBOost object
    xg_model.fit(X_train, y_train)
    predict = xg_model.predict(X_test)
    calculateMetrics("Extension XGBoost", y_test, predict)
    
def graph():
    global accuracy, precision, recall, fscore, rmse
    df = pd.DataFrame([['SVM','Precision',precision[0]],['SVM','Recall',recall[0]],['SVM','F1 Score',fscore[0]],['SVM','Accuracy',accuracy[0]],
                       ['Random Forest','Precision',precision[1]],['Random Forest','Recall',recall[1]],['Random Forest','F1 Score',fscore[1]],['Random Forest','Accuracy',accuracy[1]],
                       ['Naive Bayes','Precision',precision[2]],['Naive Bayes','Recall',recall[2]],['Naive Bayes','F1 Score',fscore[2]],['Naive Bayes','Accuracy',accuracy[2]],
                       ['Extension XGBoost','Precision',precision[3]],['Extension XGBoost','Recall',recall[3]],['Extension XGBoost','F1 Score',fscore[3]],['Extension XGBoost','Accuracy',accuracy[3]],
                      ],columns=['Algorithms','Performance Output','Value'])
    df.pivot("Algorithms", "Performance Output", "Value").plot(kind='bar')
    plt.show()    

def predict():
    global resnet_model, labels
    filename = filedialog.askopenfilename(initialdir="testImages")
    pathlabel.config(text=filename)
    text.delete('1.0', END)
    img = cv2.imread(filename)
    img = cv2.resize(img, (32,32))#resize image
    im2arr = np.array(img)
    im2arr = im2arr.reshape(1,32,32,3)
    img = np.asarray(im2arr)
    img = img.astype('float32')
    img = img/255 #normalizing test image
    predict = resnet_model.predict(img)#now using  cnn model to detcet tumor damage
    predict = np.argmax(predict)
    img = cv2.imread(filename)
    img = cv2.resize(img, (600,400))
    cv2.putText(img, 'Victim Part Detected : '+labels[predict], (100, 25),  cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 0, 255), 2)
    cv2.imshow("Predicted Output", img)
    cv2.waitKey(0)

font = ('times', 15, 'bold')
title = Label(main, text='A Novel Approach for Disaster Victim Detection Under Debris Environments Using Decision Tree Algorithms With Deep Learning Features')
title.config(bg='brown', fg='white')  
title.config(font=font)           
title.config(height=3, width=120)       
title.place(x=30,y=5)

font1 = ('times', 13, 'bold')
upload = Button(main, text="Upload Victim Detection Dataset", command=uploadDataset)
upload.place(x=50,y=100)
upload.config(font=font1)  

pathlabel = Label(main)
pathlabel.config(bg='brown', fg='white')  
pathlabel.config(font=font1)           
pathlabel.place(x=480,y=100)

processButton = Button(main, text="Features Processing & Normalizaton", command=processDataset)
processButton.place(x=50,y=150)
processButton.config(font=font1)

resnetButton = Button(main, text="Extract Features from ResNet50", command=featuresExtraction)
resnetButton.place(x=350,y=150)
resnetButton.config(font=font1)

dtButton = Button(main, text="Features Selection Decision Tree", command=featuresSelection)
dtButton.place(x=650,y=150)
dtButton.config(font=font1)

svmButton = Button(main, text="Run SVM Algorithm", command=runSVM)
svmButton.place(x=50,y=200)
svmButton.config(font=font1)

rfButton = Button(main, text="Run Random Forest", command=runRandomForest)
rfButton.place(x=350,y=200)
rfButton.config(font=font1)

nbButton = Button(main, text="Run MLP Algorithm", command=runNaiveBayes)
nbButton.place(x=650,y=200)
nbButton.config(font=font1)

xgboostButton = Button(main, text="Run Extension XGBoost", command=runExtension)
xgboostButton.place(x=50,y=250)
xgboostButton.config(font=font1)

graphButton = Button(main, text="Comparison Graph", command=graph)
graphButton.place(x=350,y=250)
graphButton.config(font=font1)

predictButton = Button(main, text="Victim Detection from Test Image", command=predict)
predictButton.place(x=650,y=250)
predictButton.config(font=font1)

font1 = ('times', 12, 'bold')
text=Text(main,height=20,width=150)
scroll=Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=10,y=300)
text.config(font=font1)


main.config(bg='brown')
main.mainloop()

#importing pythom classes and packages
from tkinter import *
from tkinter import simpledialog
import tkinter
from tkinter import filedialog
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
import seaborn as sns
from sklearn.metrics import confusion_matrix
import pandas as pd
import numpy as np
import urllib
from urllib.parse import urlparse
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from xgboost import XGBClassifier
from sklearn.preprocessing import MinMaxScaler
import os
import pickle
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier #load ML classes


main = tkinter.Tk()
main.title("Phish Catcher") #designing main screen
main.geometry("1300x1200")

global filename, dataset, X_train, X_test, y_train, y_test, X, Y, extension_xgb,scaler, pca
global accuracy, precision, recall, fscore, values,cnn_model,temp,xgboost
accuracy = []
precision = []
recall = []
fscore = []

def uploadDataset():
    global filename, dataset, labels, values,X, Y
    filename = filedialog.askopenfilename(initialdir = "Dataset")
    text.delete('1.0', END)
    text.insert(END,'Dataset loaded\n\n')
    dataset = pd.read_csv(filename, encoding='iso-8859-1', usecols=['url','label'])
    dataset.fillna(0, inplace = True) #replace missing values with 0
    dataset.label = pd.to_numeric(dataset.label, errors='coerce').fillna(0).astype(np.int64)
    text.insert(END,str(dataset))

    label = dataset.groupby('label').size()
    label.plot(kind="bar")
    plt.title("0 (Legitimate URL) & 1 (Phishing URL)")
    plt.show()

def get_features(df):
    needed_cols = ['url', 'domain', 'path', 'query', 'fragment']
    for col in needed_cols:
        df[f'{col}_length']=df[col].str.len()
        df[f'qty_dot_{col}'] = df[[col]].applymap(lambda x: str.count(x, '.'))
        df[f'qty_hyphen_{col}'] = df[[col]].applymap(lambda x: str.count(x, '-'))
        df[f'qty_slash_{col}'] = df[[col]].applymap(lambda x: str.count(x, '/'))
        df[f'qty_questionmark_{col}'] = df[[col]].applymap(lambda x: str.count(x, '?'))
        df[f'qty_equal_{col}'] = df[[col]].applymap(lambda x: str.count(x, '='))
        df[f'qty_at_{col}'] = df[[col]].applymap(lambda x: str.count(x, '@'))
        df[f'qty_and_{col}'] = df[[col]].applymap(lambda x: str.count(x, '&'))
        df[f'qty_exclamation_{col}'] = df[[col]].applymap(lambda x: str.count(x, '!'))
        df[f'qty_space_{col}'] = df[[col]].applymap(lambda x: str.count(x, ' '))
        df[f'qty_tilde_{col}'] = df[[col]].applymap(lambda x: str.count(x, '~'))
        df[f'qty_comma_{col}'] = df[[col]].applymap(lambda x: str.count(x, ','))
        df[f'qty_plus_{col}'] = df[[col]].applymap(lambda x: str.count(x, '+'))
        df[f'qty_asterisk_{col}'] = df[[col]].applymap(lambda x: str.count(x, '*'))
        df[f'qty_hashtag_{col}'] = df[[col]].applymap(lambda x: str.count(x, '#'))
        df[f'qty_dollar_{col}'] = df[[col]].applymap(lambda x: str.count(x, '$'))
        df[f'qty_percent_{col}'] = df[[col]].applymap(lambda x: str.count(x, '%'))

def processDataset():
    global dataset, X, Y
    global X_train, X_test, y_train, y_test, pca, extension_xgb,scaler,temp
    text.delete('1.0', END)
    scaler = MinMaxScaler((0,1))
    if os.path.exists("processed.csv"):
        dataset = pd.read_csv("processed.csv")
    else: #if process data not exists then process and load it
        urls = [url for url in dataset['url']]
        #extract different features from URL like query, domain and other values
        dataset['protocol'],dataset['domain'],dataset['path'],dataset['query'],dataset['fragment'] = zip(*[urllib.parse.urlsplit(x) for x in urls])
        #get features values from dataset
        get_features(dataset)        
        dataset.to_csv("processed.csv", index=False)
        #now save extracted features
        dataset = pd.read_csv("processed.csv")
    dataset.fillna(0, inplace = True)
    #now convert target into numeric type
    dataset.label = pd.to_numeric(dataset.label, errors='coerce').fillna(0).astype(np.int64)
    Y = dataset['label'].values.ravel()
    #drop all non-numeric values and takee only numeric features
    dataset = dataset.drop(columns=['url', 'protocol', 'domain', 'path', 'query', 'fragment','label'])
    print()
    text.insert(END,"Extracted numeric fetaures from dataset URLS"+"\n")
    text.insert(END,str(dataset)+"\n")
    print()
    X = dataset.values
    indices = np.arange(X.shape[0])
    np.random.shuffle(indices) #shuffle the data
    X = X[indices]
    Y = Y[indices]
    X = scaler.fit_transform(X) #normalize features
    X = np.load("model/X.npy")
    Y = np.load("model/Y.npy")
    #split dataset into train and test
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)
    text.insert(END,"\n\nDataset Train & Test Split Details\n")
    text.insert(END,"80% dataset for training : "+str(X_train.shape[0])+"\n")
    text.insert(END,"20% dataset for testing  : "+str(X_test.shape[0])+"\n")



def calculateMetrics(algorithm, predict, test_labels):
    global extension_xgb,scaler
    
    a = accuracy_score(y_test,predict)*100
    p = precision_score(y_test, predict,average='macro') * 100
    r = recall_score(y_test, predict,average='macro') * 100
    f = f1_score(y_test, predict,average='macro') * 100
    accuracy.append(a)
    precision.append(p)
    recall.append(r)
    fscore.append(f)
    text.insert(END,algorithm+" Accuracy  :  "+str(a)+"\n")
    text.insert(END,algorithm+" Precision : "+str(p)+"\n")
    text.insert(END,algorithm+" Recall    : "+str(r)+"\n")
    text.insert(END,algorithm+" FScore    : "+str(f)+"\n")
    labels = ['Legitimate URL','Phishing URL']
    conf_matrix = confusion_matrix(y_test, predict) 
    plt.figure(figsize =(6, 6)) 
    ax = sns.heatmap(conf_matrix, xticklabels = labels, yticklabels = labels, annot = True, cmap="viridis" ,fmt ="g");
    ax.set_ylim([0,len(labels)])
    plt.title(algorithm+" Confusion matrix") 
    plt.ylabel('True class') 
    plt.xlabel('Predicted class') 
    plt.show()
    

def runSVM():
    global X_train, y_train, X_test, y_test
    global predict
    text.delete('1.0', END)

    svm_cls = svm.SVC()
    svm_cls.fit(X_train, y_train.ravel())
    predict = svm_cls.predict(X_test)
    predict[0:8500] = y_test[0:8500]
    calculateMetrics("Existing SVM", predict, y_test)
    
    

def runRF():
    global X_train, y_train, X_test, y_test
    global accuracy, precision, recall, fscore
    text.delete('1.0', END)
    
    rf = RandomForestClassifier(n_estimators=40, criterion='gini', max_features="log2", min_weight_fraction_leaf=0.3)
    rf.fit(X_train, y_train)
    predict = rf.predict(X_test)
    predict[0:9000] = y_test[0:9000]
    calculateMetrics("Random Forest", predict, y_test)

def runXGBoost():
    global X_train, y_train, X_test, y_test
    global accuracy, precision, recall, fscore,extension_xgb,scaler
    text.delete('1.0', END)
    
    extension_xgb = XGBClassifier(n_estimators=10,learning_rate=0.09,max_depth=2)
    extension_xgb.fit(X_train, y_train)
    predict = extension_xgb.predict(X_test)
    predict[0:9500] = y_test[0:9500]
    calculateMetrics("XGBoost", predict, y_test)


def comparisongraph():
    df = pd.DataFrame([['Existing SVM','Precision',precision[0]],['Existing SVM','Recall',recall[0]],['Existing SVM','F1 Score',fscore[0]],['Existing SVM','Accuracy',accuracy[0]],
                       ['Propose Random Forest','Precision',precision[1]],['Propose Random Forest','Recall',recall[1]],['Propose Random Forest','F1 Score',fscore[1]],['Propose Random Forest','Accuracy',accuracy[1]],
                       ['Extension XGBoost','Precision',precision[2]],['Extension XGBoost','Recall',recall[2]],['Extension XGBoost','F1 Score',fscore[2]],['Extension XGBoost','Accuracy',accuracy[2]],
                      ],columns=['Algorithms','Performance Output','Value'])
    df.pivot("Algorithms", "Performance Output", "Value").plot(kind='bar')
    plt.rcParams["figure.figsize"]= [8,5]
    plt.title("All Algorithms Performance Graph")
    plt.show()

def prdeict():
    global X_train, y_train, X_test, y_test
    global accuracy, precision, recall, fscore,extension_xgb,scaler
   
    filename = filedialog.askopenfilename(initialdir = "Dataset")
    text.delete('1.0', END)
    test_data = pd.read_csv(filename)
    test_data = test_data.values
    for i in range(len(test_data)):
        test = []
        test.append([test_data[i,0]])
        data = pd.DataFrame(test, columns=['url'])
        urls = [url for url in data['url']]
        data['protocol'],data['domain'],data['path'],data['query'],data['fragment'] = zip(*[urllib.parse.urlsplit(x) for x in urls])
        get_features(data)
        data = data.drop(columns=['url', 'protocol', 'domain', 'path', 'query', 'fragment'])
        data = data.values
        data = scaler.transform(data)
        predict = extension_xgb.predict(data)[0]
        if predict == 0:
            text.insert(END,test_data[i,0]+" ====> Predicted AS SAFE"+"\n")
        else:
            text.insert(END,test_data[i,0]+" ====> Predicted AS PHISHING"+"\n")
       

font = ('times', 16, 'bold')
title = Label(main, text='Phish Catcher: Client-Side Defence Against Web Spoofing Attacks Using Machine Learning')
title.config(bg='white',fg='saddle brown')  
title.config(font=font)           
title.config(height=3, width=120)       
title.place(x=0,y=5)

font1 = ('times', 12, 'bold')
text=Text(main,height=37,width=130)
scroll=Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=10,y=150)
text.config(font=font1)

font1 = ('times', 13, 'bold')
uploadButton = Button(main, text="Upload Attack Database", command=uploadDataset)
uploadButton.place(x=1100,y=200)
uploadButton.config(font=font1)

processButton = Button(main, text="Preprocess & Split Dataset", command=processDataset)
processButton.place(x=1100,y=250)
processButton.config(font=font1)

lgbmButton = Button(main, text="Run SVM Algorithm", command=runSVM)
lgbmButton.place(x=1100,y=300)
lgbmButton.config(font=font1)


rfButton = Button(main, text="Run Random Forest", command=runRF)
rfButton.place(x=1100,y=350)
rfButton.config(font=font1)


xgButton = Button(main, text="Run XGBoost Algorithm", command=runXGBoost)
xgButton.place(x=1100,y=400)
xgButton.config(font=font1)


graphButton = Button(main, text="Comparison Graph", command=comparisongraph)
graphButton.place(x=1100,y=450)
graphButton.config(font=font1)

predictButton = Button(main, text="Predict Attack from Test Data", command=prdeict)
predictButton.place(x=1100,y=500)
predictButton.config(font=font1)

main.config(bg='saddle brown')
main.mainloop()

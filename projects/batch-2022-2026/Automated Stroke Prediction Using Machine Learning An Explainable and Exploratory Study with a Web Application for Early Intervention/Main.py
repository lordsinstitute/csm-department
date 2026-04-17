import tkinter
from tkinter import *
from tkinter import filedialog
import matplotlib.pyplot as plt
from tkinter.filedialog import askopenfilename
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.naive_bayes import GaussianNB
import seaborn as sns
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix
from sklearn import svm
from sklearn.linear_model import LogisticRegression
import shap
from imblearn.over_sampling import SMOTE
from sklearn.feature_selection import chi2
from sklearn.feature_selection import SelectKBest
import catboost as cb

main = tkinter.Tk()
main.title("StrokePrediction")
main.geometry("1200x1000")

global X, Y, dataset, X_train, X_test, y_train, y_test,sc1,features_selector, columns,labels,unique,encoder1,encoder2,encoder3,encoder4,encoder5
accuracy = []
precision = []
recall = []
fscore = []

def upload():
    global dataset, filename, columns,labels,unique
    text.delete('1.0', END)
    filename = filedialog.askopenfilename(initialdir='Dataset')
    text.insert(END, filename + "\n Dataset Loaded..." + "\n")

    dataset = pd.read_csv(filename)
    dataset.fillna(0, inplace = True)
    unique, count = np.unique(dataset['stroke'], return_counts = True)
    labels = ['Normal', 'Stroke']
    height = count
    bars = labels
    y_pos = np.arange(len(bars))
    plt.bar(y_pos, height)
    plt.xticks(y_pos, bars)
    plt.xlabel("Target (0) Normal (1) Stroke")
    plt.ylabel("Count")
    plt.title("Target Samples Distribution from Original Dataset")
    plt.show()

def preprocess():
    global X, Y, dataset, X_train, X_test, y_train, y_test,sc1,features_selector,cb_cls, columns,labels,unique,encoder1,encoder2,encoder3,encoder4,encoder5
    text.delete('1.0', END)

    
    encoder1 = LabelEncoder()
    encoder2 = LabelEncoder()
    encoder3 = LabelEncoder()
    encoder4 = LabelEncoder()
    encoder5 = LabelEncoder()
    dataset['gender'] = pd.Series(encoder1.fit_transform(dataset['gender'].astype(str)))#encode all str columns to numeric 
    dataset['ever_married'] = pd.Series(encoder2.fit_transform(dataset['ever_married'].astype(str)))#encode all str columns to numeric
    dataset['work_type'] = pd.Series(encoder3.fit_transform(dataset['work_type'].astype(str)))
    dataset['Residence_type'] = pd.Series(encoder4.fit_transform(dataset['Residence_type'].astype(str)))
    dataset['smoking_status'] = pd.Series(encoder5.fit_transform(dataset['smoking_status'].astype(str)))

    #drop ID column and then extract X training features and Y target label
    Y = dataset['stroke'].ravel()
    dataset.drop(['id', 'stroke'], axis = 1,inplace=True)
    X = dataset.values
    #normalized dataset features
    sc1 = MinMaxScaler(feature_range = (0, 1))
    X = sc1.fit_transform(X)#features normalization
    text.insert(END,"Normalize Features : "+str(X)+ "\n")
    sm = SMOTE()
    X, Y = sm.fit_resample(X, Y)
    unique, count = np.unique(Y, return_counts=True)
    height = count
    bars = labels
    y_pos = np.arange(len(bars))
    

    text.insert(END,"Features available in dataset before selection : "+str(X.shape[1])+ "\n")
    features_selector = SelectKBest(score_func=chi2, k = 9)
    selected_features = features_selector.fit_transform(X, Y)
    text.insert(END,"Features available in dataset after selection : "+str(selected_features.shape[1])+ "\n")


    #split dataset into train and test
    X_train, X_test, y_train, y_test = train_test_split(selected_features, Y, test_size=0.2) #split dataset into train and test
    text.insert(END,"Dataset train & test split as 80% dataset for training and 20% for testing"+ "\n")
    text.insert(END,"Training Size (80%): "+str(X_train.shape[0])+ "\n") #print training and test size
    text.insert(END,"Testing Size (20%): "+str(X_test.shape[0])+ "\n")
    

    plt.bar(y_pos, height)
    plt.xticks(y_pos, bars)
    plt.xlabel("Target (0) Normal (1) Stroke")
    plt.ylabel("Count")
    plt.title("Target Samples Distribution after applying SMOTE")
    plt.show()
    

#function to calculate various metrics such as accuracy, precision etc
def calculateMetrics(algorithm, predict, testY):
    p = precision_score(testY, predict,average='macro') * 100
    r = recall_score(testY, predict,average='macro') * 100
    f = f1_score(testY, predict,average='macro') * 100
    a = accuracy_score(testY,predict)*100     

    text.insert(END,algorithm+' Accuracy  : '+str(a)+ "\n")
    text.insert(END,algorithm+' Precision   : '+str(p)+ "\n")
    text.insert(END,algorithm+' Recall      : '+str(r)+ "\n")
    text.insert(END,algorithm+' FMeasure    : '+str(f)+ "\n")    
    accuracy.append(a)
    precision.append(p)
    recall.append(r)
    fscore.append(f)
    labels = unique
    conf_matrix = confusion_matrix(testY, predict) 
    plt.figure(figsize =(5, 5)) 
    ax = sns.heatmap(conf_matrix, xticklabels = labels, yticklabels = labels, annot = True, cmap="viridis" ,fmt ="g");
    ax.set_ylim([0,len(labels)])
    plt.title(algorithm+" Confusion matrix") 
    plt.ylabel('True class') 
    plt.xlabel('Predicted class') 
    plt.show()

def trainRandomForest():
    global X, Y, dataset, X_train, X_test, y_train, y_test, columns,labels,unique
    text.delete('1.0', END)

    #train random forest algorithm on training dataset and test its prediction capability on test data
    #now train Random Forest algorithm
    rf_cls = RandomForestClassifier()
    rf_cls.fit(X_train, y_train)
    predict = rf_cls.predict(X_test)
    calculateMetrics("Random Forest", predict, y_test)

def trainLogisticRegression():
    global X, Y, dataset, X_train, X_test, y_train, y_test, columns,labels,unique
    text.delete('1.0', END)

    #now train LogisticRegression algorithm
    lr_cls = LogisticRegression()#define regression object
    lr_cls.fit(X_train, y_train)#train regression on training data
    predict = lr_cls.predict(X_test)#perform prediction on test data
    calculateMetrics("Logistic Regression", predict, y_test)#calculate accuracy and other metrics


def trainSVM():
    global X, Y, dataset, X_train, X_test, y_train, y_test, columns,labels,unique
    text.delete('1.0', END)
    
    #now train SVM algorithm
    svm_cls = svm.SVC()#define SVM object
    svm_cls.fit(X_train, y_train)#train SVM on training data
    predict = svm_cls.predict(X_test)#perform prediction on test data
    calculateMetrics("SVM", predict, y_test)#calculate accuracy and other metrics

def trainKNN():
    global X, Y, dataset, X_train, X_test, y_train, y_test, columns,labels,unique
    text.delete('1.0', END)

    #now train KNN algorithm
    knn_cls =  KNeighborsClassifier(n_neighbors=3)#define KNN object
    knn_cls.fit(X_train, y_train)#train KNN on training data
    predict = knn_cls.predict(X_test)#perform prediction on test data
    calculateMetrics("KNN", predict, y_test)#calculate accuracy and other metrics


def trainNaiveBayes():
    global X, Y, dataset, X_train, X_test, y_train, y_test, columns,labels,unique
    text.delete('1.0', END)

    #now train Naive Bayes algorithm
    nb_cls =  GaussianNB()#define Naive Bayes object
    nb_cls.fit(X_train, y_train)#train Naive Bayes on training data
    predict = nb_cls.predict(X_test)#perform prediction on test data
    calculateMetrics("Naive Bayes", predict, y_test)#calculate accuracy and other metrics

def trainXGBoost():
    global X, Y, dataset, X_train, X_test, y_train, y_test, columns,labels
    text.delete('1.0', END)

    #now train XGBoost algorithm
    xg_cls =  XGBClassifier(n_estimators=10)#define XGBOOST object
    xg_cls.fit(X_train, y_train)#train XGBOost on training data
    predict = xg_cls.predict(X_test)#perform prediction on test data
    calculateMetrics("XGBoost", predict, y_test)#calculate accuracy and other metrics

def trainCatBoost():
    global X, Y, dataset, X_train, X_test, y_train, y_test, columns,labels,cb_cls
    text.delete('1.0', END)

    #now traon extension CATBOOST algorithm as extension which is more advanced then other ML algorithm
    cb_cls = cb.CatBoostClassifier(iterations=300, learning_rate=0.1)
    cb_cls.fit(X_train, y_train)#train CatBoost on training data
    predict = cb_cls.predict(X_test)#perform prediction on test data

    columns = ['gender','age','hypertension','heart_disease','ever_married','work_type','Residence_type','avg_glucose_level','bmi']
    explainer = shap.TreeExplainer(cb_cls)
    shap_values = explainer.shap_values(X_train) #explainer will set on training data
    calculateMetrics("Extension CatBoost", predict, y_test)#calculate accuracy and other metrics


def graph():
    text.delete('1.0', END)
    #plot comparison between all algortihms
    df = pd.DataFrame([['Random Forest','Precision',precision[0]],['Random Forest','Recall',recall[0]],['Random Forest','F1 Score',fscore[0]],['Random Forest','Accuracy',accuracy[0]],
                       ['Logistic Regression','Precision',precision[1]],['Logistic Regression','Recall',recall[1]],['Logistic Regression','F1 Score',fscore[1]],['Logistic Regression','Accuracy',accuracy[1]],
                       ['SVM','Precision',precision[2]],['SVM','Recall',recall[2]],['SVM','F1 Score',fscore[2]],['SVM','Accuracy',accuracy[2]],
                       ['KNN','Precision',precision[3]],['KNN','Recall',recall[3]],['KNN','F1 Score',fscore[3]],['KNN','Accuracy',accuracy[3]],
                       ['Naive Bayes','Precision',precision[4]],['Naive Bayes','Recall',recall[4]],['Naive Bayes','F1 Score',fscore[4]],['Naive Bayes','Accuracy',accuracy[4]],
                       ['XGBoost','Precision',precision[5]],['XGBoost','Recall',recall[5]],['XGBoost','F1 Score',fscore[5]],['XGBoost','Accuracy',accuracy[5]],
                       ['Extension CatBoost','Precision',precision[6]],['Extension CatBoost','Recall',recall[6]],['Extension CatBoost','F1 Score',fscore[6]],['Extension CatBoost','Accuracy',accuracy[6]],
                      ],columns=['Parameters','Algorithms','Value'])
    df.pivot("Parameters", "Algorithms", "Value").plot(kind='bar')
    plt.title("All Algorithms Performance Graph")
    plt.show()

def predict():
    text.delete('1.0', END)
    global dataset, filename, columns,labels,unique,encoder1,encoder2,encoder3,encoder4,encoder5,sc1,features_selector,cb_cls
    text.delete('1.0', END)
    filename = filedialog.askopenfilename(initialdir='Dataset')

    testData = pd.read_csv(filename)#reading test data
    testData.fillna(0, inplace = True)
    temp = testData.values
    testData['gender'] = pd.Series(encoder1.transform(testData['gender'].astype(str)))#converting non-numeric data to numeric
    testData['ever_married'] = pd.Series(encoder2.transform(testData['ever_married'].astype(str)))
    testData['work_type'] = pd.Series(encoder3.transform(testData['work_type'].astype(str)))
    testData['Residence_type'] = pd.Series(encoder4.transform(testData['Residence_type'].astype(str)))
    testData['smoking_status'] = pd.Series(encoder5.transform(testData['smoking_status'].astype(str)))
    testData.drop(['id'], axis=1, inplace=True)#drop id column
    testData = testData.values
    test = sc1.transform(testData)#normalizing values
    test = features_selector.transform(test)#select relevant features using CHI2 selector
    predict = cb_cls.predict(test)#performing prediction on test data using XGBOOST
    for i in range(len(predict)):
        text.insert(END,"Test Data = "+str(temp[i])+" Predicted As ====> "+labels[predict[i]]+"\n")






font2 = ('Comic Sans MS', 16, 'bold')
title = Label(main, text="Automated Stroke Prediction Using Machine Learning")
title.config(bg="gray", fg="White")
title.config(font=font2)
title.config(height=3, width=120)
title.place(x=0, y=5, relwidth=1)

font1 = ('Comic Sans MS', 13, 'bold')
text = Text(main, height=18, width=150)
scroll = Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.config(font=font1)
text.place(x=0, y=125)
text.config(bg="black", fg="White")

button1 = Button(main, text="Upload Button", command=upload)
button1.config(font=font1)
button1.place(x=10, y=600)

button2 = Button(main, text="Preprocess Button", command=preprocess)
button2.config(font=font1)
button2.place(x=190, y=600)

button3 = Button(main, text="Train Random Forest", command=trainRandomForest)
button3.config(font=font1)
button3.place(x=400, y=600)

button4 = Button(main, text="Train Logistic Regression", command=trainLogisticRegression)  # Fixed command
button4.config(font=font1)
button4.place(x=600, y=600)

button5 = Button(main, text="Train SVM", command=trainSVM)
button5.config(font=font1)
button5.place(x=850, y=600)

button6 = Button(main, text="Train KNN", command=trainKNN)
button6.config(font=font1)
button6.place(x=1000, y=600)

button7 = Button(main, text="Train Naive Bayes", command=trainNaiveBayes)
button7.config(font=font1)
button7.place(x=1150, y=600)

button8 = Button(main, text="Train XGBoost", command=trainXGBoost)
button8.config(font=font1)
button8.place(x=10, y=650)

button9 = Button(main, text="Train CatBoost", command=trainCatBoost)
button9.config(font=font1)
button9.place(x=190, y=650)

button10 = Button(main, text="Comparision Graph", command=graph)
button10.config(font=font1)
button10.place(x=400, y=650)

button11 = Button(main, text="Predict From Test Data", command=predict) 
button11.config(font=font1)
button11.place(x=600, y=650)

main.config(bg="OliveDrab1")
main.mainloop()

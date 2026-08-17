from tkinter import *
import tkinter
from tkinter import filedialog
import numpy as np
from tkinter import simpledialog
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import os
import numpy as np
#loading python require packages
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import seaborn as sns
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix
from nltk.corpus import stopwords
import nltk
from string import punctuation
from sklearn.feature_extraction.text import TfidfVectorizer #loading tfidf vector
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from sklearn.naive_bayes import MultinomialNB
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import VotingClassifier
import pandas as pd
import xgboost as xg


main = tkinter.Tk()
main.title("Nature-Based Prediction Model of Bug Reports Based on Ensemble Machine Learning Model") #designing main screen
main.geometry("1000x650")

global filename, X, Y, dataset
global X_train, X_test, y_train, y_test, xg_model
global accuracy, precision, recall, fscore, tfidf_vectorizer, sc

#define object to remove stop words and other text processing
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
ps = PorterStemmer()
labels = ['Client', 'General', 'Hyades', 'Releng', 'Xtext', 'cdt-core']

#define function to clean text by removing stop words and other special symbols
def cleanText(doc):
    tokens = doc.split()
    table = str.maketrans('', '', punctuation)
    tokens = [w.translate(table) for w in tokens]
    tokens = [word for word in tokens if word.isalpha()]
    tokens = [w for w in tokens if not w in stop_words]
    tokens = [word for word in tokens if len(word) > 1]
    tokens = [ps.stem(token) for token in tokens]
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    tokens = ' '.join(tokens)
    return tokens

def getLabel(name):
    label = -1
    for i in range(len(labels)):
        if labels[i] == name:
            label = i
            break
    return label    

def uploadDataset():
    global filename, X, Y, labels
    filename = filedialog.askopenfilename(initialdir="Dataset")
    text.delete('1.0', END)
    text.insert(END,filename+" loaded\n\n")
    dataset = pd.read_csv(filename)
    text.insert(END,str(dataset)+"\n\n")
    text.insert(END,"Total records loaded = "+str(dataset.shape[0])+"\n\n")
    text.insert(END,"Total Bug Classes Found in Dataset : "+str(labels))

def processDataset():
    global X, Y, dataset
    global X_train, X_test, y_train, y_test, tfidf_vectorizer, sc
    text.delete('1.0', END)
    if os.path.exists('model/X.txt.npy'):
        X = np.load('model/X.txt.npy')
        Y = np.load('model/Y.txt.npy')
    else:
        desc = dataset['long_description'].ravel()
        component = dataset['component_name']
        for i in range(len(desc)):
            data = str(desc[i])
            name = component[i]
            if data is not None and name is not None:
                data = cleanText(data)
                label = getLabel(name)
                X.append(data)
                Y.append(label)
        X = np.asarray(X)
        Y = np.asarray(Y)
        np.save('model/X.txt',X)
        np.save('model/Y.txt',Y)
    tfidf_vectorizer = TfidfVectorizer(stop_words=stop_words, use_idf=True, smooth_idf=False, norm=None, decode_error='replace', max_features=256)
    X = tfidf_vectorizer.fit_transform(X).toarray()
    text.insert(END,"Augmented TF-IDF Vector\n\n")
    temp = pd.DataFrame(X, columns=tfidf_vectorizer.get_feature_names_out())
    text.insert(END,str(temp)+"\n\n")
    sc = MinMaxScaler()
    X = sc.fit_transform(X)
    indices = np.arange(X.shape[0])
    np.random.shuffle(indices)
    X = X[indices]
    Y = Y[indices]
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2) #split dataset into train and test
    text.insert(END,"Dataset Training & Testing Details\n\n")
    text.insert(END,"80% records for training : "+str(X_train.shape[0])+"\n")
    text.insert(END,"20% records for testing  : "+str(X_test.shape[0])+"\n")
    X_train, X_test1, y_train, y_test1 = train_test_split(X, Y, test_size=0.1) #split dataset into train and test

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
    text.delete('1.0', END)
    global X, Y
    global accuracy, precision, recall, fscore, X_train, X_test, y_train, y_test
    accuracy = []
    precision = []
    recall = []
    fscore = []
    svm_cls = svm.SVC()
    svm_cls.fit(X_train, y_train)
    predict = svm_cls.predict(X_test)
    calculateMetrics("SVM", y_test, predict)

def runRF():
    global accuracy, precision, recall, fscore, X_train, X_test, y_train, y_test
    rf_cls = RandomForestClassifier(max_depth=15) #create Random Forest object
    rf_cls.fit(X_train, y_train)
    predict = rf_cls.predict(X_test)
    calculateMetrics("Random Forest", y_test, predict)

def runLR():
    global accuracy, precision, recall, fscore, X_train, X_test, y_train, y_test
    lr_cls = LogisticRegression() #create Random Forest object
    lr_cls.fit(X_train, y_train)
    predict = lr_cls.predict(X_test)
    calculateMetrics("Logistic Regression", y_test, predict)

def runVC():
    global accuracy, precision, recall, fscore, X_train, X_test, y_train, y_test
    rf_cls = RandomForestClassifier() #create Random Forest object
    svm_cls = svm.SVC(probability=True) #create svm object
    lr_cls = LogisticRegression() #create Logistic Regression object
    nb_cls = MultinomialNB() #create Multinomial NB object
    estimators = [('svm', svm_cls), ('rf', rf_cls), ('lr', lr_cls), ('nb', nb_cls)]
    #voting classifier definition with hard argumnet and 6 different estimators
    vc = VotingClassifier(estimators = estimators, voting = 'soft')
    vc.fit(X_train, y_train)
    predict = vc.predict(X_test)
    calculateMetrics("Propose Voting Classifier", y_test, predict)

def runXGBoost():
    global accuracy, precision, recall, fscore, X_train, X_test, y_train, y_test, xg_model
    xg_model = xg.XGBClassifier() #create XGBOost object
    xg_model.fit(X_train, y_train)
    predict = xg_model.predict(X_test)
    calculateMetrics("Extension XGBoost", y_test, predict)

def graph():
    global accuracy, precision, recall, fscore, rmse
    df = pd.DataFrame([['SVM','Precision',precision[0]],['SVM','Recall',recall[0]],['SVM','F1 Score',fscore[0]],['SVM','Accuracy',accuracy[0]],
                       ['Random Forest','Precision',precision[1]],['Random Forest','Recall',recall[1]],['Random Forest','F1 Score',fscore[1]],['Random Forest','Accuracy',accuracy[1]],
                       ['Logistic Regression','Precision',precision[2]],['Logistic Regression','Recall',recall[2]],['Logistic Regression','F1 Score',fscore[2]],['Logistic Regression','Accuracy',accuracy[2]],
                       ['Voting Classifier','Precision',precision[3]],['Voting Classifier','Recall',recall[3]],['Voting Classifier','F1 Score',fscore[3]],['Voting Classifier','Accuracy',accuracy[3]],
                       ['Extension XGBoost','Precision',precision[4]],['Extension XGBoost','Recall',recall[4]],['Extension XGBoost','F1 Score',fscore[4]],['Extension XGBoost','Accuracy',accuracy[4]],
                      ],columns=['Algorithms','Performance Output','Value'])
    df.pivot("Algorithms", "Performance Output", "Value").plot(kind='bar')
    plt.show()

def predict():
    global xg_model, sc, tfidf_vectorizer, labels
    text.delete('1.0', END)
    filename = filedialog.askopenfilename(initialdir = "Dataset")
    data = pd.read_csv(filename)
    desc = data['long_description'].ravel()
    data = data.values
    for i in range(len(desc)):
        value = desc[i]
        value = cleanText(value)
        value = tfidf_vectorizer.transform([value]).toarray()#convert text to vector
        value = sc.transform(value)
        predict = xg_model.predict(value)[0]
        predict = labels[int(predict)]
        text.insert(END,"Test Data = "+str(desc[i])+" Predicted Bug Type ===> "+str(predict)+"\n\n")
        
    

font = ('times', 16, 'bold')
title = Label(main, text='Nature-Based Prediction Model of Bug Reports Based on Ensemble Machine Learning Model', justify=LEFT)
title.config(bg='lavender blush', fg='DarkOrchid1')  
title.config(font=font)           
title.config(height=3, width=120)       
title.place(x=100,y=5)
title.pack()

font1 = ('times', 13, 'bold')
uploadButton = Button(main, text="Upload Eclipse Mozilla Bug Dataset", command=uploadDataset)
uploadButton.place(x=10,y=100)
uploadButton.config(font=font1)

processButton = Button(main, text="Process Dataset", command=processDataset)
processButton.place(x=330,y=100)
processButton.config(font=font1) 

svmButton = Button(main, text="Run SVM Algorithm", command=runSVM)
svmButton.place(x=580,y=100)
svmButton.config(font=font1) 

rfButton = Button(main, text="Run Random Forest", command=runRF)
rfButton.place(x=10,y=150)
rfButton.config(font=font1)

lrButton = Button(main, text="Run Logistic Regression", command=runLR)
lrButton.place(x=330,y=150)
lrButton.config(font=font1)

vcButton = Button(main, text="Propose Ensemble Voting Classifier", command=runVC)
vcButton.place(x=580,y=150)
vcButton.config(font=font1)

extensionButton = Button(main, text="Extension XGBoost Algorithm", command=runXGBoost)
extensionButton.place(x=10,y=200)
extensionButton.config(font=font1)

graphButton = Button(main, text="Comparison Graph", command=graph)
graphButton.place(x=330,y=200)
graphButton.config(font=font1)

predictButton = Button(main, text="Predict Bug Type from Test Data", command=predict)
predictButton.place(x=580,y=200)
predictButton.config(font=font1)


font1 = ('times', 12, 'bold')
text=Text(main,height=22,width=140)
scroll=Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=10,y=250)
text.config(font=font1)

main.config(bg='light coral')
main.mainloop()

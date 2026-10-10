import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from xgboost import XGBClassifier
import lightgbm as lgb
from catboost import CatBoostClassifier
from sklearn.decomposition import PCA
'''
dataset = pd.read_csv("dayr5.2.csv", nrows=300)
print(np.unique(dataset['insider'], return_counts=True))

dataset.to_csv("temp1.csv", index=False)
'''
'''
temp = pd.read_csv("temp.csv")
temp.insider[temp.insider == 2] = 1
temp.insider[temp.insider == 3] = 1
temp.insider[temp.insider == 4] = 1

temp1 = pd.read_csv("temp1.csv")

data = pd.concat([temp1, temp], ignore_index=True)
print(np.unique(data['insider'], return_counts=True))
data.to_csv("CERT.csv", index=False)
'''

dataset = pd.read_csv("Dataset/CERT.csv")
dataset.fillna(0, inplace = True)
dataset = dataset.values
X = dataset[:,0:dataset.shape[1]-1]
Y = dataset[:,dataset.shape[1]-1]

scaler = StandardScaler()
X = scaler.fit_transform(X)

indices = np.arange(X.shape[0])
np.random.shuffle(indices)
X = X[indices]
Y = Y[indices]

pca = PCA(n_components=220)
X = pca.fit_transform(X)
print(X)
print(Y)


X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2) #split dataset into train and test

rf = RandomForestClassifier()
rf.fit(X_train, y_train)
predict = rf.predict(X_test)

acc = accuracy_score(y_test, predict)
print(acc)


ada = AdaBoostClassifier()
ada.fit(X_train, y_train)
predict = ada.predict(X_test)
#predict[0:10]=0
acc = accuracy_score(y_test, predict)
print(acc)

xg_cls = XGBClassifier()
xg_cls.fit(X_train, y_train)
predict = xg_cls.predict(X_test)
acc = accuracy_score(y_test, predict)
print(acc)


lg_cls = lgb.LGBMClassifier()
lg_cls.fit(X_train, y_train)
predict = lg_cls.predict(X_test)
acc = accuracy_score(y_test, predict)
print(acc) 

cat = CatBoostClassifier(iterations=100)
cat.fit(X_train, y_train)
predict = cat.predict(X_test)
acc = accuracy_score(y_test, predict)
print(acc)

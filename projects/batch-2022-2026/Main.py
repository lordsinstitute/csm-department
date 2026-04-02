#importing python classes and packages
from tkinter import *
from tkinter import simpledialog
import tkinter
from tkinter import filedialog
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
import os
import re
from keras.callbacks import ModelCheckpoint 
import pickle
from keras.layers import LSTM #load LSTM class
from keras.utils.np_utils import to_categorical
from keras.layers import  MaxPooling2D
from keras.layers import Dense, Dropout, Activation, Flatten #load DNN dense layers
from keras.layers import Convolution2D #load CNN model
from keras.models import Sequential, Model
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import RFECV
from sklearn.svm import SVR
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from xgboost import XGBClassifier #load ML classes
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from matplotlib.backends.backend_pdf import PdfPages


main = tkinter.Tk()
main.title("Detection of Ransomware Attacks Using Processor and Disk Usage Data ") #designing main screen
main.geometry("1300x1200")

global filename, dataset, X_train, X_test, y_train, y_test, X, Y, scaler, pca
global accuracy, precision, recall, fscore, values,cnn_model
precision = []
recall = []
fscore = []
accuracy = []
labels = ['Non Attack', 'Attack']
CLASS_NAME_MAP = {0: 'Non Attack', 1: 'Attack'}
cnn_model = None
scaler = None
feature_columns_used = []
AUTO_OPEN_SAVED_IMAGES = False
FIGURES_DIR = "figures"

if os.path.exists(FIGURES_DIR) == False:
    os.makedirs(FIGURES_DIR)


def _is_preprocessed():
    return 'X_train' in globals() and 'X_test' in globals() and 'y_train' in globals() and 'y_test' in globals()


def _to_one_hot(y):
    y_arr = np.array(y)
    if y_arr.ndim == 1:
        return to_categorical(y_arr)
    return y_arr


def _as_2d_features(x):
    x_arr = np.array(x)
    if x_arr.ndim == 2:
        return x_arr
    return x_arr.reshape(x_arr.shape[0], -1)


def _safe_filename(name):
    return re.sub(r'[^A-Za-z0-9_-]+', '_', str(name)).strip('_')


def _figure_path(filename):
    return os.path.join(FIGURES_DIR, filename)


def _save_current_figure(filename):
    plt.tight_layout()
    plt.savefig(_figure_path(filename), dpi=150, bbox_inches='tight')


def _save_table(df, filename):
    df.to_csv(_figure_path(filename), index=False)


def _open_image_if_possible(filename):
    if AUTO_OPEN_SAVED_IMAGES == False:
        return
    img_path = os.path.abspath(_figure_path(filename))
    try:
        if os.name == 'nt' and os.path.exists(img_path):
            os.startfile(img_path)
    except Exception:
        pass


def _reset_plot_windows():
    try:
        plt.close('all')
    except Exception:
        pass


def _log_section(title):
    text.insert(END, "\n" + "=" * 68 + "\n")
    text.insert(END, title + "\n")
    text.insert(END, "=" * 68 + "\n")


def _class_distribution_table(y_values):
    unique_vals, counts = np.unique(y_values, return_counts=True)
    rows = []
    for cls_val, cls_count in zip(unique_vals, counts):
        cls_name = CLASS_NAME_MAP.get(int(cls_val), 'Class ' + str(int(cls_val)))
        rows.append([int(cls_val), cls_name, int(cls_count)])
    return pd.DataFrame(rows, columns=['Class_ID', 'Class_Name', 'Count'])


def _apply_plot_theme():
    style_candidates = [
        'seaborn-v0_8-whitegrid',
        'seaborn-whitegrid',
        'ggplot',
        'default'
    ]
    for style_name in style_candidates:
        try:
            plt.style.use(style_name)
            break
        except Exception:
            continue

    try:
        sns.set_style('whitegrid')
    except Exception:
        pass

    plt.rcParams.update({
        'axes.facecolor': '#f9fbff',
        'figure.facecolor': '#ffffff',
        'axes.edgecolor': '#c9d6ea',
        'grid.color': '#dce5f3',
        'axes.titleweight': 'bold',
        'axes.titlesize': 13,
        'axes.labelsize': 11,
        'font.size': 10
    })


def _create_pdf_report():
    output_pdf = _figure_path("all_outputs_report.pdf")
    image_files = [
        f for f in os.listdir(FIGURES_DIR)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]
    table_files = [
        f for f in os.listdir(FIGURES_DIR)
        if f.lower().endswith('.csv')
    ]

    if len(image_files) == 0 and len(table_files) == 0:
        text.insert(END, "No figures/tables found in figures folder to build PDF report.\n")
        return

    with PdfPages(output_pdf) as pdf:
        for img_name in sorted(image_files):
            img_path = _figure_path(img_name)
            img = plt.imread(img_path)
            fig = plt.figure(figsize=(11, 8.5))
            ax = fig.add_subplot(111)
            ax.imshow(img)
            ax.axis('off')
            ax.set_title(img_name, fontsize=12)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

        for csv_name in sorted(table_files):
            csv_path = _figure_path(csv_name)
            df = pd.read_csv(csv_path)
            fig = plt.figure(figsize=(11, 8.5))
            ax = fig.add_subplot(111)
            ax.axis('off')
            ax.set_title(csv_name, fontsize=12)
            table = ax.table(
                cellText=df.values,
                colLabels=df.columns,
                loc='center'
            )
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.3)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

    text.insert(END, "PDF report saved at: " + output_pdf + "\n")

def uploadDataset():
    global filename, dataset, labels, values
    filename = filedialog.askopenfilename(initialdir = "Dataset")
    if filename is None or len(filename) == 0:
        return

    text.delete('1.0', END)
    dataset = pd.read_csv(filename)
    _log_section("Dataset Loaded Successfully")
    text.insert(END, "File: " + os.path.basename(filename) + "\n")
    text.insert(END, "Rows: " + str(dataset.shape[0]) + "\n")
    text.insert(END, "Columns: " + str(dataset.shape[1]) + "\n")
    text.insert(END, "Feature Columns: " + str(dataset.shape[1] - 2) + "\n")

    missing_total = int(dataset.isnull().sum().sum())
    text.insert(END, "Missing Values: " + str(missing_total) + "\n")

    if 'label' in dataset.columns:
        dist_df = _class_distribution_table(dataset['label'].astype(int).values)
        text.insert(END, "\nClass Distribution:\n")
        text.insert(END, dist_df.to_string(index=False) + "\n")

    preview_rows = min(8, len(dataset))
    text.insert(END, "\nDataset Preview (first " + str(preview_rows) + " rows):\n")
    text.insert(END, dataset.head(preview_rows).to_string(index=False) + "\n")

    class_dist_df = _class_distribution_table(dataset['label'].astype(int).values)
    height = class_dist_df['Count'].values
    bars = class_dist_df['Class_Name'].values

    _reset_plot_windows()
    _apply_plot_theme()
    plt.figure(figsize=(7.2, 4.6))
    bar_colors = ['#4c78a8', '#e45756'][:len(bars)]
    plotted = plt.bar(bars, height, color=bar_colors, edgecolor='#1f2d3d', linewidth=0.7)
    for bar in plotted:
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + max(height) * 0.01,
            str(int(bar.get_height())),
            ha='center',
            va='bottom',
            fontsize=10,
            fontweight='bold'
        )
    plt.title('Dataset Class Distribution')
    plt.xlabel('Class')
    plt.ylabel('Count')
    _save_current_figure("dataset_class_distribution.png")
    plt.show()

def processDataset():
    global dataset, X, Y
    global X_train, X_test, y_train, y_test, pca, scaler, feature_columns_used
    text.delete('1.0', END)

    if 'dataset' not in globals() or dataset is None:
        text.insert(END, "Please click 'Upload Attack Database' first.\n")
        return

    _log_section("Preprocessing Pipeline")

    null_before = int(dataset.isnull().sum().sum())
    text.insert(END, "Initial Missing Values: " + str(null_before) + "\n")
    dataset.fillna(0, inplace = True)
    null_after = int(dataset.isnull().sum().sum())
    text.insert(END, "Missing Values After Fill: " + str(null_after) + "\n")

    if 'label' not in dataset.columns:
        text.insert(END, "Dataset must include a 'label' column.\n")
        return

    y_series = dataset['label'].astype(int)
    full_feature_df = dataset.drop(columns=['label'])

    # Keep legacy behavior (drop first feature column) for compatibility with existing trained weights.
    if full_feature_df.shape[1] < 2:
        text.insert(END, "Not enough feature columns in dataset after removing label.\n")
        return

    feature_df = full_feature_df.iloc[:, 1:]
    feature_columns_used = list(feature_df.columns)

    X = feature_df.values
    Y = y_series.values

    text.insert(END, "\nFeature Matrix Shape: " + str(X.shape) + "\n")
    text.insert(END, "Label Vector Shape: " + str(Y.shape) + "\n")

    indices = np.arange(X.shape[0])
    np.random.shuffle(indices)#shuffle dataset values
    X = X[indices]
    Y = Y[indices]

    scaler = MinMaxScaler((0,1)) #use to normalize training data
    X = scaler.fit_transform(X)#normalized or transform features

    text.insert(END, "\nNormalization: MinMaxScaler(0, 1) applied\n")
    text.insert(END, "Normalized Value Range: [" + str(round(float(X.min()), 4)) + ", " + str(round(float(X.max()), 4)) + "]\n")

    preview_count = min(5, X.shape[0])
    preview_matrix = np.array2string(
        X[:preview_count, :],
        precision=4,
        suppress_small=True,
        max_line_width=160
    )
    text.insert(END, "\nNormalized Feature Preview (first " + str(preview_count) + " rows):\n")
    text.insert(END, preview_matrix + "\n")

    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = 0.2)

    _log_section("Train/Test Split Summary")
    text.insert(END, "Training Samples (80%): " + str(X_train.shape[0]) + "\n")
    text.insert(END, "Testing Samples (20%):  " + str(X_test.shape[0]) + "\n")
    text.insert(END, "Features per Sample:    " + str(X_train.shape[1]) + "\n")

    train_dist = _class_distribution_table(y_train)
    test_dist = _class_distribution_table(y_test)
    text.insert(END, "\nTraining Class Distribution:\n")
    text.insert(END, train_dist.to_string(index=False) + "\n")
    text.insert(END, "\nTesting Class Distribution:\n")
    text.insert(END, test_dist.to_string(index=False) + "\n")

    text.insert(END, "\nReady: You can now run model algorithms from the top buttons.\n")

def calculateMetrics(algorithm, predict, testY):
    p = precision_score(testY, predict,average='macro') * 100
    r = recall_score(testY, predict,average='macro') * 100
    f = f1_score(testY, predict,average='macro') * 100
    a = accuracy_score(testY,predict)*100     
    _log_section(algorithm + " Evaluation Results")
    text.insert(END, 'Accuracy : ' + str(round(a, 2)) + "%\n")
    text.insert(END, 'Precision: ' + str(round(p, 2)) + "%\n")
    text.insert(END, 'Recall   : ' + str(round(r, 2)) + "%\n")
    text.insert(END, 'F1-Score : ' + str(round(f, 2)) + "%\n")

    conf_matrix = confusion_matrix(testY, predict)
    text.insert(END, "\nConfusion Matrix:\n")
    text.insert(END, str(conf_matrix) + "\n")
    text.insert(END, "Saved Plot: figures/" + _safe_filename(algorithm.lower()) + "_confusion_matrix.png\n")

    accuracy.append(a)
    precision.append(p)
    recall.append(r)
    fscore.append(f)

    _reset_plot_windows()
    _apply_plot_theme()
    fig, ax = plt.subplots(figsize=(6.2, 5.4))
    try:
        cmap = sns.color_palette('Blues', as_cmap=True)
    except Exception:
        cmap = plt.cm.Blues
    sns.heatmap(
        conf_matrix,
        xticklabels=labels,
        yticklabels=labels,
        cmap=cmap,
        cbar=True,
        annot=False,
        linewidths=1.0,
        linecolor='white',
        square=True,
        ax=ax
    )
    for i in range(conf_matrix.shape[0]):
        for j in range(conf_matrix.shape[1]):
            value = int(conf_matrix[i, j])
            max_val = int(np.max(conf_matrix)) if np.max(conf_matrix) > 0 else 1
            color = 'white' if value > (0.45 * max_val) else '#0f172a'
            ax.text(
                j + 0.5,
                i + 0.5,
                str(value),
                ha='center',
                va='center',
                fontsize=19,
                fontweight='bold',
                color=color
            )
    ax.set_ylim([0, len(labels)])
    ax.set_title(algorithm + " Confusion Matrix", pad=12)
    ax.set_ylabel('True Label')
    ax.set_xlabel('Predicted Label')
    ax.tick_params(axis='x', rotation=0)
    ax.tick_params(axis='y', rotation=90)
    algo_file = _safe_filename(algorithm.lower())
    _save_current_figure(algo_file + "_confusion_matrix.png")
    plt.show()
    _open_image_if_possible(algo_file + "_confusion_matrix.png")

def runsvm():
    global X_train, y_train, X_test, y_test
    global accuracy, precision, recall, fscore
    text.delete('1.0', END)
    
    svm_cls = svm.SVC(kernel="poly", gamma="scale", C=0.004)
    svm_cls.fit(X_train, y_train)
    predict = svm_cls.predict(X_test)
    calculateMetrics("SVM", predict, y_test)

def runknn():
    global X_train, y_train, X_test, y_test
    global accuracy, precision, recall, fscore
    text.delete('1.0', END)
   
    knn_cls =  KNeighborsClassifier(n_neighbors=500)
    knn_cls.fit(X_train, y_train)
    predict = knn_cls.predict(X_test)
    calculateMetrics("KNN", predict, y_test)

def runDT():
    global X_train, y_train, X_test, y_test
    global accuracy, precision, recall, fscore
    text.delete('1.0', END)
    
    dt_cls = DecisionTreeClassifier(criterion = "entropy",max_leaf_nodes=2,max_features="auto")#giving hyper input parameter values
    dt_cls.fit(X_train, y_train)
    predict = dt_cls.predict(X_test)
    calculateMetrics("Decision Tree", predict, y_test)

def runRF():
    global X_train, y_train, X_test, y_test
    global accuracy, precision, recall, fscore
    text.delete('1.0', END)
    
    rf = RandomForestClassifier(n_estimators=40, criterion='gini', max_features="log2", min_weight_fraction_leaf=0.3)
    rf.fit(X_train, y_train)
    predict = rf.predict(X_test)
    calculateMetrics("Random Forest", predict, y_test)
def runXGBoost():
    global X_train, y_train, X_test, y_test
    global accuracy, precision, recall, fscore
    text.delete('1.0', END)
    
    xgb_cls = XGBClassifier(n_estimators=10,learning_rate=0.09,max_depth=2)
    xgb_cls.fit(X_train, y_train)
    predict = xgb_cls.predict(X_test)
    calculateMetrics("XGBoost", predict, y_test)

def runDNN():
    global X_train, y_train, X_test, y_test
    global accuracy, precision, recall, fscore
    text.delete('1.0', END)
    if _is_preprocessed() == False:
        text.insert(END, "Please click 'Preprocess & Split Dataset' first.\n")
        return
    try:
        y_train_dl = _to_one_hot(y_train)
        y_test_dl = _to_one_hot(y_test)
        x_train_dl = _as_2d_features(X_train)
        x_test_dl = _as_2d_features(X_test)
        #define DNN object
        dnn_model = Sequential()
        #add DNN layers
        dnn_model.add(Dense(2, input_shape=(x_train_dl.shape[1],), activation='relu'))
        dnn_model.add(Dense(2, activation='relu'))
        dnn_model.add(Dropout(0.3))
        dnn_model.add(Dense(y_train_dl.shape[1], activation='softmax'))
        # compile the keras model
        dnn_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        #start training model on train data and perform validation on test data
        #train and load the model
        if os.path.exists("model/dnn_weights.hdf5") == False:
            model_check_point = ModelCheckpoint(filepath='model/dnn_weights.hdf5', verbose = 1, save_best_only = True)
            hist = dnn_model.fit(x_train_dl, y_train_dl, batch_size = 32, epochs = 10, validation_data=(x_test_dl, y_test_dl), callbacks=[model_check_point], verbose=1)
            f = open('model/dnn_history.pckl', 'wb')
            pickle.dump(hist.history, f)
            f.close()
        else:
            dnn_model.load_weights("model/dnn_weights.hdf5")
        #perform prediction on test data
        predict = dnn_model.predict(x_test_dl)
        predict = np.argmax(predict, axis=1)
        testY = np.argmax(y_test_dl, axis=1)
        calculateMetrics("DNN", predict, testY)#call function to calculate accuracy and other metrics
    except Exception as e:
        text.insert(END, "DNN execution failed:\n"+str(e)+"\n")

def runLSTM():
    global X_train, y_train, X_test, y_test
    global accuracy, precision, recall, fscore
    text.delete('1.0', END)
    if _is_preprocessed() == False:
        text.insert(END, "Please click 'Preprocess & Split Dataset' first.\n")
        return
    try:
        y_train_dl = _to_one_hot(y_train)
        y_test_dl = _to_one_hot(y_test)
        x_train_base = _as_2d_features(X_train)
        x_test_base = _as_2d_features(X_test)
        x_train_lstm = np.reshape(x_train_base, (x_train_base.shape[0], x_train_base.shape[1], 1))
        x_test_lstm = np.reshape(x_test_base, (x_test_base.shape[0], x_test_base.shape[1], 1))

        lstm_model = Sequential()#defining deep learning sequential object
        #adding LSTM layer with 100 filters to filter given input X train data to select relevant features
        lstm_model.add(LSTM(32,input_shape=(x_train_lstm.shape[1], x_train_lstm.shape[2])))
        #adding dropout layer to remove irrelevant features
        lstm_model.add(Dropout(0.2))
        #adding another layer
        lstm_model.add(Dense(32, activation='relu'))
        #defining output layer for prediction
        lstm_model.add(Dense(y_train_dl.shape[1], activation='softmax'))
        #compile LSTM model
        lstm_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        #start training model on train data and perform validation on test data
        #train and load the model
        if os.path.exists("model/lstm_weights.hdf5") == False:
            model_check_point = ModelCheckpoint(filepath='model/lstm_weights.hdf5', verbose = 1, save_best_only = True)
            hist = lstm_model.fit(x_train_lstm, y_train_dl, batch_size = 32, epochs = 10, validation_data=(x_test_lstm, y_test_dl), callbacks=[model_check_point], verbose=1)
            f = open('model/lstm_history.pckl', 'wb')
            pickle.dump(hist.history, f)
            f.close()
        else:
            lstm_model.load_weights("model/lstm_weights.hdf5")
        #perform prediction on test data
        predict = lstm_model.predict(x_test_lstm)
        predict = np.argmax(predict, axis=1)
        testY = np.argmax(y_test_dl, axis=1)
        calculateMetrics("LSTM", predict, testY)#call function to calculate accuracy and other metrics
    except Exception as e:
        text.insert(END, "LSTM execution failed:\n"+str(e)+"\n")
def runCNN():
    global X_train, y_train, X_test, y_test,cnn_model
    global accuracy, precision, recall, fscore
    text.delete('1.0', END)
    if _is_preprocessed() == False:
        text.insert(END, "Please click 'Preprocess & Split Dataset' first.\n")
        return
    try:
        y_train_dl = _to_one_hot(y_train)
        y_test_dl = _to_one_hot(y_test)
        x_train_base = _as_2d_features(X_train)
        x_test_base = _as_2d_features(X_test)
        x_train_cnn = np.reshape(x_train_base, (x_train_base.shape[0], x_train_base.shape[1], 1, 1))
        x_test_cnn = np.reshape(x_test_base, (x_test_base.shape[0], x_test_base.shape[1], 1, 1))
        #define extension CNN model object
        cnn_model = Sequential()
        #adding CNN layer wit 32 filters to optimized dataset features using 32 neurons
        cnn_model.add(Convolution2D(64, (1, 1), input_shape = (x_train_cnn.shape[1], x_train_cnn.shape[2], x_train_cnn.shape[3]), activation = 'relu'))
        #adding maxpooling layer to collect filtered relevant features from previous CNN layer
        cnn_model.add(MaxPooling2D(pool_size = (1, 1)))
        #adding another CNN layer to further filtered features
        cnn_model.add(Convolution2D(32, (1, 1), activation = 'relu'))
        cnn_model.add(MaxPooling2D(pool_size = (1, 1)))
        #collect relevant filtered features
        cnn_model.add(Flatten())
        cnn_model.add(Dropout(0.2))
        #defining output layers
        cnn_model.add(Dense(units = 256, activation = 'relu'))
        #defining prediction layer with Y target data
        cnn_model.add(Dense(units = y_train_dl.shape[1], activation = 'softmax'))
        #compile the CNN with LSTM model
        cnn_model.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
        #train and load the model
        if os.path.exists("model/cnn_weights.hdf5") == False:
            model_check_point = ModelCheckpoint(filepath='model/cnn_weights.hdf5', verbose = 1, save_best_only = True)
            hist = cnn_model.fit(x_train_cnn, y_train_dl, batch_size = 8, epochs = 10, validation_data=(x_test_cnn, y_test_dl), callbacks=[model_check_point], verbose=1)
            f = open('model/cnn_history.pckl', 'wb')
            pickle.dump(hist.history, f)
            f.close()
        else:
            cnn_model.load_weights("model/cnn_weights.hdf5")
        #perform prediction on test data
        predict = cnn_model.predict(x_test_cnn)
        predict = np.argmax(predict, axis=1)
        testY = np.argmax(y_test_dl, axis=1)
        calculateMetrics("Extension CNN2D", predict, testY)#call function to calculate accuracy and other metrics
    except Exception as e:
        text.insert(END, "CNN2D execution failed:\n"+str(e)+"\n")

def comparisongraph():
    text.delete('1.0', END)
    if len(accuracy) < 8:
        text.insert(END, "Please run all algorithms first, then click 'Comparison Graph'.\n")
        return
    try:
        _reset_plot_windows()
        df = pd.DataFrame([['SVM','Precision',precision[0]],['SVM','Recall',recall[0]],['SVM','F1 Score',fscore[0]],['SVM','Accuracy',accuracy[0]],
                           ['KNN','Precision',precision[1]],['KNN','Recall',recall[1]],['KNN','F1 Score',fscore[1]],['KNN','Accuracy',accuracy[1]],
                           ['Decision Tree','Precision',precision[2]],['Decision Tree','Recall',recall[2]],['Decision Tree','F1 Score',fscore[2]],['Decision Tree','Accuracy',accuracy[2]],
                           ['Random Forest','Precision',precision[3]],['Random Forest','Recall',recall[3]],['Random Forest','F1 Score',fscore[3]],['Random Forest','Accuracy',accuracy[3]],
                           ['XGBoost','Precision',precision[4]],['XGBoost','Recall',recall[4]],['XGBoost','F1 Score',fscore[4]],['XGBoost','Accuracy',accuracy[4]],
                           ['DNN','Precision',precision[5]],['DNN','Recall',recall[5]],['DNN','F1 Score',fscore[5]],['DNN','Accuracy',accuracy[5]],
                           ['LSTM','Precision',precision[6]],['LSTM','Recall',recall[6]],['LSTM','F1 Score',fscore[6]],['LSTM','Accuracy',accuracy[6]],
                           ['Extension CNN','Precision',precision[7]],['Extension CNN','Recall',recall[7]],['Extension CNN','F1 Score',fscore[7]],['Extension CNN','Accuracy',accuracy[7]],
                          ],columns=['Parameters','Algorithms','Value'])
        _save_table(df, "algorithm_metrics_long.csv")
        _apply_plot_theme()
        pivot_df = df.pivot(index="Parameters", columns="Algorithms", values="Value")
        ax = pivot_df.plot(kind='bar', figsize=(11.5, 6), width=0.84)
        ax.set_title("All Algorithms Performance Comparison")
        ax.set_xlabel("Model")
        ax.set_ylabel("Score (%)")
        ax.legend(loc='upper center', ncol=4, frameon=True)
        ax.set_ylim(0, 105)
        plt.xticks(rotation=25, ha='right')
        _save_current_figure("all_algorithms_performance_graph.png")
        plt.show()
        _open_image_if_possible("all_algorithms_performance_graph.png")

        leaderboard_df = pd.DataFrame({
            'Model': [
                'SVM',
                'KNN',
                'Decision Tree',
                'Random Forest',
                'XGBoost',
                'DNN',
                'LSTM',
                'Extension CNN2D'
            ],
            'Accuracy_%': [
                round(float(accuracy[0]), 2),
                round(float(accuracy[1]), 2),
                round(float(accuracy[2]), 2),
                round(float(accuracy[3]), 2),
                round(float(accuracy[4]), 2),
                round(float(accuracy[5]), 2),
                round(float(accuracy[6]), 2),
                round(float(accuracy[7]), 2)
            ]
        }).sort_values(by='Accuracy_%', ascending=False).reset_index(drop=True)

        best_model = str(leaderboard_df.loc[0, 'Model'])
        best_acc = float(leaderboard_df.loc[0, 'Accuracy_%'])

        _log_section("Comparison Graph Generated")
        text.insert(END, "Saved Table : figures/algorithm_metrics_long.csv\n")
        text.insert(END, "Saved Plot  : figures/all_algorithms_performance_graph.png\n")
        text.insert(END, "\nBest Model (by Accuracy): " + best_model + " = " + str(best_acc) + "%\n")
        text.insert(END, "\nModel Accuracy Leaderboard:\n")
        text.insert(END, leaderboard_df.to_string(index=False) + "\n")
    except Exception as e:
        text.insert(END, "Comparison graph failed:\n" + str(e) + "\n")

def prdeict():
    global X_train, y_train, X_test, y_test
    global accuracy, precision, recall, fscore,cnn_model, feature_columns_used
    text.delete('1.0', END)
    if scaler is None:
        text.insert(END, "Please load and preprocess dataset first.\n")
        return
    if cnn_model is None:
        text.insert(END, "Please run 'Run CNN2D Algorithm' first.\n")
        return
    try:
        test_file = filedialog.askopenfilename(
            initialdir="Dataset",
            title="Select Test Dataset CSV",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if test_file is None or len(test_file) == 0:
            text.insert(END, "Prediction cancelled. No test dataset selected.\n")
            return

        test_df = pd.read_csv(test_file)#reading test data
        test_df.fillna(0, inplace = True)
        has_ground_truth = 'label' in test_df.columns
        y_true_test = None
        if has_ground_truth:
            try:
                y_true_test = test_df['label'].astype(int).values
            except Exception:
                y_true_test = None
                has_ground_truth = False

        raw_feature_df = test_df.drop(columns=['label'], errors='ignore')

        expected_feature_count = int(X_train.shape[1]) if _is_preprocessed() else int(raw_feature_df.shape[1])

        if len(feature_columns_used) > 0 and set(feature_columns_used).issubset(set(raw_feature_df.columns)):
            feature_df = raw_feature_df[feature_columns_used]
        elif raw_feature_df.shape[1] == expected_feature_count + 1:
            # Fallback to legacy behavior: drop first feature column.
            feature_df = raw_feature_df.iloc[:, 1:]
        elif raw_feature_df.shape[1] == expected_feature_count:
            feature_df = raw_feature_df
        else:
            text.insert(END, "Prediction failed:\n")
            text.insert(END, "Feature mismatch between training data and selected test file.\n")
            text.insert(END, "Expected feature columns: " + str(expected_feature_count) + "\n")
            text.insert(END, "Found feature columns:    " + str(raw_feature_df.shape[1]) + "\n")
            return

        testData = feature_df.values
        test = scaler.transform(testData)#normalizing values
        test = np.reshape(test, (test.shape[0], test.shape[1], 1, 1))
        predict = cnn_model.predict(test)#performing prediction on test data using extension CNN model

        _log_section("Prediction Results on " + os.path.basename(test_file))
        text.insert(END, "Samples Evaluated: " + str(len(predict)) + "\n")

        prediction_rows = []
        for i in range(len(predict)):
            pred_probs = predict[i]
            pred = int(np.argmax(pred_probs))
            pred_label = CLASS_NAME_MAP.get(pred, 'Class ' + str(pred))
            confidence = float(np.max(pred_probs)) * 100.0
            prediction_rows.append([
                i + 1,
                pred_label,
                round(confidence, 2),
                int(pred)
            ])

        pred_df = pd.DataFrame(
            prediction_rows,
            columns=["Sample_No", "Predicted_Label", "Confidence_%", "Predicted_Class_ID"]
        )

        summary_df = pred_df['Predicted_Label'].value_counts().reset_index()
        summary_df.columns = ['Predicted_Label', 'Count']
        summary_df['Percent'] = (summary_df['Count'] / len(pred_df) * 100).round(2)

        text.insert(END, "\nPrediction Distribution:\n")
        text.insert(END, summary_df.to_string(index=False) + "\n")

        preview_n = min(15, len(pred_df))
        text.insert(END, "\nDetailed Preview (first " + str(preview_n) + " rows):\n")
        text.insert(END, pred_df.head(preview_n).to_string(index=False) + "\n")

        _reset_plot_windows()
        _apply_plot_theme()
        plt.figure(figsize=(7.2, 4.6))
        color_map = {'Non Attack': '#4c78a8', 'Attack': '#e45756'}
        bar_colors = [color_map.get(lbl, '#72b7b2') for lbl in summary_df['Predicted_Label']]
        bars = plt.bar(summary_df['Predicted_Label'], summary_df['Count'], color=bar_colors)
        for bar in bars:
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + max(summary_df['Count']) * 0.01,
                str(int(bar.get_height())),
                ha='center',
                va='bottom',
                fontsize=10,
                fontweight='bold'
            )
        plt.title('Prediction Class Distribution (Test Data)')
        plt.xlabel('Predicted Label')
        plt.ylabel('Count')
        _save_current_figure("test_prediction_distribution.png")
        plt.show()
        _open_image_if_possible("test_prediction_distribution.png")

        _save_table(pred_df, "test_predictions.csv")
        _save_table(summary_df, "test_predictions_summary.csv")
        text.insert(END, "\nSaved Table : figures/test_predictions.csv\n")
        text.insert(END, "Saved Summary: figures/test_predictions_summary.csv\n")
        text.insert(END, "Saved Plot  : figures/test_prediction_distribution.png\n")

        # Optional validation mode: runs only when selected test file includes a valid label column.
        if has_ground_truth and y_true_test is not None and len(y_true_test) == len(pred_df):
            y_pred_test = pred_df['Predicted_Class_ID'].astype(int).values

            val_acc = accuracy_score(y_true_test, y_pred_test) * 100.0
            val_p = precision_score(y_true_test, y_pred_test, average='macro') * 100.0
            val_r = recall_score(y_true_test, y_pred_test, average='macro') * 100.0
            val_f1 = f1_score(y_true_test, y_pred_test, average='macro') * 100.0

            val_cm = confusion_matrix(y_true_test, y_pred_test)
            val_df = pd.DataFrame([
                [round(float(val_acc), 2), round(float(val_p), 2), round(float(val_r), 2), round(float(val_f1), 2)]
            ], columns=['Accuracy_%', 'Precision_%', 'Recall_%', 'F1_Score_%'])
            _save_table(val_df, "test_predictions_validation_metrics.csv")

            _log_section("Validation Against Ground Truth (label column found)")
            text.insert(END, "Accuracy : " + str(round(float(val_acc), 2)) + "%\n")
            text.insert(END, "Precision: " + str(round(float(val_p), 2)) + "%\n")
            text.insert(END, "Recall   : " + str(round(float(val_r), 2)) + "%\n")
            text.insert(END, "F1-Score : " + str(round(float(val_f1), 2)) + "%\n")
            text.insert(END, "\nValidation Confusion Matrix:\n")
            text.insert(END, str(val_cm) + "\n")

            _reset_plot_windows()
            _apply_plot_theme()
            fig, ax = plt.subplots(figsize=(6.2, 5.4))
            try:
                v_cmap = sns.color_palette('Blues', as_cmap=True)
            except Exception:
                v_cmap = plt.cm.Blues

            sns.heatmap(
                val_cm,
                xticklabels=labels,
                yticklabels=labels,
                cmap=v_cmap,
                cbar=True,
                annot=False,
                linewidths=1.0,
                linecolor='white',
                square=True,
                ax=ax
            )
            for i in range(val_cm.shape[0]):
                for j in range(val_cm.shape[1]):
                    value = int(val_cm[i, j])
                    max_val = int(np.max(val_cm)) if np.max(val_cm) > 0 else 1
                    color = 'white' if value > (0.45 * max_val) else '#0f172a'
                    ax.text(
                        j + 0.5,
                        i + 0.5,
                        str(value),
                        ha='center',
                        va='center',
                        fontsize=19,
                        fontweight='bold',
                        color=color
                    )
            ax.set_ylim([0, len(labels)])
            ax.set_title('Prediction Validation Confusion Matrix', pad=12)
            ax.set_ylabel('True Label')
            ax.set_xlabel('Predicted Label')
            ax.tick_params(axis='x', rotation=0)
            ax.tick_params(axis='y', rotation=90)
            _save_current_figure("test_predictions_validation_confusion_matrix.png")
            plt.show()

            text.insert(END, "\nSaved Validation Table : figures/test_predictions_validation_metrics.csv\n")
            text.insert(END, "Saved Validation Plot  : figures/test_predictions_validation_confusion_matrix.png\n")
    except Exception as e:
        text.insert(END, "Prediction failed:\n"+str(e)+"\n")


def generatePDFReport():
    text.delete('1.0', END)
    try:
        _create_pdf_report()
    except Exception as e:
        text.insert(END, "PDF generation failed:\n" + str(e) + "\n")

APP_BG = '#edf3fb'
CARD_BG = '#ffffff'
TITLE_COLOR = '#12335b'
SUBTITLE_COLOR = '#415a77'
PRIMARY_BTN = '#1768ac'
PRIMARY_BTN_ACTIVE = '#0f4d80'
SECONDARY_BTN = '#2a9d8f'
SECONDARY_BTN_ACTIVE = '#1f776d'

main.config(bg=APP_BG)

title_font = ('Segoe UI', 20, 'bold')
subtitle_font = ('Segoe UI', 10, 'normal')

title = Label(
    main,
    text='Detection of Ransomware Attacks Using Processor and Disk Usage Data',
    bg=APP_BG,
    fg=TITLE_COLOR,
    font=title_font
)
title.place(x=20, y=14)

subtitle = Label(
    main,
    text='Train, evaluate, compare, and report ransomware detection models from one interface',
    bg=APP_BG,
    fg=SUBTITLE_COLOR,
    font=subtitle_font
)
subtitle.place(x=22, y=52)

controls_frame = Frame(main, bg=CARD_BG, highlightthickness=1, highlightbackground='#c9d6ea')
controls_frame.place(x=20, y=85, width=1260, height=150)

for col in range(6):
    controls_frame.grid_columnconfigure(col, weight=1)

btn_font = ('Segoe UI', 10, 'bold')

def _style_button(button_obj, primary=True):
    if primary:
        button_obj.config(
            bg=PRIMARY_BTN,
            activebackground=PRIMARY_BTN_ACTIVE,
            fg='white',
            activeforeground='white'
        )
    else:
        button_obj.config(
            bg=SECONDARY_BTN,
            activebackground=SECONDARY_BTN_ACTIVE,
            fg='white',
            activeforeground='white'
        )
    button_obj.config(
        font=btn_font,
        relief='flat',
        bd=0,
        padx=10,
        pady=8,
        cursor='hand2'
    )

uploadButton = Button(controls_frame, text='Upload Attack Database', command=uploadDataset)
uploadButton.grid(row=0, column=0, padx=8, pady=8, sticky='ew')
_style_button(uploadButton)

processButton = Button(controls_frame, text='Preprocess & Split Dataset', command=processDataset)
processButton.grid(row=0, column=1, padx=8, pady=8, sticky='ew')
_style_button(processButton)

svmButton = Button(controls_frame, text='Run SVM Algorithm', command=runsvm)
svmButton.grid(row=0, column=2, padx=8, pady=8, sticky='ew')
_style_button(svmButton)

knnButton = Button(controls_frame, text='Run KNN Algorithm', command=runknn)
knnButton.grid(row=0, column=3, padx=8, pady=8, sticky='ew')
_style_button(knnButton)

dtButton = Button(controls_frame, text='Run Decision Tree', command=runDT)
dtButton.grid(row=0, column=4, padx=8, pady=8, sticky='ew')
_style_button(dtButton)

rfButton = Button(controls_frame, text='Run Random Forest', command=runRF)
rfButton.grid(row=0, column=5, padx=8, pady=8, sticky='ew')
_style_button(rfButton)

xgButton = Button(controls_frame, text='Run XGBoost Algorithm', command=runXGBoost)
xgButton.grid(row=1, column=0, padx=8, pady=8, sticky='ew')
_style_button(xgButton)

dnnButton = Button(controls_frame, text='Run DNN Algorithm', command=runDNN)
dnnButton.grid(row=1, column=1, padx=8, pady=8, sticky='ew')
_style_button(dnnButton)

lstmButton = Button(controls_frame, text='Run LSTM Algorithm', command=runLSTM)
lstmButton.grid(row=1, column=2, padx=8, pady=8, sticky='ew')
_style_button(lstmButton)

cnnButton = Button(controls_frame, text='Run CNN2D Algorithm', command=runCNN)
cnnButton.grid(row=1, column=3, padx=8, pady=8, sticky='ew')
_style_button(cnnButton)

graphButton = Button(controls_frame, text='Comparison Graph', command=comparisongraph)
graphButton.grid(row=1, column=4, padx=8, pady=8, sticky='ew')
_style_button(graphButton)

predictButton = Button(controls_frame, text='Predict Attack from Test Data', command=prdeict)
predictButton.grid(row=1, column=5, padx=8, pady=8, sticky='ew')
_style_button(predictButton)

pdfButton = Button(controls_frame, text='Generate PDF Report', command=generatePDFReport)
pdfButton.grid(row=2, column=0, columnspan=6, padx=8, pady=(4, 8), sticky='ew')
_style_button(pdfButton, primary=False)

output_frame = Frame(main, bg=CARD_BG, highlightthickness=1, highlightbackground='#c9d6ea')
output_frame.place(x=20, y=250, width=1260, height=620)

text_font = ('Consolas', 10, 'normal')
text = Text(
    output_frame,
    wrap='word',
    bg='#f8fbff',
    fg='#102a43',
    insertbackground='#102a43',
    bd=0,
    highlightthickness=0,
    font=text_font
)
scroll = Scrollbar(output_frame, orient=VERTICAL, command=text.yview)
text.configure(yscrollcommand=scroll.set)

text.place(x=12, y=12, width=1208, height=594)
scroll.place(x=1222, y=12, height=594)

main.mainloop()

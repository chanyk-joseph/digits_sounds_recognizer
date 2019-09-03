import librosa
import numpy as np
import sklearn
import pandas as pd
import tflearn
import tensorflow as tf

allDataDf = pd.read_csv("./digits-with-label.csv")
allDataDf = sklearn.utils.shuffle(allDataDf, random_state=0)
allDataDf.reset_index(inplace=True, drop=True)

# train_df = allDataDf[0:(int(.8*len(allDataDf)))]
# validation_df = allDataDf[(int(.8*len(allDataDf))):(int(.9*len(allDataDf)))]
# test_df = allDataDf[(int(.9*len(allDataDf))):]

train_df = allDataDf[0:(int(.9*len(allDataDf)))]
validation_df = allDataDf[(int(.9*len(allDataDf))):(len(allDataDf)-5)]
test_df = allDataDf[(len(allDataDf)-5):]

number_classes=10 # Digits
digitOneHotMap = np.eye(number_classes)
cache = dict()

def loadWav(wavFile):
    if wavFile in cache:
        return cache[wavFile]

    wave, sr = librosa.load(wavFile, mono=True)
    mfcc = librosa.feature.mfcc(wave, sr)
    mfcc=np.pad(mfcc,((0,0),(0,80-len(mfcc[0]))), mode='constant', constant_values=0)
    return mfcc

def mfcc_batch_generator(df, batch_size=10):
    batch_features = []
    labels = []
    
    while True:
        print("loaded batch of %d files" % len(df))
        df = sklearn.utils.shuffle(df, random_state=0)
        df.reset_index(inplace=True, drop=True)

        for index, row in df.iterrows():
            filepath = row['filepath']
            digit = int(row['digit'])

            batch_features.append(np.array(loadWav(filepath)))
            labels.append(digitOneHotMap[digit])
            if len(batch_features) >= batch_size:
                yield batch_features, labels  # basic_rnn_seq2seq inputs must be a sequence
                batch_features = []  # Reset for next batch
                labels = []

def preloadWav(df):
    for index, row in df.iterrows():
        filepath = row['filepath']
        cache[filepath] = loadWav(filepath)

preloadWav(train_df)
preloadWav(validation_df)
preloadWav(test_df)

# with tf.device('/gpu:0'):
tflearn.init_graph(num_cores=16, gpu_memory_fraction=0.5)
net = tflearn.input_data(shape=[None, 20, 80])
net = tflearn.fully_connected(net, 64)
net = tflearn.dropout(net, 0.5)
net = tflearn.fully_connected(net, number_classes, activation='softmax')
net = tflearn.regression(net, optimizer='adam', loss='categorical_crossentropy')
model = tflearn.DNN(net, best_checkpoint_path='./best_model')

count = 0
trainX, trainY = next(mfcc_batch_generator(train_df, len(train_df.index)))
validationX, validationY = next(mfcc_batch_generator(validation_df, len(validation_df.index)))
model.fit(trainX, trainY, n_epoch=100, batch_size=10, validation_set=(validationX, validationY), show_metric=True, snapshot_step=100, run_id='jchan')
# model.save("model")


for i in range(0, len(test_df.index)):
    testRow = test_df.iloc[i]
    testFile = testRow['filepath']
    testDigit = testRow['digit']
    result=model.predict([loadWav(testFile)])
    result=np.argmax(result)
    print("predicted digit for %s : result = %d | actual = %d"%(testFile, result, testDigit))

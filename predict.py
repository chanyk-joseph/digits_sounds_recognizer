import logging
import warnings
import os
warnings.filterwarnings('ignore') 
logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import io
import sys
from pydub import AudioSegment
import tflearn
import librosa
import numpy as np
import tensorflow as tf

# tf.logging.set_verbosity(tf.logging.FATAL)

# Load MP3
mp3FilePath = sys.argv[1]
audio = AudioSegment.from_mp3(mp3FilePath)
digits = [audio[2000:2500], audio[4000:4500], audio[6000:6500], audio[8000:8500]]

# Load Pre-trained model
tflearn.init_graph(num_cores=16, gpu_memory_fraction=0.5)
net = tflearn.input_data(shape=[None, 20, 80])
net = tflearn.fully_connected(net, 64)
net = tflearn.dropout(net, 0.5)
net = tflearn.fully_connected(net, 10, activation='softmax')
net = tflearn.regression(net, optimizer='adam', loss='categorical_crossentropy')
model = tflearn.DNN(net)
model.load('./best_model10000')

result = ''
for j, sound in enumerate(digits):
    buf = io.BytesIO()
    tmpWavPath = '/tmp/%d.wav' % j
    sound.export(tmpWavPath, format="wav")
    wave, sr = librosa.load(tmpWavPath, mono=True)
    mfcc = librosa.feature.mfcc(wave, sr)
    mfcc=np.pad(mfcc,((0,0),(0,80-len(mfcc[0]))), mode='constant', constant_values=0)
    featuresX = [mfcc]
    predictedProbabilitiesOfEachDigit = model.predict(featuresX)
    result += str(np.argmax(predictedProbabilitiesOfEachDigit))

print('Prediction for %s = %s' % (mp3FilePath, result))
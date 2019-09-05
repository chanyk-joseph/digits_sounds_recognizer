import json
import base64
import uuid

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

# Load Pre-trained model
tflearn.init_graph(num_cores=1, gpu_memory_fraction=0.5)
net = tflearn.input_data(shape=[None, 20, 80])
net = tflearn.fully_connected(net, 64)
net = tflearn.dropout(net, 0.5)
net = tflearn.fully_connected(net, 10, activation='softmax')
net = tflearn.regression(net, optimizer='adam', loss='categorical_crossentropy')
model = tflearn.DNN(net)
model.load('./best_model10000')

def digits_recognizer(request):
    mp3Base64Str = ''
    content_type = request.headers['content-type']
    if content_type == 'application/json':
        request_json = request.get_json(silent=True)
        if request_json and 'mp3' in request_json:
            mp3Base64Str = request_json['mp3']
        else:
            raise ValueError("JSON is invalid, or missing a 'name' property")
    else:
        raise ValueError("Unknown content type: {}".format(content_type))

    print(len(mp3Base64Str))
    
    # Export base64 into .mp3 file
    mp3_64_decode = base64.b64decode(mp3Base64Str)
    mp3FilePath = '/tmp/'+str(uuid.uuid4())+'.mp3'
    mp3_result = open(mp3FilePath, 'wb')
    mp3_result.write(mp3_64_decode)
    
    # Load MP3
    audio = AudioSegment.from_mp3(mp3FilePath)
    digits = [audio[2000:2500], audio[4000:4500], audio[6000:6500], audio[8000:8500]]
    
    result = ''
    for j, sound in enumerate(digits):
        buf = io.BytesIO()
        tmpWavPath = '/tmp/%s.wav' % (str(j)+'_'+str(uuid.uuid4()))
        sound.export(tmpWavPath, format="wav")
        wave, sr = librosa.load(tmpWavPath, mono=True)
        mfcc = librosa.feature.mfcc(wave, sr)
        mfcc=np.pad(mfcc,((0,0),(0,80-len(mfcc[0]))), mode='constant', constant_values=0)
        featuresX = [mfcc]
        predictedProbabilitiesOfEachDigit = model.predict(featuresX)
        result += str(np.argmax(predictedProbabilitiesOfEachDigit))
    
    return json.dumps({'ans': result})

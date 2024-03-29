# digits_sounds_recognizer
Simple NN model for recovering Cantonese digits to text  (99% Accuracy after 100 epoch)
```Shell
--
Training Step: 18000  | total loss: 0.20440 | time: 2.408s
| Adam | epoch: 100 | loss: 0.20440 - acc: 0.9911 | val_loss: 0.00000 - val_acc: 1.0000 -- iter: 1800/1800
--
```
![TensorBoard](img/tensorboard.png)

# Installation on ubuntu
```Shell
$ sudo apt-get install libasound2-dev
$ pip3 install -r requirements.txt
```

# Predict
```Shell
$ python predict.py ./data/4999.mp3
Prediction for ./data/4999.mp3 = 9972
```

# Train
```Shell
$ python train.py
```

# Fetch more samples & perform labelling manually
```Shell
$ node samples_collector.js
$ python 4-digits-audio-splitter-and-labeler.py
$ python generate-data-summary-csv.py
```

# Deploy on Google Cloud
```Shell
$ cd ./gcloud-function
$ gcloud functions deploy digits_recognizer --runtime=python37 --trigger-http --memory=512 --timeout=60s --region=asia-east2

# Test
$ curl -d '{"mp3":"<mp3_in_base64_string>"}' -H "Content-Type: application/json" -X POST https://asia-east2-protean-silicon-865.cloudfunctions.net/digits_recognizer
```
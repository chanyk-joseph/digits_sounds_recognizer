import glob
import numpy as np
import pandas as pd
import sys
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO

def getLabeledSamples():
    dataFolder = "./data"

    data = dict()
    for i in range(300):
        pathFilter = "%s/%d-*-*.wav" % (dataFolder, i)
        files = glob.glob(pathFilter)
        for audioFilePath in files:
            ans = audioFilePath[-5]
            if ans in data:
                data[ans].append(audioFilePath)
            else:
                data[ans] = [audioFilePath]

    arrResults = []
    for ans in data:
        files = data[ans]
        for f in files:
            arrResults.append({'wav': f, 'ans': ans})

    # np.random.shuffle(arrResults)

    csvResults = "filepath;digit\n"
    for result in arrResults:
        csvResults += ("%s;%s\n" % (result['wav'], result['ans']))

    df = pd.read_csv(StringIO(csvResults), sep=";")
    df = df.sort_values(by='digit', ascending=True)
    return (arrResults, csvResults, df)

_, _, df = getLabeledSamples()
df.to_csv('./digits-with-label.csv', index = None)
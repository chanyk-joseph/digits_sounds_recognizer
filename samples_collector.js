/* eslint-disable max-len */
/* eslint-disable require-jsdoc */
/* eslint-disable no-unused-vars */

const fs = require('fs');
const path = require('path');
const Promise = require('bluebird');
const request = require('request');
const rp = require('request-promise');

async function getImage(id, retryCount=0, timeoutInSecond = 60) {
    console.log('Starting ' + id);

    const phantom = require('phantom');
    phantom.onError = function(msg, trace) {
        const msgStack = ['PHANTOM ERROR: ' + msg];
        if (trace && trace.length) {
            msgStack.push('TRACE:');
            trace.forEach(function(t) {
                msgStack.push(' -> ' + (t.file || t.sourceURL) + ': ' + t.line + (t.function ? ' (in function ' + t.function +')' : ''));
            });
        }
        console.log(msgStack.join('\n'));
        phantom.exit(1);
    };

    const instance = await phantom.create();
    const page = await instance.createPage();
    let captchaInBase64 = '';

    page.on('onResourceRequested', function(requestData) {
        console.info(id + ' | Requesting', requestData.url);
        if (requestData.url.startsWith('data:image/jpg;base64,')) {
            captchaInBase64 = requestData.url.replace('data:image/jpg;base64,', '');
        }
    });

    // let status = page.open('http://leisurelink.lcsd.gov.hk/?lang=tc');
    // console.log('Sleep');
    // await Promise.delay(10000);
    // console.log('request');
    // page.off();
    const status = await page.open('http://w1.leisurelink.lcsd.gov.hk/leisurelink/application/checkCode.do?flowId=1&lang=TC');
    // await Promise.delay(10000);
    // status = await page.open('http://w1.leisurelink.lcsd.gov.hk/leisurelink/humanTest/tsvkb');
    for (let i=0; i<(timeoutInSecond * 1) && captchaInBase64 === ''; i++) {
        await Promise.delay(1000);
        console.log(id + ' | delay ' + i);
    }
    await page.close();
    await instance.exit();
    if (captchaInBase64 === '' && retryCount > 0 ) {
        captchaInBase64 = await getImage(id, retryCount--);
    }
    if (captchaInBase64 === '') {
        throw new Error('Failed ' + id);
    }
    return captchaInBase64;
}

function downloadImageSample(id, retryCount=0) {
    console.log(id);
    return rp({
        method: 'POST',
        uri: 'http://w1.leisurelink.lcsd.gov.hk/leisurelink/humanTest/tsvkb',
    }).then((html) => {
        const regex = /data:image\/jpg;base64,(.*?)"/gm;
        const m = regex.exec(html);
        if (m && m.length == 2) {
            const base64Data = m[1];
            fs.writeFileSync(path.join('./samples/captcha/4_chars', id + '.png'), base64Data, 'base64');
        } else {
            throw new Error('Failed to get image: ' + id);
        }
    }).catch((err) => {
        if (retryCount > 0) {
            return downloadAudioSample(id, retryCount--);
        } else {
            throw err;
        }
    });
}

function downloadAudioSample(id, retryCount=0) {
    console.log(id);

    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(path.join('./data', id + '.mp3'));
        request({
            uri: 'http://w1.leisurelink.lcsd.gov.hk/leisurelink/jcaptcha.mp3?reload=1567262982384',
        })
            .pipe(file)
            .on('finish', () => {
                resolve();
            })
            .on('error', (error)=>{
                reject(error);
            });
    }).catch((err) => {
        console.log(err);
        if (retryCount > 0) {
            return downloadAudioSample(id, retryCount--);
        } else {
            reject(err);
        }
    });
}

(async function() {
    const taskIDs = [];
    for (let i=0; i<5000; i++) {
        taskIDs.push(i);
    }
    await Promise.map(taskIDs, (taskID) => {
        return downloadAudioSample(taskID, 10).catch(console.log);
    }, {concurrency: 10});
})();

from os import path
from pydub import AudioSegment
from pydub.playback import play

samples_folder = "./data"

# Play the digit one by one, and ask user to input the correct label without enter
def askDegit(sound):
    play(sound)

    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


for i in range(350, 400):
    audioPath = path.join(samples_folder, str(i) + '.mp3')
    audio = AudioSegment.from_mp3(audioPath)
    
    digits = [audio[2000:2500], audio[4000:4500], audio[6000:6500], audio[8000:8500]]

    for j, sound in enumerate(digits):
        ans = askDegit(sound)
        outFilePath = path.join(samples_folder, ("%d-%d-%s.wav" % (i, j, ans)))
        sound.export(outFilePath, format="wav")
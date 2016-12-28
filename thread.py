from threading import Thread
from random import randint
import time
import threading
from omxplayer import OMXPlayer
import subprocess
import RPi.GPIO as GPIO
import os
from mutagen.mp3 import MP3

BUTTON_GPIO = 16

GPIO.setmode(GPIO.BCM)
GPIO.setup(20,GPIO.IN)
GPIO.setup(BUTTON_GPIO,GPIO.IN, pull_up_down=GPIO.PUD_UP)

AUDIO_PATH = '/home/pi/Music/m.mp3'
AUDIO_LENGTH = MP3(AUDIO_PATH).info.length

AUDIO_WAS_PLAYING = False

sectionDuration = 10 #in seconds
sensorPhaseDuration = 5 #seconds
isSensingMode = False
lastPositionFile = 'audioLastPosition.txt'


def createFileLastPosition():
    return open(lastPositionFile, "w")

def loadLastPosition():
    if (os.path.exists(lastPositionFile) == False):
        createFileLastPosition()
        return 0
    fo = open(lastPositionFile, "r")
    fileContent = fo.read()
    print '----- Load from File ------'
    print fileContent
    fo.close()
    return fileContent

def saveLastPosition(newFileContent):
    print '----- Save inside File ------'
    print newFileContent
    fo = open(lastPositionFile, "w")
    fo.write(str(newFileContent))
    fo.close()
    
def convertSecondsToTimeStamp(seconds):
    return time.strftime('%H:%M:%S', time.gmtime(seconds))



AUDIO_LAST_POSITION = loadLastPosition()

print 'AUDIO LENGTH %d' % AUDIO_LENGTH


class TimeThread(Thread):

    def __init__(self, interval, cb):
        ''' Constructor. '''
        Thread.__init__(self)
        self.interval = interval
        self.callback = cb
        self._stop = threading.Event()
        self.sectionTimer = 0
        self.audioTimer = int(AUDIO_LAST_POSITION)

    def resetTimer(self, newInterval, callback, newAudioTimer):
        self.sectionTimer = 0
        self.interval = newInterval
        self.callback = callback
        self.audioTimer = newAudioTimer if newAudioTimer != None else self.audioTimer

    def stop(self):
        print 'Timer: I am stopped'
        self._stop.set()
        # print 'Last Section Duration %d' % self.getTime()
        print '-------------'

    def restart(self):
        print 'Timer: Refreshed and back to work'
        # print 'New values for timer %d' % self.getTime()
        print '-------------'
        self._stop.clear()

    def startSensingMode(self, newInterval, callback):
        self.resetTimer(newInterval, callback, None)

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while True:
            while self.sectionTimer < self.interval and self._stop.isSet() == False:
                time.sleep(1)
                self.sectionTimer = self.sectionTimer + 1
                self.audioTimer = self.audioTimer + 1
                
                if self.audioTimer > AUDIO_LENGTH: 
					print 'TimerThread: The File Is OVER'
					orchestrator.reset()

                print '------ Timer ------'
                print 'Audio track %d' % self.audioTimer
                print '-------------'

                if self.sectionTimer  == self.interval and self.callback:
                    self.callback()
                    

    def getTrackPosition(self):
        return self.audioTimer

class PlayThread(Thread):

    def __init__(self):
        ''' Constructor. '''
        Thread.__init__(self)
        self._player = "subprocess"

    def run(self):
        self.createSubProcess()
        
    def createSubProcess(self):
        lastPosition = None
		#create subprocess
        if AUDIO_LAST_POSITION > 0:	
            lastPosition = convertSecondsToTimeStamp(float(AUDIO_LAST_POSITION))
        #lastPosition = None
        subProcessParameters = ['omxplayer', AUDIO_PATH]
        if lastPosition:
			subProcessParameters = ['omxplayer','-l ' + lastPosition, AUDIO_PATH]
			print subProcessParameters[1]
        print 'creating sub process to audiobook'
        self._player = subprocess.Popen(subProcessParameters,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds = True)
        self._player.stdin.write('p')
    
    def play(self):
        print 'PlayThread: going to playing the audiobook'
        self._player.stdin.write('p')

    def pause(self):
        print 'pause the audiobook'
        self._player.stdin.write('p')

    def volumeDown(self):
        print 'PlayThread: My volume is down!'
        for i in range (0, 3):
            self._player.stdin.write('-')
            time.sleep(0.1)
        
    def volumeUp(self):
        print 'PlayThread: My volume is up again!'
        for i in range (0, 3):
            self._player.stdin.write('+')
            time.sleep(0.1)
        
class ButtonThread(Thread):

    def __init__(self):
        ''' Constructor. '''
        Thread.__init__(self)
        self.wasPlaying = True
        self.clickFlag = False

    def run(self):
        #if click, check the wasPlaying
            #if wasPlaying = True
                #say to orch to stop
            #else, say to orch to start
        
        global AUDIO_WAS_PLAYING

        while True:
            input_state = GPIO.input(BUTTON_GPIO)
            if input_state == False:
                print '!!! Click detected'
                if AUDIO_WAS_PLAYING == True:
                    print 'I was playing now I should stop'
                    orchestrator.stop()
                else:
                    print 'I was paused now I should play'
                    orchestrator.play()
                time.sleep(0.2)     

    def emulateClick(self):
        print 'Clicking on button'
        self.clickFlag = True
        time.sleep(0.1)
        print 'Reseting button'
        self.clickFlag = False

class SensorThread(Thread):
    def __init__(self, cb):
        ''' Constructor. '''
        Thread.__init__(self)
        self._stop = threading.Event()
        self.sensorInterruption = False
        self.callback = cb

    def stop(self):
        print 'Sensor: I am stopped'
        self._stop.set()

    def resume(self):
        print 'Sensor: Back to work'
        self._stop.clear()

    def run(self):
        while True:
            while self._stop.isSet() == False:
                if GPIO.input(20):
                    self.callback()
                time.sleep(0.1)

    def sensorInterruptionEmulation(self):
        print 'Sensor: Emulating an interruption'
        self.sensorInterruption = True
        time.sleep(0.1)
        print 'Sensor: reseting the interruption'
        self.sensorInterruption = False

def callbackWhenSensing():
    print 'Sensor callbackWhenSensing: HEY, I sensed something here!'
    orchestrator.restartSection()

def callbackSensingMode():
    orchestrator.finish()

def callback():
    print "Sensing mode"
    # to turn volume down
    orchestrator.startSensingMode()

class Orchestrator(object):

    def __init__(self):
        ''' Constructor. '''
        self.playThread = PlayThread()
        self.timerThread = TimeThread(sectionDuration, callback)
        self.sensorThread = SensorThread(callbackWhenSensing)
       
        self.timerThread.start()
        self.playThread.start()
        self.sensorThread.start()
        
        self.sensorThread.stop()

    def play(self):
        # start audio player
        # start timer
        # self.timerThread.start()
        print "Orchestrator: I am playing everything"
        
        global AUDIO_WAS_PLAYING
        AUDIO_WAS_PLAYING = True
        
        if isSensingMode == True:
			print "I was in the SENSING MODE"
			self.playThread.volumeUp()
			global isSensingMode
			isSensingMode = False
        self.playThread.play()
        self.timerThread.resetTimer(sectionDuration, callback, None)
        self.timerThread.restart()

    def startSensingMode(self):
        global isSensingMode
        isSensingMode=True
        self.playThread.volumeDown()
        self.timerThread.startSensingMode(sensorPhaseDuration, callbackSensingMode)
        self.sensorThread.resume()

    def finish(self):
        print "Orchestrator: I finished sensing mode"
        self.stop()
        saveLastPosition(self.timerThread.getTrackPosition())

    def restartSection(self):
        global isSensingMode
        isSensingMode=False
        self.playThread.volumeUp()
        self.sensorThread.stop()
        self.timerThread.resetTimer(sectionDuration, callback, None)
        self.timerThread.restart()

    def stop(self):
        # pause audio player
        # stop and reset timer
        self.timerThread.stop()
        self.playThread.pause()
        self.sensorThread.stop()
        
        global AUDIO_WAS_PLAYING
        AUDIO_WAS_PLAYING = False

    def emulateSensorInterruption(self):
        self.sensorThread.sensorInterruptionEmulation()
    
    def reset(self):
        print 'Orchestrator: Reseting everything'
        
        global AUDIO_LAST_POSITION
        AUDIO_LAST_POSITION = 0
        createFileLastPosition()
        os.remove(lastPositionFile)
        
        self.playThread.createSubProcess()
        
        global isSensingMode
        globalisSensingMode=False
        
        global AUDIO_WAS_PLAYING
        AUDIO_WAS_PLAYING = False
        
        self.sensorThread.stop()
        self.timerThread.stop()
        self.timerThread.resetTimer(sectionDuration, callback, 0)
        

orchestrator = Orchestrator()

def main():
    time.sleep(1)
    buttonThread = ButtonThread()
    buttonThread.start()
    
    orchestrator.play()
    # time.sleep(12)
    # orchestrator.emulateSensorInterruption()
    # stop
    # buttonThread.emulateClick()
    #time.sleep(5)
    # stop
    #buttonThread.emulateClick()
    #time.sleep(5)
    # # start
    #buttonThread.emulateClick()

    # while True:
    #     orchestrator.play()
    #     time.sleep(15)
    #     buttonThread.emulateClick()


# Run following code when the program starts
if __name__ == '__main__':
    main()

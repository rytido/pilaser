from time import sleep
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
from sklearn.cluster import DBSCAN
scan = DBSCAN(eps=2, min_samples=3)

class Analysis(PiRGBAnalysis):
    def __init__(self, camera, size=None):
        #super(PiAnalysisOutput, self).__init__()
        self.camera = camera
        self.size = size
        self.x0 = np.array(0)
        self.i = 0
        self.t = self.camera.timestamp
        self.misc = []
    
    def analyse(self, x):
        x = x[:,:,1]
        d = self.x0-x
        d[self.x0<x] = 0
        xy = np.argwhere(d>10)
        if xy.shape[0]>2 and xy.shape[0]<1200:
            clust = scan.fit_predict(xy)
            ind = clust>-1
            clust = clust[ind]
            xy = xy[ind]
            denom = np.bincount(clust)
            numerx = np.bincount(clust, xy[:,0])
            numery = np.bincount(clust, xy[:,1])
            xc = numerx/denom
            yc = numery/denom
            #self.misc = [xc, yc]
        self.x0 = x
        self.i += 1
        if self.i % 10 == 0:
            td = self.camera.timestamp - self.t
            self.t += td
            #print("\r" + str(10/td), end="")
            print("\r" + str(self.camera.exposure_speed), end="")
        


rectime = 4
camera = PiCamera(resolution=(640, 480), framerate=25)
tracker = Analysis(camera)
camera.color_effects = (128,128)
camera.awb_mode = 'off'
camera.awb_gains = (1.5, 1.5)
camera.exposure_mode = 'night'
camera.shutter_speed = 32000
camera.video_denoise = False

camera.start_preview(fullscreen=False, window = (20, 40, 640, 480))
sleep(2)
camera.start_recording(tracker, format='rgb')
#camera.start_recording('/home/pi/video2.h264')
camera.wait_recording(rectime)
camera.stop_recording()
camera.stop_preview()
print(camera.timestamp)
print("\n%s fps" % ((tracker.i)/rectime))
print(tracker.misc)

#omxplayer -o hdmi video2.h264
#avconv -i video2.h264 -s 640x480 -q:v 1 imgs2/v%04d.jpg

"""
import os
from scipy.misc import imread, imshow
 
path = '/home/pi/imgs2/'
files = os.listdir(path)
files.sort()

for f in files:
    x = imread(path+f)
    tracker.analyse(x)

"""

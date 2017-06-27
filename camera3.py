from time import sleep
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
from sklearn.cluster import DBSCAN
scan = DBSCAN(eps=2, min_samples=3)

crosshair = np.zeros((480, 640, 3), dtype=np.uint8)

class Analysis(PiRGBAnalysis):
    def __init__(self, camera, size=None):
        #super(PiAnalysisOutput, self).__init__()
        self.camera = camera
        self.size = size
        self.x0 = np.array(0)
        self.i = 0
        self.t0 = self.camera.timestamp
        self.xc = 240
        self.yc = 320
    
    def analyse(self, x):
        x = x[:,:,1]
        d = self.x0-x
        d[self.x0<x] = 0
        xy = np.argwhere(d>20)
        if xy.shape[0]>2 and xy.shape[0]<1200:
            clust = scan.fit_predict(xy)
            ind = clust>-1
            if ind.any():
                clust = clust[ind]
                xy = xy[ind]
                denom = np.bincount(clust)
                numerx = np.bincount(clust, xy[:,0])
                numery = np.bincount(clust, xy[:,1])
                self.xc = np.rint((numerx/denom)[0]).astype(np.uint16)
                self.yc = np.rint((numery/denom)[0]).astype(np.uint16)
                #crosshair[xc, (yc-2):(yc+3), :] = 0xff
                #crosshair[(xc-2):(xc+3), yc, :] = 0xff
                #ol.update(crosshair)
        self.x0 = x
        self.i += 1
        #td = self.camera.timestamp - self.t0
        #self.t0 += td    
        #if self.i % 10 == 0:
        #    print("\r" + str(10/td), end="")
            

rectime = 3
camera = PiCamera(resolution=(640, 480), framerate=20)
camera.awb_mode = 'off'
camera.awb_gains = (1.5, 1.5)
camera.iso = 500
camera.color_effects = (128,128)
camera.exposure_mode = 'sports' #sports
#camera.shutter_speed = 32000
camera.video_denoise = False

#fullscreen=False, window = (10, 10, 640, 480)
camera.start_preview(fullscreen=False, window = (10, 10, 960, 720))
ol = camera.add_overlay(crosshair, layer=3, alpha=25, fullscreen=False, window = (10, 10, 960, 720)) #memoryview tobytes()
tracker = Analysis(camera)
camera.start_recording(tracker, format='rgb')
#camera.start_recording('/home/pi/video2.h264')
#camera.wait_recording(rectime)
xc0 = 0
yc0 = 0
try:
    while True:
        if tracker.xc!=xc0 or tracker.yc!=yc0:
            crosshair[tracker.xc, (tracker.yc-2):(tracker.yc+3), :] = 0xff
            crosshair[(tracker.xc-2):(tracker.xc+3), tracker.yc, :] = 0xff
            ol.update(crosshair)
        xc0 = tracker.xc
        yc0 = tracker.yc
        sleep(.05)
except KeyboardInterrupt:
    pass
camera.remove_overlay(ol)
camera.stop_recording()
camera.stop_preview()
print("%s frames" % tracker.i)
td = (tracker.camera.timestamp - tracker.t0)/1000000
print("%s fps" % (tracker.i/td))

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

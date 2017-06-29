from time import sleep
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
from sklearn.cluster import DBSCAN
scan = DBSCAN(eps=2, min_samples=3, metric='euclidean', algorithm='ball_tree', leaf_size=30) 

class Analysis(PiRGBAnalysis):
    def __init__(self, camera, size=None):
        #super(PiAnalysisOutput, self).__init__()
        self.camera = camera
        self.size = size
        self.x0 = np.array(0)
        self.i = 0
        self.t0 = self.camera.timestamp
        self.xc = 0
        self.yc = 0
    
    def analyse(self, x):
        x = x[:,:,1]
        d = self.x0-x
        d[self.x0<x] = 0
        xy = np.argwhere(d>12)
        if xy.shape[0]>2 and xy.shape[0]<1000:
            clust = scan.fit_predict(xy)
            ind = clust==0
            if ind.any():
                #xy = xy[ind]
                self.xc = int(xy[ind,0].mean().round(0))
                self.yc = int(xy[ind,1].mean().round(0))
        self.x0 = x
        self.i += 1
        #td = self.camera.timestamp - self.t0
        #self.t0 += td
        #print("\r" + str(10/td), end="")
            

camera = PiCamera(resolution=(640, 480), framerate=20)
camera.awb_mode = 'off'
camera.awb_gains = (1.2, 1.2)
camera.iso = 640
camera.color_effects = (128,128)
camera.exposure_mode = 'sports' #sports
camera.shutter_speed = 12000
camera.video_denoise = False

camera.start_preview(fullscreen=False, window=(0,0,640,480))
tracker = Analysis(camera)
camera.start_recording(tracker, format='rgb')

crosshair = np.zeros((480, 640, 3), dtype=np.uint8)
ol = camera.add_overlay(crosshair, layer=3, alpha=25, fullscreen=False, window=(0,0,640,480)) #memoryview tobytes()

hist = [[5,5]] * 20
try:
    while True:
        if tracker.xc!=hist[-1][0] or tracker.yc!=hist[-1][1]:
            crosshair[tracker.xc, (tracker.yc-3):(tracker.yc+4), :] = 0xff
            crosshair[(tracker.xc-3):(tracker.xc+4), tracker.yc, :] = 0xff
            xc,yc = hist.pop(0)
            crosshair[xc, (yc-3):(yc+4), :] = 0
            crosshair[(xc-3):(xc+4), yc, :] = 0
            ol.update(crosshair)
            hist.append([tracker.xc,tracker.yc])
        sleep(.05)
except KeyboardInterrupt:
    pass

#camera.start_recording('/home/pi/video2.h264')
#camera.wait_recording(10)
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

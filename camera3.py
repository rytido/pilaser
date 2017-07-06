from time import sleep
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
from sklearn.cluster import DBSCAN
scan = DBSCAN(eps=2, min_samples=3, metric='euclidean', algorithm='ball_tree', leaf_size=30) 

class Analysis(PiRGBAnalysis):
    def __init__(self, camera, size=None):
        self.camera = camera
        self.size = size
        self.x0 = np.array(0)
        self.i = 0
        self.t0 = self.camera.timestamp
        self.xc0 = np.float32(0)
        self.yc0 = np.float32(0)
        self.xc = np.float32(0)
        self.yc = np.float32(0)
        self.xc2 = np.float32(0)
        self.yc2 = np.float32(0)
    
    def analyse(self, x):
        x = x[:,:,1]
        d = self.x0-x
        d[self.x0<x] = 0
        xy = np.argwhere(d>25)
        if xy.shape[0]>2 and xy.shape[0]<1000:
            clust = scan.fit_predict(xy)
            ind = clust==0
            if ind.any():
                self.xc = xy[ind,0].mean()
                self.yc = xy[ind,1].mean()
                self.xc2 = 2 * self.xc - self.xc0
                self.yc2 = 2 * self.yc - self.yc0
                self.xc0 = self.xc
                self.yc0 = self.yc
        self.x0 = x   
        self.i += 1
        #print("\r" + str(10/td), end="")

camera = PiCamera(resolution=(640, 480), framerate=20)
camera.awb_mode = 'off'
camera.awb_gains = (1.2, 1.2)
#camera.iso = 640
camera.color_effects = (128,128)
camera.exposure_mode = 'sports'
camera.shutter_speed = 12000
camera.video_denoise = False

#fullscreen=False, window=(0,0,640,480)
camera.start_preview()
tracker = Analysis(camera)
camera.start_recording(tracker, format='rgb')

crosshair = np.zeros((480, 640, 3), dtype=np.uint8)
ol = camera.add_overlay(crosshair, layer=3, alpha=25) 
#memoryview tobytes()

hist = [[5,5]] * 25
try:
    while True:
        xc = int(tracker.xc.round(0))
        yc = int(tracker.yc.round(0))
        if xc!=hist[-1][0] or yc!=hist[-1][1]:
            crosshair[xc, (yc-3):(yc+4), 1] = 0xff
            crosshair[(xc-3):(xc+4), yc, 1] = 0xff
            ol.update(crosshair)
            xc0,yc0 = hist.pop(0)
            crosshair[xc0, (yc0-3):(yc0+4), 1] = 0
            crosshair[(xc0-3):(xc0+4), yc0, 1] = 0
            hist.append([xc,yc])
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


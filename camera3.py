import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
from sklearn.cluster import DBSCAN
scan = DBSCAN(eps=2, min_samples=3, metric='euclidean', algorithm='ball_tree', leaf_size=30)

def printr(s):
    print("\r" + s + "       ", end="")

class Analysis(PiRGBAnalysis):
    def __init__(self, camera, size=None):
        self.camera = camera
        self.size = size
        self.x0 = np.array(0)
        self.i = 0
        self.xc0 = np.float32(0)
        self.yc0 = np.float32(0)
        self.xc = np.float32(0)
        self.yc = np.float32(0)
        self.xp = np.array(0)
        self.yp = np.array(0)
        self.calibrationMode = True
        self.stableCounter = 0
        self.bgsum = np.zeros((480, 640), dtype=np.uint16)
        self.bg = np.array(0)
        self.t0 = self.camera.timestamp
    
    def analyse(self, x):
        x = x[:,:,1]
        if self.calibrationMode:
            if np.any((self.x0>x) & (self.x0-x>50)):
                self.stableCounter = 0
                self.bgsum = np.zeros((480, 640), dtype=np.uint16)
            else:
                self.stableCounter += 1
                self.bgsum += x
                if self.stableCounter == 30:
                    self.bg = (self.bgsum/self.stableCounter).round(0).astype(np.uint8)
                    self.stableCounter = 0
                    self.bgsum = np.zeros((480, 640), dtype=np.uint16)
                    self.calibrationMode = False
                    printr("done")
            self.x0 = x
                    
        else: 
            d = (self.bg>x) & (self.bg-x>80)
            xy = np.where(d.ravel())[0]
            if xy.shape[0]>999:
                self.calibrationMode = True
                printr("calibrating")
            elif xy.shape[0]>4:
                xy = np.transpose(np.unravel_index(xy, d.shape))
                clust = scan.fit_predict(xy)
                ind = clust==0
                if ind.sum()>1:
                    self.xc = xy[ind,0].mean()
                    self.yc = xy[ind,1].mean()
                    xc2 = 2 * self.xc - self.xc0
                    yc2 = 2 * self.yc - self.yc0
                    #self.xp = np.linspace(self.xc0,xc2,10)
                    #self.yp = np.linspace(self.yc0,yc2,10)
                    self.xc0 = self.xc
                    self.yc0 = self.yc
                    printr("%s %s" % (int(self.xc.round()), int(self.yc.round())))
        self.i += 1

camera = PiCamera(resolution=(640, 480), framerate=20)
camera.awb_mode = 'off'
camera.awb_gains = (1.2, 1.2)
#camera.iso = 400 # 400 500 640 800
camera.color_effects = (128,128)
camera.exposure_mode = 'sports'
camera.shutter_speed = 12000
camera.video_denoise = True

camera.start_preview(fullscreen=False, window=(160,0,640,480))
printr("calibrating")
tracker = Analysis(camera)
camera.start_recording(tracker, format='rgb')
#camera.start_recording('/home/pi/video2.h264')

try:
    camera.wait_recording(9999) # sleep(9999)
except KeyboardInterrupt:
    pass

camera.stop_recording()
camera.stop_preview()
print("%s frames" % tracker.i)
td = (tracker.camera.timestamp - tracker.t0)/1000000
print("%s fps" % (tracker.i/td))


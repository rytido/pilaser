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
        self.misc = []
    
    def analyse(self, x):
        x = x[:,:,1]
        d = self.x0-x
        d[self.x0<x] = 0
        ind = np.argwhere(d>10)
        #self.misc.append(ind.shape)
        if ind.shape[0]>0 and ind.shape[0]<2000:
            clust = scan.fit_predict(ind)
            self.misc.append(np.unique(clust).shape)
        self.x0 = x
        self.i += 1


rectime = 2
camera = PiCamera()
output = Analysis(camera)
camera.resolution = (640, 640)
camera.framerate = 24
camera.color_effects = (128,128)
camera.start_preview()
sleep(3)
camera.start_recording(output, format='rgb')
#camera.start_recording('/home/pi/video2.h264')
camera.wait_recording(rectime)
camera.stop_recording()
camera.stop_preview()
        
print("%s fps" % ((output.i+6)/rectime))
print(output.misc)

#omxplayer -o hdmi video2.h264
#avconv -i video.h264 -s 640x640 -q:v 1 imgs/video-%03d.jpg


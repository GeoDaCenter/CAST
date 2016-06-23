"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['DynamicControl']

import time,random,threading

class DynamicControl(threading.Thread):
    """
    Base class for Dynamic/Animation control
    """
    def __init__(self):
        threading.Thread.__init__(self)
        
        self._stop = threading.Event()
        self._alive = True
        
        self.interval = 2 
        self.steps = 1#len(self.data_dict)
        self.step = 0
        
    def run(self):
        """
        run() will be called by Thread.start()
        """
        self.step = 0
        while not self.stopped():
            while self._alive and self.step < self.steps:
                # do something
                self.Do()
                self.step += 1
                #time.sleep (self.interval)
                time.sleep(.8)
            if self.step == self.steps:
                self.Finish()
            time.sleep(0.1)
  
    def Do(self):
        """
        Abstract function which should be implemented 
        at inherited classes for their own purpose
        """
        pass
    
    def Finish(self):
        pass
    
    def setup_speed(self,speed):
        self.interval = 5.0 / (speed+1) # 0.01 ~ 0.1 ~ 0.5
   
    def pause(self):
        self._alive = False
   
    def resume(self):
        self._alive = True
        
    def stop(self):
        self.pause()
        # fake stop
        self.step = 0

    def stopped (self):
        return self._stop.isSet()
    
    def real_stop(self):
        self._stop.set()
    
class DynamicMapControl(DynamicControl):
    """
    Dynamic control for Dynamic Maps:
        Dynamic Density Maps
        Dynamic LISA Maps
        Dynamic LISA Markovs
        ...
    """
    def __init__(self, frame,n,executor):
        DynamicControl.__init__(self)
       
        self.slider = frame.animate_slider
        self.frame = frame
        
        self.executor = executor
    
        self.steps = n
        self.slider.SetRange(0,n-1)
        
    def Do(self):
        self.executor(self.step)
        self.slider.SetValue(self.step)    
        
    def Finish(self):
        self._alive = False
        self.step = 0
        self.frame.OnEnd()
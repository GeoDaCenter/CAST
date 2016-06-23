"""
"""

__author__  = "Xun Li <xunli@asu.edu>"
__all__ = ['MultiCoreProxy']

import os
from multiprocessing import *

class TaskProcessor:
    """
    The TaskProcessor class provides the functions necessary to process each task.
    """
    def __init__(self, numcalcs):
        """
        Initialise the TaskProcessor.
        """
        self.numcalcs = numcalcs
 
    def calculate(self, angle_deg):
        """
        Calculate the result of a task.
        """
        result = 0
        for i in range(self.numcalcs):
            angle_rad = math.radians(angle_deg)
            result += math.tanh(angle_rad)/math.cosh(angle_rad)/self.numcalcs
        return ( angle_deg, result )
    
class ObjectDispatcher:
    """
    The Dispatcher class manages the task and result queues.
    """
    def __init__(self):
        """
        Initialise the Dispatcher.
        """
        self.taskQueue = Queue()
        self.resultQueue = Queue()
 
    def putTask(self, task):
        """
        Put a task on the task queue.
        """
        self.taskQueue.put(task)
 
    def getTask(self):
        """
        Get a task from the task queue.
        """
        return self.taskQueue.get()
 
    def putResult(self, output):
        """
        Put a result on the result queue.
        """
        self.resultQueue.put(output)
 
    def getResult(self):
        """
        Get a result from the result queue.
        """
        return self.resultQueue.get()
    
class MultiCoreProxy:
    """
    The MultiCoreServer class provides a target worker class method for queued processes.
    """
    def __init__(self, numprocesses=1, tasks=[ ]):
        """
        Initialise the TaskServerMP and create the dispatcher and processes.
        """
        self.numprocesses = numprocesses
        self.Tasks = tasks
        self.numtasks = len(tasks)
 
        # Create the dispatcher
        self.dispatcher = Dispatcher()
 
        self.Processes = [ ]
 
        # The worker processes must be started here!
        for n in range(numprocesses):
            process = Process(target=MultiCoreProxy.worker, args=(self.dispatcher,))
            process.start()
            self.Processes.append(process)
 
        self.timeStart = 0.0
        self.timeElapsed = 0.0
        self.timeRemain = 0.0
        self.processTime = { }
 
        # Set some program flags
        self.keepgoing = True
        self.i = 0
        self.j = 0
 
    def run(self):
        """
        Run the MultiCoreProxy- start, stop & terminate processes.
        """
        if (self.numprocesses == 0):
            sys.stdout.write(' (no extra processes)')
        sys.stdout.write('\nUnordered results...\n')
        self.processTasks(self.update)
        if (self.keepgoing):
            sys.stdout.write('Time elapsed: %s\n' % time.strftime('%M:%S', time.gmtime(self.timeElapsed)))
        if (self.numprocesses > 0):
            sys.stdout.write("Waiting for processes to terminate...")
            self.processTerm()
 
    def processTasks(self, resfunc=None):
        """
        Start the execution of tasks by the processes.
        """
        self.keepgoing = True
 
        self.timeStart = time.time()
        # Set the initial process time for each
        for n in range(self.numprocesses):
            pid_str = '%d' % self.Processes[n].pid
            self.processTime[pid_str] = 0.0
 
        # Submit first set of tasks
        if (self.numprocesses == 0):
            numprocstart = 1
        else:
            numprocstart = min(self.numprocesses, self.numtasks)
        for self.i in range(numprocstart):
            self.dispatcher.putTask(self.Tasks[self.i])
 
        self.j = -1
        self.i = numprocstart - 1
        while (self.j < self.i):
            # Get and print results
            output = self.getOutput()
            # Execute some function (Yield to a wx.Button event)
            if (isinstance(resfunc, (types.FunctionType, types.MethodType))):
                resfunc(output)
            if ((self.keepgoing) and (self.i + 1 < self.numtasks)):
                # Submit another task
                self.i += 1
                self.dispatcher.putTask(self.Tasks[self.i])
 
    def processStop(self, resfunc=None):
        """
        Stop the execution of tasks by the processes.
        """
        self.keepgoing = False
 
        while (self.j < self.i):
            # Get and print any results remining in the done queue
            output = self.getOutput()
            if (isinstance(resfunc, (types.FunctionType, types.MethodType))):
                resfunc(output)
 
    def processTerm(self):
        """
        Stop the execution of tasks by the processes.
        """
        for n in range(self.numprocesses):
            # Terminate any running processes
            self.Processes[n].terminate()
 
        # Wait for all processes to stop
        while (self.anyAlive()):
            time.sleep(0.5)
 
    def anyAlive(self):
        """
        Check if any processes are alive.
        """
        isalive = False
        for n in range(self.numprocesses):
            isalive = (isalive or self.Processes[n].is_alive())
        return isalive
 
    def getOutput(self):
        """
        Get the output from one completed task.
        """
        self.j += 1
 
        if (self.numprocesses == 0):
            # Use the single-process method
            self.worker_sp()
 
        output = self.dispatcher.getResult()
        # Calculate the time remaining
        self.timeRemaining(self.j + 1, self.numtasks, output['process']['pid'])
 
        return(output)
 
    def timeRemaining(self, tasknum, numtasks, pid):
        """
        Calculate the time remaining for the processes to complete N tasks.
        """
        timeNow = time.time()
        self.timeElapsed = timeNow - self.timeStart
 
        pid_str = '%d' % pid
        self.processTime[pid_str] = self.timeElapsed
 
        # Calculate the average time elapsed for all of the processes
        timeElapsedAvg = 0.0
        numprocesses = self.numprocesses
        if (numprocesses == 0): numprocesses = 1
        for pid_str in self.processTime.keys():
            timeElapsedAvg += self.processTime[pid_str]/numprocesses
        self.timeRemain = timeElapsedAvg*(float(numtasks)/float(tasknum) - 1.0)
 
    def update(self, output):
        """
        Get and print the results from one completed task.
        """
        pass
 
    def worker(cls, dispatcher):
        """
        The worker creates a TaskProcessor object to calculate the result.
        """
        while True:
            args = dispatcher.getTask()
            taskproc = TaskProcessor(args[0])
            result = taskproc.calculate(args[1])
            # Put the result on the output queue
            dispatcher.putResult(output)
 
    # The multiprocessing worker must not require any existing object for execution!
    worker = classmethod(worker)
 
    def worker_sp(self):
        """
        A single-process version of the worker method.
        """
        args = self.dispatcher.getTask()
        taskproc = TaskProcessor(args[0])
        result = taskproc.calculate(args[1])
        # Put the result on the output queue
        self.dispatcher.putResult(output)

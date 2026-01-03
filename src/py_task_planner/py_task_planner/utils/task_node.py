######################################################################################
#
#          University of Applied Sciences, Laboratory of Autonomous Systems (LAS)              
######################################################################################

import threading
import time
import rclpy
from rclpy.node import Node

class TaskNode(Node):
    def __init__(self, node_name):
        super().__init__(node_name)
        self._thread = threading.Thread(target=self._running_task)
        self._thread_fn = None
        self._thread_args = {}
        self._thread_kwargs = {}
        self._thread_task_triggered = False
        self._thread.start()
        self._should_stop = threading.Event()
    
    def start_task(self, fn, *args, **kwargs):
        if self._thread_task_triggered:
            return False
        self._thread_fn = fn
        self._thread_args = args
        self._thread_kwargs = kwargs
        self._thread_task_triggered = True
        return True
    
    def stop_task(self):
        self._should_stop.set()
        
    def task_should_stop(self):
        '''Can be used in the task to check if it should be stopped'''
        return self._should_stop()
        
    def _running_task(self):
        while rclpy.ok():
            if self._thread_task_triggered:
                self.get_logger().info('Long-running task started.')
                self._thread_fn(*self._thread_args, **self._thread_kwargs)
                self.get_logger().info('Long-running task completed.')
                self._thread_task_triggered = False
            time.sleep(0.1)
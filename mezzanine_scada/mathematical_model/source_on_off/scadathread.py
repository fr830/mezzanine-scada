# -*- coding: UTF-8 -*-
"""
This app allow us to simulate a tank. This tank have a maximum volume, a initial volume 
an input flow and an output flow that would be two variables.

we can use other mathematical models with this one like level sensors that will change with the volume of the tank, valves or pumps
that will modify the input or output flow, ...



"""



import threading
import logging
from .models import source_on_off
from .source_on_off import source_on_off_simulator



class scadathread(threading.Thread):
    def __init__(self,
                 server=None,
                 database=None,
                 end=threading.Event(),
                 debug_logger=logging):       
        threading.Thread.__init__(self)  
        print('en __init__ de scadathread')
        self.logger=debug_logger
        self.database=database
        self.end=end
        self.thread_list={}
        for var_onoff in source_on_off.objects.all():
#            try:
            if 1:
                print(1)
                source_on_off_instance=source_on_off_simulator(database=self.database,
                                                               end=self.end,
                                                               logger=self.logger,
                                                               flow_off=var_onoff.flow_off,
                                                               flow_on=var_onoff.flow_on,
                                                               input_var=var_onoff.input_variable.name,
                                                               flow_var=var_onoff.flow_variable.name,
                                                               init_state=var_onoff.input_variable.default_value)
                self.thread_list[var_onoff.name]=source_on_off_instance
                print(2)
#            except:
#                self.logger.error('Error creating source on/off: %s' %var_onoff.name)
#                print('error creating the thread of '+var_onoff.name)
#                continue
    def run(self):
        for thread_name in self.thread_list:
            self.thread_list[thread_name].start()
        for thread_name in self.thread_list:
            self.thread_list[thread_name].join()



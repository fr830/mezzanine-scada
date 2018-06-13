# -*- coding: UTF-8 -*-
from daemon import Daemon
from threading import Event
from mezzanine_scada.base.database import variable_database
from mezzanine_scada.base.models import variable, scada_config
from time import time, sleep





#script para generar un servicio al ejecutar con start/stop/restart


import logging
from logging.handlers import SysLogHandler


from service import find_syslog, Service

#this should be in the django database
LOGGER_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'short': {
            'format': '%(asctime)s:%(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'INFO',
            'class':'logging.StreamHandler',
        },
        'fileHandler': {
            'level':'ERROR',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/home/paco/eclipse/python/EDSolar/scada/scada/logs/log_scada.log',
            'mode':'a',
            'maxBytes': 10485760,
            'backupCount': 500,
            'formatter':'standard',
        },
        'consoleHandler': {
            'level':'ERROR',
            'class':'logging.StreamHandler',
            'formatter':'short',
        },
    },
    'loggers': {
        'simple_scada': {
            'handlers': ['fileHandler','consoleHandler'],
            'level': 'ERROR',
            'propagate': False
        },
    }
}

TXTRECORDS_DIR='/home/paco/eclipse/python/EDSolar/scada/scada/data'
TXTRECORDS_T=10.0




class ScadaService(Service):
    def __init__(self, *args, **kwargs):
        super(ScadaService, self).__init__(*args, **kwargs)
        settings=scada_config.objects.first()
        file_handler = logging.FileHandler(settings.logging_file)
        file_handler.setLevel(settings.logging_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def stop(self):
        #stop makes end_event true so all threads ends. For more security, sends kill signals 
        self.end_event.set()
        self.realtime_db.set_all_events()
        sleep(10)
        return super(ScadaService,self).stop()

    def start(self):
        #this event ends the daemon
        self.end_event=Event()
        #realtime database instance
        self.realtime_db=variable_database(name='Data Base')
        #pre-create all variables
        for var in variable.objects.all():
            self.realtime_db.set_value(name=var.name,value=var.default_value,t_aquisition=time())
#si se carga la app backup, crear un hilo de su tipo
#        self.backup_thread=backup_textfile(variable_names=variable_names,
#                                           sensor_gui_names=sensor_gui_names,
#                                           sampling_time=settings.TXTRECORDS_T,
#                                           data_path=settings.TXTRECORDS_DIR, 
#                                           database=self.realtime_db,
#                                           end=self.end_event,
#                                           debug_logger=self.logger)
#        self.hilo_backup.setName('backup')
#hilo_backup.start()
#lista_hilos.append(hilo_backup)
#
#Every app in django, if is an instrument then load the thread/threads for every instruent 
#for every output variable, add a thread that wait for a change in the database and then send the new value to the real world
#if the state machine app is loaded, for every control state machine add a thread 
        return super(ScadaService,self).start()
    
    def restart(self):
        self.stop()
        self.start()
    
    def run(self):
        while not self.got_sigterm():
            self.logger.info("I'm working...")
            sleep(5)

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        sys.exit('Syntax: %s COMMAND' % sys.argv[0])

    cmd = sys.argv[1].lower()
    service = ScadaService('scada_service', pid_dir='/tmp')

    if cmd == 'start':
        service.start()
    elif cmd == 'stop':
        service.stop()
    elif cmd == 'restart':
        service.stop()
        sleep(10.0)
        service.start()
    elif cmd == 'status':
        if service.is_running():
            print "Service is running."
        else:
            print "Service is not running."
    else:
        sys.exit('Unknown command "%s".' % cmd)




"""
#an event that makes all daemon to stop
end_event=Event()

#realtime database instance
realtime_db=variable_database(name='Data Base')
#pre-create all variables
for var in variable.objects.all():
    realtime_db.set_value(name=var.name,value=var.default_value,t_aquisition=time())

#one thread for every output variable. This thread waits for a change in the variable and then it sends the new value to the real world
#for var in variable.objects.filter(direction='output'):
#    new_thread=output_variable_thread(instrument=output_channels[signal_name]['driver'],
#                              database=realtime_db,
#                              name=signal_name,
#                              nchannel=output_channels[signal_name]['nchannel'],
#                              end=end_event,
#                              debug_logger=logger)
#
#hilo_backup=backup_textfile(sensor_names=sensor_names,
#                            sensor_gui_names=sensor_gui_names,
#                            sampling_time=settings.TXTRECORDS_T,
#                            data_path=settings.TXTRECORDS_DIR, 
#                            database=realtime_db,
#                            end=evento_salir,
#                            debug_logger=logger)
#hilo_backup.setName('backup')
#hilo_backup.start()
#lista_hilos.append(hilo_backup)

#a thread for every state machine (controls) available
#
#
#
"""

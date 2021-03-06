# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from mezzanine_scada.base.database import variable_database
from mezzanine_scada.base.models import variable, scada_config

import time
import logging
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from xmlrpc.client import ServerProxy

from secrets import token_hex
import threading 
import daemon
from django.conf import settings
from importlib import import_module



#this class handles the client request
#change the path to http://ip:port/RPC2
#It only serves request from localhost. This is important for security reasons
#It's an extra precaution because if the xmlrpc server is listening to localhost
#It shouldn't allow external IP to access
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)
    def do_POST(self):
        ip_address, ip_port = self.client_address
        if ip_address!='127.0.0.1':
            self.report_404()
            return
        SimpleXMLRPCRequestHandler.do_POST(self)

class xmlrpcserver_killer(threading.Thread):  
    def __init__(self, server=None,debug_logger=logging):  
        threading.Thread.__init__(self)  
        self.server=server
        self.logger=debug_logger
    def shutdown_daemon(self):
        self.start()
        return 'done'
    def run(self):
        #We want to end the serve_forever method in the server class. The proper method to do this is calling the shutdown method from another thread
        #the user python3 manage.py daemons stop command call the start method of this class by a xmlrpc call. This method just calls the shutdown method 
        #of the server
        try:
            self.server.shutdown()
            self.logger.info('XMLRPC Server shut down')
        except:
            self.logger.error('Error shutting down the XMLRPC Server')





class ScadaDaemon:
    def __init__(self):
        self.settings=scada_config.objects.first()
        logging.basicConfig(level=self.settings.logging_level,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            filename=self.settings.logging_file,
                            filemode='w')
        self.logger=logging 
    def stop(self):
        #conect with the server and end the daemon
        try:
            #it should use https if this is going to be on the internet
            proxy = ServerProxy('http://localhost:%i' %self.settings.server_port)
            proxy.shutdown_daemon()
        except:
            message="DAEMON can't stop"
            print(message)
            self.logger.error(message)
    
    def start(self):
        #the password is one use only
        self.settings.server_password=token_hex(16)
        self.settings.save()
        #create all instances and run all threads
        #a dictionary of threads that are executing
        self.thread_list={}
        #this event ends the daemon
        self.end_event=threading.Event()
        #realtime database instance
        self.realtime_db=variable_database(name='Data Base')
        #pre-create all variables
        for var in variable.objects.all():
            self.realtime_db.set_value(name=var.name,value=var.default_value,t_aquisition=time.time())
        #execute all threads needed
        #thread for saving variable values to files
        #hardware related threads
        #one thread for each output variable
        #one thread for each input type of hardware
        #control related threads
        #a xmlrpc server to be able to access methods from outside this process
        #this should use https if it is going to be in a unsafe net
        self.server = SimpleXMLRPCServer(("localhost", self.settings.server_port),
                                          requestHandler=RequestHandler)
        self.server.register_introspection_functions()
        self.server.register_function(self.realtime_db.set_value)
        self.server.register_function(self.realtime_db.get_multiple_value)
        #to kill a xmlrpc server another thread must call the shutdown function
        self.thread_list['server killer']=xmlrpcserver_killer(server=self.server,debug_logger=self.logger)
        self.server.register_function(self.thread_list['server killer'].shutdown_daemon,"shutdown_daemon")
        #run a thread for each app that has a scadathread file with a scadathread class in it
        for app in settings.INSTALLED_APPS:
            if app == 'mezzanine_scada.base':
                continue
            if 'mezzanine_scada.' in app:
                try:
                    app_complete_path=app+'.scadathread'
                    print(app_complete_path)
                    app_thread=import_module(app_complete_path).scadathread
                    self.thread_list[app]=app_thread(server=self.server,
                                                     database=self.realtime_db,
                                                     end=self.end_event,
                                                     debug_logger=self.logger)
                    self.thread_list[app].start()
                    print(app+' thread loaded')
                except:
                    self.logger.debug('APP %s cant load scadathread' %app)
        self.server.serve_forever()
        #the service is shutting down, wait for all threads to end
        self.end_event.set()
        for thread_name in self.thread_list:
            self.thread_list[thread_name].join()
            self.logger.info('Thread %s ended' %thread_name)            
            print('Thread %s ended' %thread_name)


class Command(BaseCommand):
    help = 'command that load all threads in mezzanine-scada'
    def add_arguments(self, parser):
        parser.add_argument('action', choices=['start', 'stop'], nargs='+', type=str)
    def handle(self, *args, **options):
        #service instance
        scada = ScadaDaemon()
        if 'start' == options['action'][0]:
            scada.start()
        elif 'stop' == options['action'][0]:
            scada.stop()

"""
This version can execute start as a daemon. Use this if you want a command that can load the daemon at his own
Is better a non daemonized version and use systemd to daemonize the thread

#daemonized version
class Command(BaseCommand):
    help = 'command that load all threads in mezzanine-scada'
    def add_arguments(self, parser):
        parser.add_argument('action', choices=['start', 'stop'], nargs='+', type=str)
    def handle(self, *args, **options):
        #service instance
        scada = ScadaDaemon()
        if 'start' == options['action'][0]:
            with daemon.DaemonContext():
                scada.start()
        elif 'stop' == options['action'][0]:
            scada.stop()
 

"""

    


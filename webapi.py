import sys
import requests
import subprocess
import time

from PyQt5.QtCore import QSettings, pyqtSignal, QObject

class WebApi(QObject):

    # HOST = 'https://ekranya.onrender.com'
    HOST = 'https://ekrana-cro.amvera.io'
    TIMEOUT = 5

    checking_server_connection_finished = pyqtSignal(bool)
    checking_activation_finished = pyqtSignal(bool)
    adding_activation_finished = pyqtSignal(bool)


    def __init__(self):
        super().__init__()
        self.settings = QSettings('Ekranya', 'IMax',  None)

        
    def check_server_connection(self):
        try:
            start = time.perf_counter()
            requests.get(self.HOST, timeout=self.TIMEOUT)
            spend = start-time.perf_counter()
            if spend < 1:
                time.sleep(1 - spend)
            self.checking_server_connection_finished.emit(True)
        except: 
            self.checking_server_connection_finished.emit(False)
            
    def check_activation(self):
        try:
            key = self.settings.value('key')
            machine = self.settings.value('machine')
            if requests.get(f'{self.HOST}/isactivated/', params={'key': key, 'machine': machine}, timeout=self.TIMEOUT).json()['success'] == True:
                self.checking_activation_finished.emit(True)
            else:
                self.checking_activation_finished.emit(False)
        except:
            self.checking_activation_finished.emit(False)
         
    def add_activation(self, key):
        try:            
            machine = self.get_machine_id()  
            if requests.post(f'{self.HOST}/addactivation/', params={'key': key, 'machine': machine}, timeout=self.TIMEOUT).json()['success'] == True:
                self.settings.setValue('key', key)
                self.settings.setValue('machine', machine)
                self.adding_activation_finished.emit(True)
            else: 
                self.adding_activation_finished.emit(False)              
        except:
            self.adding_activation_finished.emit(False)
        
    def get_machine_id(self):
        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            uuid = str(subprocess.check_output('wmic csproduct get UUID', startupinfo=startupinfo), 'utf-8').split('\n')[1].strip()
            return uuid
        else:
            return ''
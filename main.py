import sys
import os
from threading import Thread

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSlot

from ekranya import Ekranya as Project
from webapi import WebApi
from activation import ActivationWindow, StartWidget
from stylesheet import StyleSheet


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def start_project():    
    project.show()

@pyqtSlot(bool) 
def on_check_server_connection(success):
    if not success:
       start_widget.close()
       activation_dialog.switch_to_no_connection_widget()
       activation_dialog.show()
    else:
        Thread(target=wapi.check_activation).start()

@pyqtSlot(bool) 
def on_check_activation(success):
    start_widget.close()
    if not success:
        activation_dialog.switch_to_activation_widget()
        activation_dialog.show()
    else:        
        start_project()

@pyqtSlot(bool)
def on_add_activation(success):
    if not success:
        activation_dialog.switch_to_error_widget()
    else:
        activation_dialog.switch_to_ok_widget()

@pyqtSlot(str)
def on_activate_key(key):
    Thread(target=wapi.add_activation, args=(key,)).start() 

def resolve_icon_file():
    try:
        icon_folder = resource_path(Project.ICON_FOLDER)
        for file in os.listdir(icon_folder):
            if file.endswith(Project.ICON_EXTENSION):
                return(resource_path(os.path.join(icon_folder, file)))
    except FileNotFoundError:
        raise

def resolve_image_file():
    try:
        image_folder = resource_path(Project.IMAGE_FOLDER)
        for file in os.listdir(image_folder):
            if file.endswith(Project.IMAGE_EXTENSION):
                return(resource_path(os.path.join(image_folder, file)))
    except FileNotFoundError:
        raise


if __name__ == '__main__':           
    app = QApplication(sys.argv) 

    os.environ["QT_ENABLE_HIGHDPI_SCALING"]   = '1'
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = '1'
    os.environ["QT_SCALE_FACTOR"]             = '1'

    icon_file = resolve_icon_file()
    image_file = resolve_image_file()
    
    sh = StyleSheet(bg=resource_path(os.path.join('res','background.png')),
                    close_icon=resource_path(os.path.join('res', 'close_icon.png')),
                    close_icon_hover=resource_path(os.path.join('res', 'close_icon_hover.png')))
    app.setStyleSheet(sh.stylesheet)

    project = Project(icon=resource_path(icon_file),
                      image=resource_path(image_file))

    activation_dialog = ActivationWindow(icon=resource_path(icon_file),
                                         splash_image=resource_path(os.path.join('res', 'head.png')),
                                         vk_icon=resource_path(os.path.join('res', 'vk_icon.png')))
    activation_dialog.activation_widget_success.button_clicked.connect(start_project) 
    activation_dialog.activate_key.connect(on_activate_key)   

    wapi = WebApi()
    wapi.checking_server_connection_finished.connect(on_check_server_connection)
    wapi.checking_activation_finished.connect(on_check_activation)
    wapi.adding_activation_finished.connect(on_add_activation)

    start_widget = StartWidget(icon=resource_path(icon_file),
                               image=resource_path(os.path.join('res', 'start_image.png'))) 
    start_widget.show()
    
    Thread(target=wapi.check_server_connection).start()

    # activation_dialog.switch_to_error_widget()
    # activation_dialog.switch_to_activation_widget()
    # activation_dialog.switch_to_no_connection_widget()
    # activation_dialog.switch_to_splash_screen_widget()
    # activation_dialog.switch_to_ok_widget()
    # activation_dialog.show()

    app.installEventFilter(project) 
    sys.exit(app.exec_())  
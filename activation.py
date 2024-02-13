from PIL import Image 
from enum import Enum
import webbrowser

from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QLineEdit, QPushButton, QStackedWidget, QDesktopWidget, QFrame
from PyQt5.QtGui import QFont, QPixmap, QPainter, QIcon
from PyQt5.QtCore import QEvent, QPoint, pyqtSignal, pyqtSlot, Qt, pyqtProperty, QPropertyAnimation, QSequentialAnimationGroup, QEasingCurve, QSize, QEvent

import messages


class WindowState(Enum):
    
    NO_CONNECTION = 0
    ACTIVATION = 1
    ACTIVATION_OK = 2
    ACTIVATION_ERROR = 3
    SPLASH_SCREEN = 4    


class CustomButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)


class CloseButton(CustomButton):

    def __init__(self, text, parent=None):
        super().__init__(text, parent)  


class LinkButton(CustomButton):

    def __init__(self, text, parent=None):
        super().__init__(text, parent)     


class ActivationWindow(QMainWindow):

    activate_key = pyqtSignal(str)

    def __init__(self, icon, splash_image, vk_icon):
        super().__init__()
        
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setWindowIcon(QIcon(icon))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.no_connection_widget = ActivationMessageWidget(messages.server_connection_failed, vk_icon)
        self.activation_widget = ActivationWidget()
        self.activation_widget_success = ActivationMessageWidget(messages.activation_succeed, vk_icon)
        self.activation_widget_fail = ActivationFailedMessageWidget(messages.activation_failed, vk_icon)
        self.splash_screen_widget = SplashScreenWidget(splash_image)

        self.no_connection_widget.button_clicked.connect(self.close)
        self.no_connection_widget.close_button_clicked.connect(self.close)
        self.activation_widget.button_clicked.connect(self.activate)
        self.activation_widget.close_button_clicked.connect(self.close)
        self.activation_widget_success.button_clicked.connect(self.close)
        self.activation_widget_success.close_button_clicked.connect(self.close)
        self.activation_widget_fail.button_clicked.connect(self.close)
        self.activation_widget_fail.link_clicked.connect(self.on_link_button_clicked)
        self.activation_widget_fail.close_button_clicked.connect(self.close)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.no_connection_widget)
        self.stacked_widget.addWidget(self.activation_widget)
        self.stacked_widget.addWidget(self.activation_widget_success)
        self.stacked_widget.addWidget(self.activation_widget_fail) 
        self.stacked_widget.addWidget(self.splash_screen_widget)
        
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.stacked_widget)
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.setWindowTitle('Активация')
        self.center()

        self.oldPos = None
        self.is_dragging = False
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def switch_to_no_connection_widget(self):
        self.move(self.x()-(490-self.width())//2, self.y()-(350-self.height())//2)
        self.setFixedSize(490, 350) 
        self.stacked_widget.setCurrentIndex(WindowState.NO_CONNECTION.value)
    
    def switch_to_activation_widget(self):
        self.move(self.x()-(490-self.width())//2, self.y()-(250-self.height())//2)
        self.setFixedSize(490, 250) 
        self.stacked_widget.widget(WindowState.ACTIVATION.value).line_edit.setText('')
        self.stacked_widget.widget(WindowState.ACTIVATION.value).line_edit.setFocus()
        self.stacked_widget.setCurrentIndex(WindowState.ACTIVATION.value)
    
    def switch_to_ok_widget(self):
        self.move(self.x()-(490-self.width())//2, self.y()-(350-self.height())//2)
        self.setFixedSize(490, 350) 
        self.stacked_widget.setCurrentIndex(WindowState.ACTIVATION_OK.value)

    def switch_to_error_widget(self):
        self.move(self.x()-(490-self.width())//2, self.y()-(375-self.height())//2)
        self.setFixedSize(490, 375)         
        self.stacked_widget.setCurrentIndex(WindowState.ACTIVATION_ERROR.value)
        
    
    def switch_to_splash_screen_widget(self):
        self.move(self.x()-(490-self.width())//2, self.y()-(200-self.height())//2)
        self.setFixedSize(490, 200) 
        self.stacked_widget.setCurrentIndex(WindowState.SPLASH_SCREEN.value)
    
    def activate(self, key): 
        self.switch_to_splash_screen_widget()   
        self.activate_key.emit(key) 

    @pyqtSlot()
    def on_link_button_clicked(self):
        self.switch_to_activation_widget()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if event.pos().x() < 440 and event.pos().y() < 50:
                self.oldPos = event.globalPos()
                self.x_oldpos, self.y_oldpos = self.x(), self.y()
                self.is_dragging = True
            else:
                self.is_dragging = False

    def mouseMoveEvent(self, event):       
        if self.oldPos and self.is_dragging:         
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()  
                 

class ActivationMessageWidget(QWidget):
    
    button_clicked = pyqtSignal()
    close_button_clicked = pyqtSignal()

    def __init__(self, text, icon):
        super().__init__()

        self.init_ui(text, icon)

    def init_ui(self, text, icon):

        self.label = QLabel(text)     
        self.frame = QFrame()
        self.frame.setFixedHeight(40)
        self.label.setAlignment(Qt.AlignCenter)
        self.link_button = CustomButton('')
        self.link_button.setIcon(QIcon(icon))
        self.link_button.setIconSize(QSize(48, 48))
        self.link_button.setStyleSheet('')
        self.link_button.clicked.connect(self.open_link)
        self.button = QPushButton('Хорошо')    
        self.button.clicked.connect(self.button_clicked.emit)   

        self.toplayout = QHBoxLayout()
        self.layout1 = QHBoxLayout()
        self.layout2 = QHBoxLayout()
        self.layout3 = QHBoxLayout()        
        self.layout = QVBoxLayout() 

        self.toplayout.addWidget(self.frame)
        self.layout1.addWidget(self.label)
        self.layout2.addWidget(self.link_button)       
        self.layout3.addStretch(1)
        self.layout3.addWidget(self.button)

        self.layout.addLayout(self.toplayout)
        self.layout.addStretch(1)
        self.layout.addLayout(self.layout1)       
        self.layout.addStretch(1)      
        self.layout.addLayout(self.layout2)
        self.layout.addStretch(1)
        self.layout.addLayout(self.layout3)
        self.layout.addStretch(1)
        
        self.setLayout(self.layout)

        self.close_button = CloseButton('', self)
        self.close_button.setGeometry(440, 5, 24, 24)
        self.close_button.clicked.connect(self.close_button_clicked)

    @pyqtSlot()
    def open_link(self):
        webbrowser.open('https://vk.com/koralinalogoped')


class ActivationFailedMessageWidget(ActivationMessageWidget):

    link_clicked = pyqtSignal()
    
    def __init__(self, text, icon):
        super().__init__(text, icon)

        self.link_button = LinkButton('🗝 ввести ключ еще раз', self)
        self.link_button.setGeometry(10, 325, 180, 20)
        self.link_button.clicked.connect(self.link_button_clicked)        

    @pyqtSlot()
    def link_button_clicked(self):
        self.link_clicked.emit()
        e = QEvent(QEvent.Leave)
        QApplication.sendEvent(self.link_button, e)


class ActivationWidget(QWidget):

    button_clicked = pyqtSignal(str)
    close_button_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.init_ui()        

    def init_ui(self):
        
        self.frame = QFrame()
        self.frame.setFixedHeight(40)       
        self.label = QLabel('🗝 Пожалуйста, введите ключ активации ')
        self.label.setAlignment(Qt.AlignCenter)
        self.line_edit = QLineEdit()
        self.line_edit.setMaxLength(35)
        self.line_edit.setAlignment(Qt.AlignCenter)
        self.line_edit.returnPressed.connect(self.on_button_clicked)
        self.button = QPushButton('Принять')    
        self.button.clicked.connect(self.on_button_clicked)        

        self.toplayout = QHBoxLayout()
        self.hlayout1 = QHBoxLayout()
        self.hlayout2 = QHBoxLayout()
        self.hlayout3 = QHBoxLayout()
        self.layout = QVBoxLayout() 
        
        self.toplayout.addWidget(self.frame)
        self.hlayout1.addWidget(self.label)
        self.hlayout2.addWidget(self.line_edit)
        self.hlayout3.addStretch(1)
        self.hlayout3.addWidget(self.button)

        self.layout.addLayout(self.toplayout) 
        self.layout.addStretch(1)
        self.layout.addLayout(self.hlayout1)       
        self.layout.addStretch(1)
        self.layout.addLayout(self.hlayout2)
        self.layout.addStretch(1)
        self.layout.addLayout(self.hlayout3)
        self.layout.addStretch(1)
        
        self.setLayout(self.layout)  

        self.close_button = CloseButton('', self)
        self.close_button.setGeometry(440, 5, 24, 24)
        self.close_button.clicked.connect(self.close_button_clicked)

    def on_button_clicked(self):
        key = self.line_edit.text()       
        self.button_clicked.emit(key) 


class SplashScreenWidget(QWidget):
    
    def __init__(self, iamge):
        super().__init__()

        self.image = SplashImage(self)
        self.image.setPixmap(QPixmap(iamge))
        _layout = QVBoxLayout(self)                                      
        _layout.addWidget(self.image) 

        self.animate()

    def animate(self):
        self.swingup_anim = QPropertyAnimation(self, b"pos")
        self.swingup_anim.setEasingCurve(QEasingCurve.Linear)
        self.swingup_anim.setEndValue(QPoint(self.x(), self.y()+30))
        self.swingup_anim.setDuration(700)
        self.swingdown_anim = QPropertyAnimation(self, b"pos")
        self.swingdown_anim.setEasingCurve(QEasingCurve.Linear)
        self.swingdown_anim.setEndValue(QPoint(self.x(), self.y()))
        self.swingdown_anim.setDuration(700)
        self.anim_group = QSequentialAnimationGroup()        
        self.anim_group.addAnimation(self.swingup_anim)
        self.anim_group.addAnimation(self.swingdown_anim)
        self.anim_group.setLoopCount(-1)      
        self.anim_group.start() 
        

class SplashImage(QWidget):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.p = QPixmap()
        self._angle = 0    

    def setPixmap(self, p):
        self.p = p
        self.update()

    def paintEvent(self, event):
        if not self.p.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)  
            painter.translate(self.width() / 2, self.height() / 2)
            painter.rotate(self._angle)
            painter.translate(-self.width() / 2, -self.height() / 2)
            painter.drawPixmap(self.rect(), self.p)
    
    @pyqtProperty(int)
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self.update()


class StartWidget(QWidget):

    def __init__(self, icon, image):
        super().__init__()  

        self.setWindowIcon(QIcon(icon))                   

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint)  
        
        try:
            self._imagefile = image
        except FileNotFoundError:
            raise
        
        im = Image.open(self._imagefile) 
            
        self.base_width, self.base_height = im.size
        
        self.screen = QApplication.primaryScreen()  
        
        _layout = QVBoxLayout(self)                  
        self.label = ImageWidget(self)
        self.label.setPixmap(QPixmap(self._imagefile))        
        _layout.addWidget(self.label)  
        self.resize(*im.size) 

class ImageWidget(QWidget):

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.p = QPixmap()

    def setPixmap(self, p):
        self.p = p
        self.update()

    def paintEvent(self, event):
        if not self.p.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.drawPixmap(self.rect(), self.p) 

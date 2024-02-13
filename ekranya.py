from PIL import Image 

from PyQt5.QtWidgets import  QApplication, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QCursor, QIcon
from PyQt5.QtCore import QPoint, Qt, QTimer

from activation import ImageWidget


class Ekranya(QWidget): 

    IMAGE_FOLDER = 'image'
    IMAGE_EXTENSION = '.png'
    ICON_FOLDER = 'icon'
    ICON_EXTENSION = '.ico'

    def __init__(self, icon, image):
        super().__init__()  

        self.setWindowIcon(QIcon(icon))

        self.setMouseTracking(True)

        self.locked = False
        self.window_x = 0
        self.window_y = 0
        self.window_width = 0
        self.window_height = 0
        self.start_x = 0
        self.start_y = 0 
        self.end_x = 0 
        self.end_y = 0               

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        try:
            self._imagefile = image
        except FileNotFoundError:
            raise
        
        im = Image.open(self._imagefile)        
        max_height = 305
        if im.size[1] > max_height:
            im.thumbnail((im.size[0]*max_height/im.size[1], max_height))
            
        self.base_width, self.base_height = im.size
        
        self.screen = QApplication.primaryScreen()  
        
        _layout = QVBoxLayout(self)                  
        self.label = ImageWidget(self)
        self.label.setPixmap(QPixmap(self._imagefile))
        self.label.setMouseTracking(True)
        _layout.addWidget(self.label)  
        self.resize(*im.size)      
        self._is_moving = False 

        self.timer = QTimer(self)
        self.timer.setInterval(5)
        self.timer.timeout.connect(self.pollCursor)
        self.timer.start()
        self._offset = None

    def pollCursor(self):
        cursor = QCursor
        if self._is_moving:            
            self.move(cursor.pos().x() - self._offset.x(), cursor.pos().y() - self._offset.y())
    
    def mousePressEvent(self, event):      
        if event.button() == Qt.LeftButton:
            if not self._is_moving:                
                self._is_moving = True
                self.setCursor(Qt.BlankCursor)

                cursor = QCursor
                self._offset = QPoint(cursor.pos().x() - self.x(), cursor.pos().y() - self.y())    
                self._offset_x_ratio = (cursor.pos().x() - self.label.mapToGlobal(QPoint(0,0)).x()) / self.label.width()
                self._offset_y_ratio = (cursor.pos().y() - self.label.mapToGlobal(QPoint(0,0)).y()) / self.label.height()
            else:
                self._is_moving = False
                self.unsetCursor()

    def wheelEvent(self, event):
        delta = int(event.angleDelta().y() / 6)        
        new_width = self.width() + delta
        new_height = self.height() + delta        
        if new_width >= self.base_width and\
           new_width < self.screen.size().width() and\
           new_height >= self.base_height and\
           new_height < self.screen.size().height(): 
            cursor = QCursor
            x_ratio = (cursor.pos().x() - self.label.mapToGlobal(QPoint(0,0)).x()) / self.label.width()
            y_ratio = (cursor.pos().y() - self.label.mapToGlobal(QPoint(0,0)).y()) / self.label.height()
            
            self.resize(new_width, new_height)
            self.move(self.x() - round(delta * x_ratio),
                      self.y() - round(delta * y_ratio))
            if self._offset:
                self._offset = QPoint(self._offset.x() + round(delta * self._offset_x_ratio), self._offset.y() + round(delta * self._offset_y_ratio))
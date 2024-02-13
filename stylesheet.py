from activation import CloseButton

class StyleSheet:

    def __init__(self, bg, close_icon, close_icon_hover):
        self.bg = bg
        self.close_icon = close_icon
        self.close_icon_hover = close_icon_hover 

    @property
    def stylesheet(self):
        sh =  ''' 
        * {            
            font-size: 12pt;            
        }

        QMainWindow {
            background-image: url(%s);             
            
        }

        QLabel{
            color: white
        }

        QLineEdit{
            background-color: white;
            color: #541B5F;
            font-size: 14pt;
            font-weight: bold;
            border: 5px solid white;
            border-radius: 10;
        }

        QPushButton{
            background-color: white;
            border: 5px solid white;
            border-radius: 10;
            color: #541B5F;            
        }

        QPushButton:hover{
            background-color: #C1C1C1;
            border: 5px solid #C1C1C1;
        } 

        CustomButton{
            background-color: transparent;
            border: 0px ;
            border-radius: 0;
        } 

        CustomButton:hover{
            background-color: transparent;
            border: 0px;
        }  

        CloseButton{
            border-image: url(%s);
            background-repeat: no-repeat;
        }

        CloseButton:hover {
            border-image: url(%s);
            background-repeat: no-repeat;
        }

        LinkButton{  
            color: white;
            text-decoration: underline;                    
        }

        LinkButton:hover{
            color: #C1C1C1;          
        }
        '''
        return sh %  (self.to_url(self.bg),
                        self.to_url(self.close_icon),
                        self.to_url(self.close_icon_hover))
    
    def to_url(self, path: str) -> str:
        return path.replace('\\', '/')

        

 
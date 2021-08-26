from qgis.gui import QgsMapTool 

class CoordinatesSelectorTool(QgsMapTool):   
    def __init__(self, canvas, label):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas    
        self.label = label    

    def canvasPressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        self.label.setText('x:{} || y:{}'.format(x,y))
        

    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

        print('The cordinates are: ', point)

    def canvasReleaseEvent(self, event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

    def activate(self):
        pass

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
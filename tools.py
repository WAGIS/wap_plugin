from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import QgsPointXY, QgsWkbTypes
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor 

from shapely.geometry import Polygon

class CoordinatesSelectorTool(QgsMapTool):   
    def __init__(self, canvas, label):
        QgsMapTool.__init__(self, canvas)
        
        self.canvas = canvas    
        self.label = label    

        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry )
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setFillColor(QColor(0,255,0,0))
        self.rubberBand.setWidth(1)
        self.reset()

    def reset(self):
        self.rubberCoordinates = list()
        self.polygonCoordinates = list()

        self.isEmittingPoint = False
        self.rubberBand.reset(True)
    
    def updateShape(self):
        self.rubberBand.reset(True)
        for idx, point in enumerate(self.rubberCoordinates):
            if idx != len(self.rubberCoordinates)-1:
                self.rubberBand.addPoint(QgsPointXY(point.x(), point.y()), False)
            else:
                self.rubberBand.addPoint(QgsPointXY(point.x(), point.y()), True) # true to update canvas
        self.rubberBand.show()

    def canvasPressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        self.label.setText('x:{} || y:{}'.format(x,y))

        self.rubberCoordinates.append(self.toMapCoordinates(event.pos()))
        # self.polygonCoordinates.append((float(self.toMapCoordinates(event.pos()).x()),
        #                                 float(self.toMapCoordinates(event.pos()).y())))

        self.polygonCoordinates.append([float(self.toMapCoordinates(event.pos()).x()),
                                        float(self.toMapCoordinates(event.pos()).y())])

        print(self.rubberCoordinates)
        print(self.polygonCoordinates)

        self.isEmittingPoint = True
        self.updateShape()

        
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
        self.setCursor(Qt.CrossCursor)
        self.reset()

    def deactivate(self):
        pass

    def getCoordinatesBuffer(self):
        self.rubberBand.closePoints(True)
        polygon = Polygon(self.polygonCoordinates)
        if polygon.is_valid:
            self.label.setText('{} vertex sel.'.format(len(self.polygonCoordinates)))
            self.polygonCoordinates.append(self.polygonCoordinates[0])
            return self.polygonCoordinates
        else:
            self.label.setText('Shape not valid')
            return None

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
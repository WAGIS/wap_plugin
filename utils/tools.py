from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import QgsPointXY, QgsWkbTypes
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor 

from .geometry import isValid

class CoordinatesSelectorTool(QgsMapTool):   
    """
        Class used to define a tool to select coordinates from the canvas of QGIS.

        ...

        Attributes
        ----------
        canvas : QgsCanvas
            Canvas from which the coordinates will be selected.
        label : QtLabel
            Label to comunicate events from the tool.
        savePolygonButton : QtButton
            Button to coordinate the closure of the polygon.
        rubberBand : QgsRubberBand
            Entity to storage the coordinates and draw the resulting polygon in
            canvas.

        Methods
        -------

    """
    def __init__(self, canvas, label, savePolygonButton):
        QgsMapTool.__init__(self, canvas)
        
        self.canvas = canvas    
        self.label = label    
        self.savePolygonButton = savePolygonButton

        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry )
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setFillColor(QColor(0,255,0,0))
        self.rubberBand.setWidth(1)
        self.reset()

    def reset(self):
        """
            Resets the coordinates storaged by the tool and clean the canvas.
        """
        self.rubberCoordinates = list()
        self.polygonCoordinates = list()

        self.rubberBand.reset()
    
    def updateShape(self):
        """
            Updates the coordinates storaged by the tool and refreshes the canvas.
        """
        self.rubberBand.reset()
        for idx, point in enumerate(self.rubberCoordinates):
            if idx != len(self.rubberCoordinates)-1:
                self.rubberBand.addPoint(QgsPointXY(point.x(), point.y()), False)
            else:
                self.rubberBand.addPoint(QgsPointXY(point.x(), point.y()), True) # true to update canvas
        self.rubberBand.show()

    def canvasPressEvent(self, event):
        """
            Captures the press events held on the canvas.
            ...
            Parameters
            ----------
            event : PressEvent
                Holds the information associated to the press event over the canvas.
        """
        x = float(self.toMapCoordinates(event.pos()).x())
        y = float(self.toMapCoordinates(event.pos()).y())
        self.label.setText('x:{} || y:{}'.format(x,y))

        self.rubberCoordinates.append(self.toMapCoordinates(event.pos()))
        self.polygonCoordinates.append([x,y])

        if not self.savePolygonButton.isEnabled() and len(self.rubberCoordinates) > 2:
            self.savePolygonButton.setEnabled(True)

        print(self.rubberCoordinates)
        print(self.polygonCoordinates)

        self.updateShape()

        
    def canvasMoveEvent(self, event):
        """
            Captures the move events held on the canvas.
            ...
            Parameters
            ----------
            event : MoveEvent
                Holds the information associated to the move event over the canvas.
        """
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

    def canvasReleaseEvent(self, event):
        """
            Captures the release events held on the canvas.
            ...
            Parameters
            ----------
            event : ReleaseEvent
                Holds the information associated to the release event over the canvas.
        """
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

    def activate(self):
        """
            Code to execute when the tool is activated.
        """
        self.setCursor(Qt.CrossCursor)
        self.reset()

    def deactivate(self):
        """
            Code to execute when the tool is deactivated.
        """
        pass

    def getCoordinatesBuffer(self):
        """
            Returns a list with the coordinates of a closed polygon generated
            with the coordinated gathered by the tool if the resulting polygon
            is valid.
        """
        self.rubberBand.closePoints(True)
        # polygon = Polygon(self.polygonCoordinates)
        # if polygon.is_valid:
        if isValid(self.polygonCoordinates):
            print('Poligon validity check manually: ', True)
            self.label.setText('{} vertex sel.'.format(len(self.polygonCoordinates)))
            self.polygonCoordinates.append(self.polygonCoordinates[0])
            return self.polygonCoordinates
        else:
            print('Poligon validity check manually: ', False)
            self.label.setText('Shape not valid')
            return None
        
    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True

    def getCanvasScopeCoord(self):
        canvScope = self.canvas.extent()
        canvScopeCoord = list()

        xmax = canvScope.xMaximum()
        ymax = canvScope.yMaximum()
        xmin = canvScope.xMinimum()
        ymin = canvScope.yMinimum()

        canvScopeCoord.append([xmin,ymin])
        canvScopeCoord.append([xmax,ymin])
        canvScopeCoord.append([xmax,ymax])
        canvScopeCoord.append([xmin,ymax])
        canvScopeCoord.append([xmin,ymin])

        return canvScopeCoord
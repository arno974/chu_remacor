#! python3 

import os
from pathlib import Path

from qgis.core import ( 
    QgsProject,
    QgsPrintLayout,
    QgsRectangle,
    QgsReadWriteContext,
    QgsLayoutExporter,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsStyle,
    QgsClassificationEqualInterval,   
    QgsGraduatedSymbolRenderer,
)

from qgis.gui import QgisInterface

from qgis.PyQt.QtXml import QDomDocument

class MapTools:
    def __init__(self, iface: QgisInterface, layerGroupName):
        """Class initialization."""
        self.iface = iface
        self.layerTreeRoot = QgsProject.instance().layerTreeRoot()
        self.layerGroupName = layerGroupName
        self.removeGroup()
        self.createLayerGroup()
        return

    def removeGroup(self):
        """
            Remove existing group (if exist) in order to create a new one
        """
        if self.layerTreeRoot.findGroup(self.layerGroupName) :
            self.layerTreeRoot.removeChildNode(self.layerTreeRoot.findGroup(self.layerGroupName))

    def createLayerGroup(self):
        """
            Create specific group to store results
        """        
        if self.layerTreeRoot.findGroup(self.layerGroupName) is None:        
            self.layerTreeRoot.insertGroup(0, self.layerGroupName)

    def addLayerToMap(self, layer, layerName, field):
        layer.setName(u'{1} ({0})'.format(layerName, field))
        QgsProject.instance().addMapLayer(layer, False)         
        self.moveLayerInsideGroup(layer)
        self.zoomMapToLayer(layer)

    def moveLayerInsideGroup(self, layer):
        """
            Move newly created layer inside the group created
        """    
        group = self.layerTreeRoot.findGroup(self.layerGroupName) 
        group.addLayer(layer)

    def zoomMapToLayer(self, layer):
        canvasCRS = QgsCoordinateReferenceSystem(layer.crs())
        layerCRS = QgsCoordinateReferenceSystem(QgsProject.instance().crs())
        transform = QgsCoordinateTransform(canvasCRS, layerCRS, QgsProject.instance())
        extent = QgsRectangle(layer.extent())       
        projectedExtent = transform.transformBoundingBox(extent)
        canvas = self.iface.mapCanvas()        
        canvas.setExtent(projectedExtent) 

    def setPointClusterStyle(self, layer):

        plugin_dir = str(Path(__file__).resolve().parent.parent)
        style_file = os.path.join(
            plugin_dir, 
            'ressources', 'styles', 'cluster_style.qml'
        )
        layer.loadNamedStyle(style_file)   

        layer.triggerRepaint()    
        return

    def setLayerPrevalenceStyle(self, layer):
        """
            New style based on prevalence field
        """ 
        #https://gis.stackexchange.com/questions/342352/apply-a-color-ramp-to-vector-layer-using-pyqgis3
        num_classes = 5
        ramp_name = 'Spectral'
        default_style = QgsStyle().defaultStyle()        

        classification_method = QgsClassificationEqualInterval()
        classification_method.setLabelFormat("%1 - %2")
        classification_method.setLabelPrecision(2)
        classification_method.setLabelTrimTrailingZeroes(True)

        renderer = QgsGraduatedSymbolRenderer()
        renderer.setClassAttribute('prevalence')
        renderer.setClassificationMethod(classification_method)

        color_ramp = default_style.colorRamp(ramp_name)
        color_ramp.invert()
        renderer.updateClasses(layer, num_classes)
        renderer.updateColorRamp(color_ramp)
        layer.setRenderer(renderer)
        layer.triggerRepaint()

    def setLayersStyle(self, prevalenceLayer, clusterLayer):
        self.setLayerPrevalenceStyle(prevalenceLayer)
        self.setPointClusterStyle(clusterLayer)    

    def createFinalMap(self, finalMapPath, mapTitle, mapFormat):
        """
            Create PDF/PNG map based on existing QPT
        """
        project = QgsProject.instance()  
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
          
        document = QDomDocument()
        
        plugin_dir = str(Path(__file__).resolve().parent.parent)
        template_file = open(
            os.path.join(
                plugin_dir, 
                'ressources', 'print', 'chu_impression.qpt'
            )
        )
            
        template_content = template_file.read()
        template_file.close()
        document.setContent(template_content)

        layout.loadFromTemplate(document, QgsReadWriteContext(), False)

        title_item = layout.itemById('title')
        title_item.setText(mapTitle)      

        exporter = QgsLayoutExporter(layout)
        if mapFormat == 'PDF':
            exporter.exportToPdf(u'{0}/prevalence.pdf'.format(finalMapPath), QgsLayoutExporter.PdfExportSettings())
        else :
            exporter.exportToImage(u'{0}/prevalence.jpg'.format(finalMapPath), QgsLayoutExporter.ImageExportSettings())
        return
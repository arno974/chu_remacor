#! python3 

from qgis.core import (
    Qgis,
    QgsProject,
    QgsMessageLog,
    QgsProcessing
) 

from qgis import processing

class AnalyseCasSimple:
    def __init__(self, layerCas, layerRepartition, FieldRepartition):

        self.layerCas = layerCas
        self.layerRepartition = layerRepartition
        self.FieldRepartition = FieldRepartition

        self.layerTreeRoot = QgsProject.instance().layerTreeRoot()
        self.layerGroupName = "Analyse cas simple"

        self.removeGroup()
        self.createLayerGroup() 
        
        self.countPointInPolygon()
        self.calculPrevalenceField()
            
        self.createFinalMap()  
        
    def countPointInPolygon(self):
        """
            First Algo Step - Counts all points feature inside the specified polygon layer
        """
        try:
            params = {
                "POINTS": self.layerCas,
                "POLYGONS": self.layerRepartition,                
                'OUTPUT':'memory:',
            }
            result = processing.run(
                "native:countpointsinpolygon",
                params,
                feedback = None
            )
            result_layer = result['OUTPUT']
            result_layer.setName('Nb Points')
            QgsProject.instance().addMapLayer(result_layer, False)
            self.moveLayerInsideGroup(result_layer)
            QgsMessageLog.logMessage("Traitement countpointsinpolygon effectué", 'CHU Remacor', level=Qgis.Info)           
        except Exception:
            QgsMessageLog.logMessage("Erreur pendant le traitement countpointsinpolygon", 'CHU Remacor', level=Qgis.Info)
            QgsMessageLog.logMessage(Exception, 'CHU Remacor', level=Qgis.Info)
        
    def calculPrevalenceField(self):
        pass

    def createFinalMap(self):
        pass

    def moveLayerInsideGroup(self, layer):    
        """
            Move newly created layer inside the group created
        """    
        group = self.layerTreeRoot.findGroup(self.layerGroupName) 
        group.addLayer(layer)

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


    


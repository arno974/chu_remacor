#! python3 

from qgis.core import (
    Qgis,
    QgsMessageLog,
    QgsVectorLayer,
    QgsField,
    QgsProject
)

from qgis.gui import QgisInterface

from qgis import processing

from .map_tools import MapTools

class ComputePrevalence:

    def __init__(self, iface: QgisInterface, layerCas: QgsVectorLayer, layerRepartition: QgsVectorLayer, FieldRepartition: QgsField, 
                    addFilter, fieldFilter, compareFilter, valueFilter,
                    finalMap, mapPath, mapTitle, mapCluster, mapFormat):
        # sub-modules
        self.mapTools = MapTools(iface, 'Analyse Prevalence')

        self.layerCas = layerCas
        self.layerRepartition = layerRepartition
        self.FieldRepartition = FieldRepartition

        self.result_layer = None
        self.fieldNbPoints = 'nb_points'

        if addFilter:
            self.filterDataSet(self.layerCas, fieldFilter, compareFilter, valueFilter)
            self.mapTools.addLayerToMap(self.layerCas, u"{0}{1}'{2}'".format(fieldFilter, compareFilter, valueFilter),'Cas filtrés')
        else:
            self.layerCas = self.layerCas.clone()
            self.mapTools.addLayerToMap(self.layerCas, "non filtré",'Cas')

        self.countPointInPolygon()
        self.computePrevalenceField()

        self.mapTools.setLayersStyle(self.result_layer, self.layerCas)

        self.mapTools.addLayerToMap(
            self.result_layer,
            'Prevalence',
            self.FieldRepartition
        )    

        if not mapCluster:
            iface.layerTreeView().setLayerVisible(self.layerCas, False)

        if finalMap :
            self.mapTools.createFinalMap(mapPath, mapTitle, mapFormat)  

        
    def countPointInPolygon(self):
        """
            First Algo Step - Counts all points feature inside the specified polygon layer
        """
        try:
            params = {
                "POINTS": self.layerCas,
                "POLYGONS": self.layerRepartition,    
                "FIELD": self.fieldNbPoints,            
                'OUTPUT':'memory:',
            }
            result = processing.run(
                "native:countpointsinpolygon",
                params,
                feedback = None
            )
            self.result_layer = result['OUTPUT']
            self.result_layer.setName('Nb Points')          
            QgsMessageLog.logMessage("Traitement countpointsinpolygon effectué", 'CHU Remacor', level=Qgis.Info)    
        except Exception:
            QgsMessageLog.logMessage("***** Erreur pendant le traitement countpointsinpolygon *****", 'CHU Remacor', level=Qgis.Warning)
            QgsMessageLog.logMessage(Exception, 'CHU Remacor', level=Qgis.Warning)
        
    def computePrevalenceField(self):
        """
            Second Algo Step - Compute prevalence Field
        """
        try:
            fPrevalence = u'({0}/{1})*100'.format(self.fieldNbPoints, self.FieldRepartition)
            params = {
                'INPUT': self.result_layer,
                'FIELD_NAME':'prevalence',
                'FIELD_TYPE':0, #float
                'FIELD_LENGTH':10,
                'FIELD_PRECISION':2,
                'NEW_FIELD':True,
                'FORMULA':fPrevalence,
                'OUTPUT':'memory:'
            }
            #https://docs.qgis.org/3.22/en/docs/user_manual/processing_algs/qgis/vectortable.html?highlight=fieldcalculator#id22
            result = processing.run(
                "native:fieldcalculator", 
                params,
                feedback=None
            )
            self.result_layer = result['OUTPUT']
            QgsMessageLog.logMessage("Traitement fieldcalculator effectué", 'CHU Remacor', level=Qgis.Info)
        except Exception:
            QgsMessageLog.logMessage("***** Erreur pendant le traitement fieldcalculator *****", 'CHU Remacor', level=Qgis.Warning)
            QgsMessageLog.logMessage(Exception, 'CHU Remacor', level=Qgis.sWarning)

    def filterDataSet(self, layerCas, fieldFilter, compareFilter, valueFilter):
        """
            Filter dataset and add the filter result to the map
        """
        try:
            match compareFilter:
                case "=":
                    compareFilter = 0
                case ">":
                    compareFilter = 2
                case "<":
                    compareFilter = 4

            params = {
                'INPUT': layerCas, 
                'FIELD': '{0}'.format(fieldFilter), 
                'OPERATOR': compareFilter, 
                'VALUE': '{0}'.format(valueFilter), 
                'OUTPUT':'memory:'
            }
            result =processing.run('native:extractbyattribute',
                params,
                feedback=None
            )
            self.layerCas = result['OUTPUT']        
        except Exception:
            QgsMessageLog.logMessage("***** Erreur pendant le traitement extractbyattribute *****", 'CHU Remacor', level=Qgis.Warning)
            QgsMessageLog.logMessage(Exception, 'CHU Remacor', level=Qgis.sWarning)


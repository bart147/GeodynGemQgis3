"""
Model exported as python.
Name : GWSW Geodyn - stap 1
Group : Geodyn cheat
With QGIS : 32208
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterMapLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class GwswGeodynStap1(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMapLayer('GWSWBemalingsgebieden', 'GWSW_Bemalingsgebieden', defaultValue=None, types=[QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterMapLayer('GWSWnetwerkknooppunt', 'GWSW_netwerk_knooppunt', defaultValue=None, types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterMapLayer('GWSWnetwerkkunstwerk', 'GWSW_netwerk_kunstwerk', defaultValue=None, types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterNumber('MaxzoekafstandRG', 'Max_zoek_afstand_RG', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=100, defaultValue=3))
        self.addParameter(QgsProcessingParameterNumber('knoopverlorenberging', 'knoopverlorenberging', type=QgsProcessingParameterNumber.Integer, minValue=0, maxValue=100, defaultValue=5))
        self.addParameter(QgsProcessingParameterNumber('leidingverlorenberging', 'leidingverlorenberging', type=QgsProcessingParameterNumber.Integer, minValue=0, maxValue=100, defaultValue=5))
        self.addParameter(QgsProcessingParameterMapLayer('netwerkverbinding', 'GWSW_netwerk_verbinding', defaultValue=None, types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterNumber('nooduitlaat', 'nooduitlaat', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=10, defaultValue=0.6))
        self.addParameter(QgsProcessingParameterFeatureSink('BemalingsgebiedenTbvStap2Bem_id', 'BEMALINGSGEBIEDEN TBV STAP 2 - BEM_ID', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('GebiedsgegevensStap1AllAtt', 'Gebiedsgegevens - stap1 - all att', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('GemengdeEnVuilwaterstelsels', 'Gemengde en vuilwaterstelsels', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Gebiedsgegevens_lijn', 'Gebiedsgegevens_lijn', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Gebiedsgegevens_puntStap1', 'Gebiedsgegevens_punt - STAP 1', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(84, model_feedback)
        results = {}
        outputs = {}

        # Drop field(s) knooppunt
        alg_params = {
            'COLUMN': ['wkt_geom','AantalWoningen','Aantal_ieBedrijven','Aantal_ieRecreatie','AfvoerendOppervlak','LateraalDebietDWA','LateraalDebietHWA','LateraalAfvoerendOppervlak'],
            'INPUT': parameters['GWSWnetwerkknooppunt'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsKnooppunt'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Extract doorlaat
        alg_params = {
            'FIELD': 'type',
            'INPUT': parameters['GWSWnetwerkkunstwerk'],
            'OPERATOR': 0,  # =
            'VALUE': 'Doorlaatniveau',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractDoorlaat'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Extract by expression - pompen die nergens naartoe pompen
        alg_params = {
            'EXPRESSION': '"type" = \'Pomp\' AND "eind" IS NULL',
            'INPUT': parameters['GWSWnetwerkkunstwerk'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionPompenDieNergensNaartoePompen'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Extract Overstortdrempel
        alg_params = {
            'FIELD': 'type',
            'INPUT': parameters['GWSWnetwerkkunstwerk'],
            'OPERATOR': 0,  # =
            'VALUE': 'Overstortdrempel',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractOverstortdrempel'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Fix geometries BEMALINGSGEBIEDEN
        alg_params = {
            'INPUT': parameters['GWSWBemalingsgebieden'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometriesBemalingsgebieden'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Drop field(s) verbinding
        alg_params = {
            'COLUMN': ['wkt_geom','AantalWoningen','Aantal_ieBedrijven','Aantal_ieRecreatie','AfvoerendOppervlak','LateraalDebietDWA','LateraalDebietHWA','LateraalAfvoerendOppervlak'],
            'INPUT': parameters['netwerkverbinding'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsVerbinding'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Extract overstorten
        alg_params = {
            'EXPRESSION': '"Drempelniveau" IS NOT NULL',
            'INPUT': parameters['GWSWnetwerkkunstwerk'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractOverstorten'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Extract pompen
        alg_params = {
            'FIELD': 'type',
            'INPUT': parameters['GWSWnetwerkkunstwerk'],
            'OPERATOR': 0,  # =
            'VALUE': 'Pomp',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractPompen'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Field calculator BEM_ID
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'BEM_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekenreeks
            'FORMULA': "'BEM' || lpad( $id ,3,0)",
            'INPUT': outputs['FixGeometriesBemalingsgebieden']['OUTPUT'],
            'OUTPUT': parameters['BemalingsgebiedenTbvStap2Bem_id']
        }
        outputs['FieldCalculatorBem_id'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['BemalingsgebiedenTbvStap2Bem_id'] = outputs['FieldCalculatorBem_id']['OUTPUT']

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Delete duplicates by attribute - dubbele pompen
        alg_params = {
            'FIELDS': ['begin'],
            'INPUT': outputs['ExtractPompen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DeleteDuplicatesByAttributeDubbelePompen'] = processing.run('native:removeduplicatesbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Afvoerrelaties (hub lines) - originele afvoerrelaties
        alg_params = {
            'ANTIMERIDIAN_SPLIT': False,
            'GEODESIC': False,
            'GEODESIC_DISTANCE': 1000,
            'HUBS': outputs['DeleteDuplicatesByAttributeDubbelePompen']['OUTPUT'],
            'HUB_FIELD': 'eind',
            'HUB_FIELDS': [''],
            'SPOKES': outputs['DropFieldsKnooppunt']['OUTPUT'],
            'SPOKE_FIELD': 'naam',
            'SPOKE_FIELDS': [''],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AfvoerrelatiesHubLinesOrigineleAfvoerrelaties'] = processing.run('native:hublines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Field calculator NUMMER
        alg_params = {
            'FIELD_LENGTH': 8,
            'FIELD_NAME': 'NUMMER',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer
            'FORMULA': ' $id',
            'INPUT': outputs['AfvoerrelatiesHubLinesOrigineleAfvoerrelaties']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorNummer'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Extract verbinding DWA/GEM stelselberging
        alg_params = {
            'EXPRESSION': '"type" LIKE \'%erg%\' OR\r\n"type" LIKE \'%emengd%\' OR\r\n"type" LIKE \'%uilwate%\' OR \r\n"type" LIKE \'%ransportrioolleidin%\'',
            'INPUT': outputs['DropFieldsVerbinding']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractVerbindingDwagemStelselberging'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Extract specific vertices eindpunt afvoerrelaties
        alg_params = {
            'INPUT': outputs['AfvoerrelatiesHubLinesOrigineleAfvoerrelaties']['OUTPUT'],
            'VERTICES': '-1',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractSpecificVerticesEindpuntAfvoerrelaties'] = processing.run('native:extractspecificvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Fix geometries verbinding DWA/GEM stelselberging - gemengde en vuilwaterstelsels voor stelselberging
        alg_params = {
            'INPUT': outputs['ExtractVerbindingDwagemStelselberging']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometriesVerbindingDwagemStelselbergingGemengdeEnVuilwaterstelselsVoorStelselberging'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Extract beginknopen afvoerrelaties
        alg_params = {
            'INPUT': outputs['AfvoerrelatiesHubLinesOrigineleAfvoerrelaties']['OUTPUT'],
            'VERTICES': '0',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractBeginknopenAfvoerrelaties'] = processing.run('native:extractspecificvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Field calculator VAN_KNOOPN
        alg_params = {
            'FIELD_LENGTH': 16,
            'FIELD_NAME': 'VAN_KNOOPN',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekenreeks
            'FORMULA': '"begin"',
            'INPUT': outputs['FieldCalculatorNummer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVan_knoopn'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Extract specific vertices - beginknoop
        alg_params = {
            'INPUT': outputs['ExtractVerbindingDwagemStelselberging']['OUTPUT'],
            'VERTICES': '0',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractSpecificVerticesBeginknoop'] = processing.run('native:extractspecificvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Extract specific vertices - eindknoop
        alg_params = {
            'INPUT': outputs['ExtractVerbindingDwagemStelselberging']['OUTPUT'],
            'VERTICES': '-1',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractSpecificVerticesEindknoop'] = processing.run('native:extractspecificvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Join BEM_ID aan leidingen
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'INPUT': outputs['FixGeometriesVerbindingDwagemStelselbergingGemengdeEnVuilwaterstelselsVoorStelselberging']['OUTPUT'],
            'JOIN': outputs['FieldCalculatorBem_id']['OUTPUT'],
            'JOIN_FIELDS': ['BEM_ID'],
            'METHOD': 0,  # Afzonderlijk object maken voor elk overeenkomend object (één-tot-veel)
            'PREDICATE': [5],  # within
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinBem_idAanLeidingen'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Drop field(s) eindknopen
        alg_params = {
            'COLUMN': ['wkt_geom','beginpunt','LengteLeiding','BobBeginpuntLeiding','vertex_pos','vertex_index','vertex_part','vertex_part_index','distance','angle',''],
            'INPUT': outputs['ExtractSpecificVerticesEindknoop']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsEindknopen'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Join - begin aan knooppunt
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'naam',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'beginpunt',
            'INPUT': outputs['DropFieldsKnooppunt']['OUTPUT'],
            'INPUT_2': outputs['ExtractSpecificVerticesBeginknoop']['OUTPUT'],
            'METHOD': 0,  # Afzonderlijk object maken voor elk overeenkomend object (één-tot-veel)
            'PREFIX': 'US_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinBeginAanKnooppunt'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Field calculator NAAR_KNOOP
        alg_params = {
            'FIELD_LENGTH': 16,
            'FIELD_NAME': 'NAAR_KNOOP',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekenreeks
            'FORMULA': '"eind"',
            'INPUT': outputs['FieldCalculatorVan_knoopn']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorNaar_knoop'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Field calculator TTOTAAL_M3
        alg_params = {
            'FIELD_LENGTH': 11,
            'FIELD_NAME': 'TTOTAAL_M3',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"Pompcapaciteit"',
            'INPUT': outputs['FieldCalculatorNaar_knoop']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorTtotaal_m3'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Merge vector layers
        alg_params = {
            'CRS': None,
            'LAYERS': [outputs['ExtractByExpressionPompenDieNergensNaartoePompen']['OUTPUT'],outputs['ExtractBeginknopenAfvoerrelaties']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Buffer
        alg_params = {
            'DISSOLVE': True,
            'DISTANCE': 0.2,
            'END_CAP_STYLE': 0,  # Rond
            'INPUT': outputs['JoinBem_idAanLeidingen']['OUTPUT'],
            'JOIN_STYLE': 0,  # Rond
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Drop field(s) beginknopen
        alg_params = {
            'COLUMN': ['wkt_geom','eindpunt','LengteLeiding','BobEindpuntLeiding','vertex_pos','vertex_index','vertex_part','vertex_part_index','distance','angle',''],
            'INPUT': outputs['ExtractSpecificVerticesBeginknoop']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsBeginknopen'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Drop field(s) overbodige info
        alg_params = {
            'COLUMN': ['geo_id','Stelsel','naam','type','beginpunt','eindpunt','MateriaalLeiding','VormLeiding','BreedteLeiding','HoogteLeiding','LengteLeiding','BobBeginpuntLeiding','BobEindpuntLeiding','BEM_ID',''],
            'INPUT': outputs['Buffer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsOverbodigeInfo'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # Join - eind aan knooppunt
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'naam',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'eindpunt',
            'INPUT': outputs['JoinBeginAanKnooppunt']['OUTPUT'],
            'INPUT_2': outputs['DropFieldsEindknopen']['OUTPUT'],
            'METHOD': 0,  # Afzonderlijk object maken voor elk overeenkomend object (één-tot-veel)
            'PREFIX': 'DS_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinEindAanKnooppunt'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Drop field(s) gebiedsgegevens lijn
        alg_params = {
            'COLUMN': ['geo_id','Stelsel','naam','type','begin','eind','BreedteOpening','HoogteOpening','VormOpening','Doorlaatniveau','Contractiecoef','MaxCapDoorlaat','Pompcapaciteit','AanslagniveauBeneden','AfslagniveauBeneden','AanslagniveauBoven','AfslagniveauBoven','Drempelbreedte','Drempelniveau','Buitenwaterstand','Stromingsrichting','geo_id_2','Stelsel_2','naam_2','type_2','Maaiveldhoogte','Maaiveldschematisering','MateriaalPut','VormPut','BreedtePut','LengtePut','HoogtePut',''],
            'INPUT': outputs['FieldCalculatorTtotaal_m3']['OUTPUT'],
            'OUTPUT': parameters['Gebiedsgegevens_lijn']
        }
        outputs['DropFieldsGebiedsgegevensLijn'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Gebiedsgegevens_lijn'] = outputs['DropFieldsGebiedsgegevensLijn']['OUTPUT']

        feedback.setCurrentStep(30)
        if feedback.isCanceled():
            return {}

        # Drop field(s) layer en path
        alg_params = {
            'COLUMN': ['layer','path'],
            'INPUT': outputs['MergeVectorLayers']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsLayerEnPath'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(31)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts rioolstelsels
        alg_params = {
            'INPUT': outputs['DropFieldsOverbodigeInfo']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSinglepartsRioolstelsels'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(32)
        if feedback.isCanceled():
            return {}

        # Drop field(s) niet relevant
        alg_params = {
            'COLUMN': ['US_vertex_index','US_vertex_part','US_vertex_part_index','US_distance','US_angle','US_vertex_pos','DS_vertex_index','DS_vertex_part','DS_vertex_part_index','DS_distance','DS_angle','DS_vertex_pos','US_eindpunt','US_BobEindpuntLeiding',''],
            'INPUT': outputs['JoinEindAanKnooppunt']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsNietRelevant'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(33)
        if feedback.isCanceled():
            return {}

        # Extract knopen aan DWA of GEM - BOB maten aan knopen plakken
        alg_params = {
            'EXPRESSION': '"US_naam" IS NOT NULL OR "DS_naam" IS NOT NULL',
            'INPUT': outputs['DropFieldsNietRelevant']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractKnopenAanDwaOfGemBobMatenAanKnopenPlakken'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(34)
        if feedback.isCanceled():
            return {}

        # Join attributes by location - within - BEM aan leidingen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['MultipartToSinglepartsRioolstelsels']['OUTPUT'],
            'JOIN': outputs['FieldCalculatorBem_id']['OUTPUT'],
            'JOIN_FIELDS': ['BEM_ID'],
            'METHOD': 2,  # Alleen attributen gebruiken van object met grootste overlapping (één-tot-één)
            'PREDICATE': [0],  # kruist met
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationWithinBemAanLeidingen'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(35)
        if feedback.isCanceled():
            return {}

        # Join attributes by location - BEM aan BEGINKNOPEN AFVOERRELATIES
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['DropFieldsLayerEnPath']['OUTPUT'],
            'JOIN': outputs['FieldCalculatorBem_id']['OUTPUT'],
            'JOIN_FIELDS': ['BEM_ID'],
            'METHOD': 1,  # Alleen attributen gebruiken van eerste overeenkomende object (één-tot-één)
            'PREDICATE': [0],  # kruist met
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationBemAanBeginknopenAfvoerrelaties'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(36)
        if feedback.isCanceled():
            return {}

        # Field calculator BEM_ID-singlepart
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'BEM_ID_SP',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekenreeks
            'FORMULA': '"BEM_ID" || \'-\' || lpad( $id+1 ,3,0)',
            'INPUT': outputs['JoinAttributesByLocationWithinBemAanLeidingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBem_idsinglepart'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(37)
        if feedback.isCanceled():
            return {}

        # Create spatial index BEM_ID_SP
        alg_params = {
            'INPUT': outputs['FieldCalculatorBem_idsinglepart']['OUTPUT']
        }
        outputs['CreateSpatialIndexBem_id_sp'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(38)
        if feedback.isCanceled():
            return {}

        # Join overstorten (summary) - overstortdata plakken
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['FieldCalculatorBem_idsinglepart']['OUTPUT'],
            'JOIN': outputs['ExtractOverstorten']['OUTPUT'],
            'JOIN_FIELDS': ['Drempelniveau'],
            'PREDICATE': [0],  # kruist met
            'SUMMARIES': [2,3,4,6,7],  # min,max,bereik,mean,median
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinOverstortenSummaryOverstortdataPlakken'] = processing.run('qgis:joinbylocationsummary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(39)
        if feedback.isCanceled():
            return {}

        # Join stats knopen maaiveld (summary)
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['FieldCalculatorBem_idsinglepart']['OUTPUT'],
            'JOIN': parameters['GWSWnetwerkknooppunt'],
            'JOIN_FIELDS': ['Maaiveldhoogte'],
            'PREDICATE': [0],  # kruist met
            'SUMMARIES': [0,2,3,6,7,11,12,4],  # aantal,min,max,mean,median,q1,q3,bereik
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinStatsKnopenMaaiveldSummary'] = processing.run('qgis:joinbylocationsummary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(40)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest BEM_ID_SP aan leidingen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['BEM_ID_SP'],
            'INPUT': outputs['JoinBem_idAanLeidingen']['OUTPUT'],
            'INPUT_2': outputs['CreateSpatialIndexBem_id_sp']['OUTPUT'],
            'MAX_DISTANCE': 0.2,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': parameters['GemengdeEnVuilwaterstelsels']
        }
        outputs['JoinAttributesByNearestBem_id_spAanLeidingen'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['GemengdeEnVuilwaterstelsels'] = outputs['JoinAttributesByNearestBem_id_spAanLeidingen']['OUTPUT']

        feedback.setCurrentStep(41)
        if feedback.isCanceled():
            return {}

        # Join stats leidingen diameters (summary)
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['FieldCalculatorBem_idsinglepart']['OUTPUT'],
            'JOIN': outputs['FixGeometriesVerbindingDwagemStelselbergingGemengdeEnVuilwaterstelselsVoorStelselberging']['OUTPUT'],
            'JOIN_FIELDS': ['HoogteLeiding'],
            'PREDICATE': [0],  # kruist met
            'SUMMARIES': [0,1,2,3,4,6,7],  # aantal,uniek,min,max,bereik,mean,median
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinStatsLeidingenDiametersSummary'] = processing.run('qgis:joinbylocationsummary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(42)
        if feedback.isCanceled():
            return {}

        # Join Doorlaat dichtsbijzijnde rioolstelsel
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['BEM_ID_SP'],
            'INPUT': outputs['ExtractDoorlaat']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorBem_idsinglepart']['OUTPUT'],
            'MAX_DISTANCE': 2,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinDoorlaatDichtsbijzijndeRioolstelsel'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(43)
        if feedback.isCanceled():
            return {}

        # Join Overstort dichtsbijzijnde rioolstelsel
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['BEM_ID_SP'],
            'INPUT': outputs['ExtractOverstortdrempel']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorBem_idsinglepart']['OUTPUT'],
            'MAX_DISTANCE': 2,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinOverstortDichtsbijzijndeRioolstelsel'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(44)
        if feedback.isCanceled():
            return {}

        # Join Pomp dichtsbijzijnde rioolstelsel
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['BEM_ID_SP'],
            'INPUT': outputs['DeleteDuplicatesByAttributeDubbelePompen']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorBem_idsinglepart']['OUTPUT'],
            'MAX_DISTANCE': 10,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinPompDichtsbijzijndeRioolstelsel'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(45)
        if feedback.isCanceled():
            return {}

        # Join attributes by location - within - BEM aan knopen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['ExtractKnopenAanDwaOfGemBobMatenAanKnopenPlakken']['OUTPUT'],
            'JOIN': outputs['FieldCalculatorBem_idsinglepart']['OUTPUT'],
            'JOIN_FIELDS': ['BEM_ID','BEM_ID_SP'],
            'METHOD': 1,  # Alleen attributen gebruiken van eerste overeenkomende object (één-tot-één)
            'PREDICATE': [5],  # within
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationWithinBemAanKnopen'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(46)
        if feedback.isCanceled():
            return {}

        # aantal overstorten per gebied
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID_SP'],
            'INPUT': outputs['JoinOverstortDichtsbijzijndeRioolstelsel']['OUTPUT'],
            'VALUES_FIELD_NAME': 'naam',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AantalOverstortenPerGebied'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(47)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest BEGINKNOOP met BEM_ID_SP
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['BEM_ID_SP'],
            'INPUT': outputs['JoinAttributesByLocationBemAanBeginknopenAfvoerrelaties']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorBem_idsinglepart']['OUTPUT'],
            'MAX_DISTANCE': parameters['MaxzoekafstandRG'],
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearestBeginknoopMetBem_id_sp'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(48)
        if feedback.isCanceled():
            return {}

        # aantal doorlaten per gebied
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID_SP'],
            'INPUT': outputs['JoinDoorlaatDichtsbijzijndeRioolstelsel']['OUTPUT'],
            'VALUES_FIELD_NAME': 'naam',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AantalDoorlatenPerGebied'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(49)
        if feedback.isCanceled():
            return {}

        # Join mv_q1 aan leidingen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID_SP',
            'FIELDS_TO_COPY': ['Maaiveldhoogte_q1'],
            'FIELD_2': 'BEM_ID_SP',
            'INPUT': outputs['JoinAttributesByNearestBem_id_spAanLeidingen']['OUTPUT'],
            'INPUT_2': outputs['JoinStatsKnopenMaaiveldSummary']['OUTPUT'],
            'METHOD': 1,  # Alleen attributen gebruiken van eerste overeenkomende object (één-tot-één)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinMv_q1AanLeidingen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(50)
        if feedback.isCanceled():
            return {}

        # aantal pompen per gebied
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID_SP'],
            'INPUT': outputs['JoinPompDichtsbijzijndeRioolstelsel']['OUTPUT'],
            'VALUES_FIELD_NAME': 'naam',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AantalPompenPerGebied'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(51)
        if feedback.isCanceled():
            return {}

        # Join overstorthoogte kunstwerken aan leidingen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID_SP',
            'FIELDS_TO_COPY': ['Drempelniveau_min'],
            'FIELD_2': 'BEM_ID_SP',
            'INPUT': outputs['JoinMv_q1AanLeidingen']['OUTPUT'],
            'INPUT_2': outputs['JoinOverstortenSummaryOverstortdataPlakken']['OUTPUT'],
            'METHOD': 1,  # Alleen attributen gebruiken van eerste overeenkomende object (één-tot-één)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinOverstorthoogteKunstwerkenAanLeidingen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(52)
        if feedback.isCanceled():
            return {}

        # Count bij NULL op 1 zetten
        alg_params = {
            'FIELD_LENGTH': 8,
            'FIELD_NAME': 'POMPEN_ST',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer
            'FORMULA': 'if("BEM_ID_SP" IS NULL, 1, "count")',
            'INPUT': outputs['AantalPompenPerGebied']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CountBijNullOp1Zetten'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(53)
        if feedback.isCanceled():
            return {}

        # Field calculator LEIDINGEN max niveau berging
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'OVH_D',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'round("Maaiveldhoogte_q1" - @nooduitlaat ,2)',
            'INPUT': outputs['JoinOverstorthoogteKunstwerkenAanLeidingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorLeidingenMaxNiveauBerging'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(54)
        if feedback.isCanceled():
            return {}

        # Join mv_q1 aan knopen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID_SP',
            'FIELDS_TO_COPY': ['Maaiveldhoogte_q1'],
            'FIELD_2': 'BEM_ID_SP',
            'INPUT': outputs['JoinAttributesByLocationWithinBemAanKnopen']['OUTPUT'],
            'INPUT_2': outputs['JoinStatsKnopenMaaiveldSummary']['OUTPUT'],
            'METHOD': 1,  # Alleen attributen gebruiken van eerste overeenkomende object (één-tot-één)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinMv_q1AanKnopen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(55)
        if feedback.isCanceled():
            return {}

        # Drop field(s) gebeidskenmerken - GEBIEDSKENMERKEN KNOPEN
        alg_params = {
            'COLUMN': ['BreedteOpening','HoogteOpening','VormOpening','Contractiecoef','MaxCapDoorlaat','Buitenwaterstand','Stromingsrichting','geo_id_2','Stelsel_2','naam_2','type_2','Maaiveldhoogte','Maaiveldschematisering','MateriaalPut','VormPut','BreedtePut','LengtePut','HoogtePut','vertex_pos','vertex_index','vertex_part','vertex_part_index','distance','angle','AanslagniveauBeneden','AfslagniveauBeneden','Doorlaatniveau','Drempelbreedte','Drempelniveau','n','feature_x','feature_y','nearest_x','nearest_y',''],
            'INPUT': outputs['JoinAttributesByNearestBeginknoopMetBem_id_sp']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsGebeidskenmerkenGebiedskenmerkenKnopen'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(56)
        if feedback.isCanceled():
            return {}

        # Doorlaten - count bij NULL op 0 zetten
        alg_params = {
            'FIELD_LENGTH': 8,
            'FIELD_NAME': 'DOORLAAT_S',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer
            'FORMULA': 'if("BEM_ID_SP" IS NULL, 0, "count")',
            'INPUT': outputs['AantalDoorlatenPerGebied']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DoorlatenCountBijNullOp0Zetten'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(57)
        if feedback.isCanceled():
            return {}

        # Join overstorthoogte aan gebiedskenmerken
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID_SP',
            'FIELDS_TO_COPY': ['Drempelniveau_min'],
            'FIELD_2': 'BEM_ID_SP',
            'INPUT': outputs['DropFieldsGebeidskenmerkenGebiedskenmerkenKnopen']['OUTPUT'],
            'INPUT_2': outputs['JoinOverstortenSummaryOverstortdataPlakken']['OUTPUT'],
            'METHOD': 1,  # Alleen attributen gebruiken van eerste overeenkomende object (één-tot-één)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinOverstorthoogteAanGebiedskenmerken'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(58)
        if feedback.isCanceled():
            return {}

        # Count overstortdrempel bij NULL op 0 zetten
        alg_params = {
            'FIELD_LENGTH': 8,
            'FIELD_NAME': 'OVERSTORT_',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer
            'FORMULA': 'if("BEM_ID_SP" IS NULL, 0, "count")',
            'INPUT': outputs['AantalOverstortenPerGebied']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CountOverstortdrempelBijNullOp0Zetten'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(59)
        if feedback.isCanceled():
            return {}

        # Berging in leidingen - Field calculator
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'B_M3_LEI',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'if(mean( "BobBeginpuntLeiding" , "BobEindpuntLeiding" ) +  ("HoogteLeiding"/1000) > if( "Drempelniveau_min" IS NOT NULL,  "Drempelniveau_min" , "OVH_D" ), 0,\r\nif("VormLeiding" LIKE \'%Ei%\' , round((((0.25 * pi()*((("BreedteLeiding"/1000)^2))/2))+(((("BreedteLeiding"/1000)+(("HoogteLeiding"-"BreedteLeiding")/1000))/2)*(("BreedteLeiding"/1000/2)+(("HoogteLeiding"-"BreedteLeiding")/1000/2)))+((0.25*pi()*(("HoogteLeiding"-"BreedteLeiding")/1000)^2/2))) *  "LengteLeiding" ,2),\r\nif("VormLeiding" = \'Rechthoekig\' , round( ("BreedteLeiding" /1000) * ("HoogteLeiding" /1000) *  "LengteLeiding" ,2),\r\nround( ("BreedteLeiding" /1000 /2) * ("BreedteLeiding" /1000 /2) * pi() *  "LengteLeiding" ,2 ))))',
            'INPUT': outputs['FieldCalculatorLeidingenMaxNiveauBerging']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BergingInLeidingenFieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(60)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - BERGING LEIDINGEN STAT BEM_ID_SP
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID_SP'],
            'INPUT': outputs['BergingInLeidingenFieldCalculator']['OUTPUT'],
            'VALUES_FIELD_NAME': 'B_M3_LEI',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesBergingLeidingenStatBem_id_sp'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(61)
        if feedback.isCanceled():
            return {}

        # Join overstorthoogte kunstwerken aan knopen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID_SP',
            'FIELDS_TO_COPY': ['Drempelniveau_min'],
            'FIELD_2': 'BEM_ID_SP',
            'INPUT': outputs['JoinMv_q1AanKnopen']['OUTPUT'],
            'INPUT_2': outputs['JoinOverstortenSummaryOverstortdataPlakken']['OUTPUT'],
            'METHOD': 1,  # Alleen attributen gebruiken van eerste overeenkomende object (één-tot-één)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinOverstorthoogteKunstwerkenAanKnopen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(62)
        if feedback.isCanceled():
            return {}

        # Field calculator default max niveau berging
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'OVH_D',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'round("Maaiveldhoogte_q1" - @nooduitlaat ,2)',
            'INPUT': outputs['JoinOverstorthoogteKunstwerkenAanKnopen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDefaultMaxNiveauBerging'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(63)
        if feedback.isCanceled():
            return {}

        # Join berging leidingen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID_SP',
            'FIELDS_TO_COPY': ['sum','count'],
            'FIELD_2': 'BEM_ID_SP',
            'INPUT': outputs['JoinOverstorthoogteAanGebiedskenmerken']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesBergingLeidingenStatBem_id_sp']['OUTPUT'],
            'METHOD': 1,  # Alleen attributen gebruiken van eerste overeenkomende object (één-tot-één)
            'PREFIX': 'LEI_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinBergingLeidingen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(64)
        if feedback.isCanceled():
            return {}

        # Berging knopen - Field calculator
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'B_M3_KNP',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'round(\r\nif( "VormPut" = \'Rond\',  (("BreedtePut" /1000) * ("BreedtePut" /1000) * pi()) * \r\n(if( "Drempelniveau_min" IS NULL,  abs("OVH_D" - min( "US_BobBeginpuntLeiding" , "DS_BobEindpuntLeiding" )),  abs("Drempelniveau_min" - min( "US_BobBeginpuntLeiding" , "DS_BobEindpuntLeiding" )))),\r\n("BreedtePut" /1000) * ("Lengteput" /1000) * if( "Drempelniveau_min" IS NULL,  abs("OVH_D" - min( "US_BobBeginpuntLeiding" , "DS_BobEindpuntLeiding" )),  abs("Drempelniveau_min" - min( "US_BobBeginpuntLeiding" , "DS_BobEindpuntLeiding" ))))\r\n, 2)',
            'INPUT': outputs['FieldCalculatorDefaultMaxNiveauBerging']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BergingKnopenFieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(65)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - BERGING KNOPEN STAT BEM_ID_SP
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID_SP'],
            'INPUT': outputs['BergingKnopenFieldCalculator']['OUTPUT'],
            'VALUES_FIELD_NAME': 'B_M3_KNP',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesBergingKnopenStatBem_id_sp'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(66)
        if feedback.isCanceled():
            return {}

        # Join berging knopen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID_SP',
            'FIELDS_TO_COPY': ['sum','count'],
            'FIELD_2': 'BEM_ID_SP',
            'INPUT': outputs['JoinBergingLeidingen']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesBergingKnopenStatBem_id_sp']['OUTPUT'],
            'METHOD': 1,  # Alleen attributen gebruiken van eerste overeenkomende object (één-tot-één)
            'PREFIX': 'KNP_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinBergingKnopen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(67)
        if feedback.isCanceled():
            return {}

        # Field calculator total storage
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'BERGING_M3',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"LEI_sum" + "KNP_sum"',
            'INPUT': outputs['JoinBergingKnopen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorTotalStorage'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(68)
        if feedback.isCanceled():
            return {}

        # Join pomp count per BEM_ID_SP
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID_SP',
            'FIELDS_TO_COPY': ['POMPEN_ST'],
            'FIELD_2': 'BEM_ID_SP',
            'INPUT': outputs['FieldCalculatorTotalStorage']['OUTPUT'],
            'INPUT_2': outputs['CountBijNullOp1Zetten']['OUTPUT'],
            'METHOD': 1,  # Alleen attributen gebruiken van eerste overeenkomende object (één-tot-één)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinPompCountPerBem_id_sp'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(69)
        if feedback.isCanceled():
            return {}

        # Join overstort count per BEM_ID_SP
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID_SP',
            'FIELDS_TO_COPY': ['OVERSTORT_'],
            'FIELD_2': 'BEM_ID_SP',
            'INPUT': outputs['JoinPompCountPerBem_id_sp']['OUTPUT'],
            'INPUT_2': outputs['CountOverstortdrempelBijNullOp0Zetten']['OUTPUT'],
            'METHOD': 1,  # Alleen attributen gebruiken van eerste overeenkomende object (één-tot-één)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinOverstortCountPerBem_id_sp'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(70)
        if feedback.isCanceled():
            return {}

        # Join doorlaat count per BEM_ID_SP
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID_SP',
            'FIELDS_TO_COPY': ['DOORLAAT_S'],
            'FIELD_2': 'BEM_ID_SP',
            'INPUT': outputs['JoinOverstortCountPerBem_id_sp']['OUTPUT'],
            'INPUT_2': outputs['DoorlatenCountBijNullOp0Zetten']['OUTPUT'],
            'METHOD': 1,  # Alleen attributen gebruiken van eerste overeenkomende object (één-tot-één)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinDoorlaatCountPerBem_id_sp'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(71)
        if feedback.isCanceled():
            return {}

        # Join NUMMER afvoerrelatie
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'begin',
            'FIELDS_TO_COPY': ['NUMMER'],
            'FIELD_2': 'begin',
            'INPUT': outputs['JoinDoorlaatCountPerBem_id_sp']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorNummer']['OUTPUT'],
            'METHOD': 1,  # Alleen attributen gebruiken van eerste overeenkomende object (één-tot-één)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinNummerAfvoerrelatie'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(72)
        if feedback.isCanceled():
            return {}

        # Field calculator NAAM
        alg_params = {
            'FIELD_LENGTH': 32,
            'FIELD_NAME': 'NAAM',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekenreeks
            'FORMULA': '"naam"',
            'INPUT': outputs['JoinNummerAfvoerrelatie']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorNaam'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(73)
        if feedback.isCanceled():
            return {}

        # Field calculator VAN_KNOOPN
        alg_params = {
            'FIELD_LENGTH': 16,
            'FIELD_NAME': 'VAN_KNOOPN',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekenreeks
            'FORMULA': '"begin"',
            'INPUT': outputs['FieldCalculatorNaam']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVan_knoopn'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(74)
        if feedback.isCanceled():
            return {}

        # Field calculator NAAR_KNOOP
        alg_params = {
            'FIELD_LENGTH': 16,
            'FIELD_NAME': 'NAAR_KNOOP',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekenreeks
            'FORMULA': '"eind"',
            'INPUT': outputs['FieldCalculatorVan_knoopn']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorNaar_knoop'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(75)
        if feedback.isCanceled():
            return {}

        # Field calculator CAP_INST_M
        alg_params = {
            'FIELD_LENGTH': 11,
            'FIELD_NAME': 'CAP_INST_M',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"Pompcapaciteit"*3.6',
            'INPUT': outputs['FieldCalculatorNaar_knoop']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorCap_inst_m'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(76)
        if feedback.isCanceled():
            return {}

        # Field calculator LAAGSTE_OS
        alg_params = {
            'FIELD_LENGTH': 11,
            'FIELD_NAME': 'LAAGSTE_OS',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"Drempelniveau_min"',
            'INPUT': outputs['FieldCalculatorCap_inst_m']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorLaagste_os'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(77)
        if feedback.isCanceled():
            return {}

        # Field calculator STRENGEN_S
        alg_params = {
            'FIELD_LENGTH': 8,
            'FIELD_NAME': 'STRENGEN_S',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer
            'FORMULA': '"LEI_COUNT"',
            'INPUT': outputs['FieldCalculatorLaagste_os']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorStrengen_s'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(78)
        if feedback.isCanceled():
            return {}

        # Field calculator KNOPEN_ST
        alg_params = {
            'FIELD_LENGTH': 8,
            'FIELD_NAME': 'KNOPEN_ST',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer
            'FORMULA': '"KNP_count"',
            'INPUT': outputs['FieldCalculatorStrengen_s']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorKnopen_st'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(79)
        if feedback.isCanceled():
            return {}

        # Field calculator BERG_KNP_M
        alg_params = {
            'FIELD_LENGTH': 11,
            'FIELD_NAME': 'BERG_KNP_M',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"KNP_sum" - ("KNP_sum" * ( @knoopverlorenberging / 100))',
            'INPUT': outputs['FieldCalculatorKnopen_st']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBerg_knp_m'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(80)
        if feedback.isCanceled():
            return {}

        # Field calculator BERGV_KNP_
        alg_params = {
            'FIELD_LENGTH': 11,
            'FIELD_NAME': 'BERGV_KNP_',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"BERG_KNP_M" * ( @knoopverlorenberging / 100)',
            'INPUT': outputs['FieldCalculatorBerg_knp_m']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBergv_knp_'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(81)
        if feedback.isCanceled():
            return {}

        # Field calculator BERG_STR_M
        alg_params = {
            'FIELD_LENGTH': 11,
            'FIELD_NAME': 'BERG_STR_M',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'if("LEI_count" > 0, "LEI_sum" - ("LEI_sum" * ( @leidingverlorenberging / 100)), NULL)',
            'INPUT': outputs['FieldCalculatorBergv_knp_']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBerg_str_m'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(82)
        if feedback.isCanceled():
            return {}

        # Field calculator BERGV_STR_
        alg_params = {
            'FIELD_LENGTH': 11,
            'FIELD_NAME': 'BERGV_STR_',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"BERG_STR_M" * ( @leidingverlorenberging / 100)',
            'INPUT': outputs['FieldCalculatorBerg_str_m']['OUTPUT'],
            'OUTPUT': parameters['GebiedsgegevensStap1AllAtt']
        }
        outputs['FieldCalculatorBergv_str_'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['GebiedsgegevensStap1AllAtt'] = outputs['FieldCalculatorBergv_str_']['OUTPUT']

        feedback.setCurrentStep(83)
        if feedback.isCanceled():
            return {}

        # Drop field(s) niet geodyn-velden
        alg_params = {
            'COLUMN': ['geo_id','Stelsel','naam','type','begin','eind','Pompcapaciteit','AanslagniveauBoven','AfslagniveauBoven','BEM_ID','BEM_ID_SP','Drempelniveau_min','LEI_sum','LEI_count','KNP_sum','KNP_count',''],
            'INPUT': outputs['FieldCalculatorBergv_str_']['OUTPUT'],
            'OUTPUT': parameters['Gebiedsgegevens_puntStap1']
        }
        outputs['DropFieldsNietGeodynvelden'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Gebiedsgegevens_puntStap1'] = outputs['DropFieldsNietGeodynvelden']['OUTPUT']
        return results

    def name(self):
        return 'GWSW Geodyn - stap 1'

    def displayName(self):
        return 'GWSW Geodyn - stap 1'

    def group(self):
        return 'Geodyn cheat'

    def groupId(self):
        return 'Geodyn cheat'

    def createInstance(self):
        return GwswGeodynStap1()

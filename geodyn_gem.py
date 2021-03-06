# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeodynGem
                                 A QGIS plugin
 Geodyn voor gemeenten
                              -------------------
        begin                : 2018-03-09
        git sha              : $Format:%H$
        copyright            : (C) 2018 by BKGIS
        email                : b.kropf@bkgis.nl
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import absolute_import
from builtins import object
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QFileDialog
from qgis.PyQt.QtGui import QIcon
#from qgis.core import QgsMessageLog, QgsMapLayerRegistry, QgsVectorFileWriter, QgsVectorLayer
from qgis.core import QgsMessageLog, QgsVectorFileWriter, QgsVectorLayer, QgsProject, Qgis
# Initialize Qt resources from file resources.py
from . import resources
# Import the code for the dialog
from .geodyn_gem_dialog import GeodynGemDialog
import os.path
from .app import settings
from .app import m1_OvernemenGegevensGEM as m1
from .app import m2_BerekenResultaten as m2
from .app.utl import print_log, blokje_log, get_d_velden, get_d_velden_csv
from .app.settings import keyword_1, keyword_2, keyword_3, keyword_4, keyword_5, keyword_6, keyword_7, result_dir
# for backward compatibility with older QGIS versions (without QgsWKBTypes)
try:
    ##from qgis.core import QgsWKBTypes
    from qgis.core import QgsWkbTypes
    b_QgsWKBTypes = True
except ImportError:
    b_QgsWKBTypes = False
	
	
class GeodynGem(object):
    """QGIS Plugin Implementation."""
    def __init__(self, iface):
        """Constructor.
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GeodynGem_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Geodyn gemeente')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GeodynGem')
        self.toolbar.setObjectName(u'GeodynGem')
        # iface.messageBar().pushMessage("Error", "I'm sorry Dave, I'm afraid I can't do that",
        #                                level=QgsMessageBar.CRITICAL)
    # noinspection PyMethodMayBeStatic
	
    def tr(self, message):
        """Get the translation for a string using Qt translation API.
        We implement this ourselves since we do not inherit QObject.
        :param message: String for translation.
        :type message: str, QString
        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GeodynGem', message)
		
    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.
        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str
        :param text: Text that should be shown in menu items for this action.
        :type text: str
        :param callback: Function to be called when the action is triggered.
        :type callback: function
        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool
        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool
        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool
        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str
        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget
        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.
        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        # Create the dialog (after translation) and keep reference
        self.dlg = GeodynGemDialog()
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)
        self.actions.append(action)
        #self.dlg.lineEdit.clear()
        self.dlg.lineEdit.setText(result_dir)
        self.dlg.lineEdit.setToolTip("Om een vaste waarde in te stellen: ga naar local_settings.py in app directory van plugin.")
        self.dlg.pushButton.clicked.connect(self.select_output_folder)
        return action
		
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/GeodynGem/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'geografische afvalwater prognose tool voor gemeenten'),
            callback=self.run,
            parent=self.iface.mainWindow())
			
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Geodyn gemeente'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
		
    def move_to_front(self, l, txt):
        """searches for txt in layer.name() if match: move to front of list"""
        index = [l.index(i) for i in l if txt.lower() in i.name().lower()]
        if len(index) > 0:
            l.insert(0, l.pop(index[0]))
        if txt in [keyword_4, keyword_6]: # VE's en verhard opp zijn optioneel dus 'no data' toevoegen
            if len(index) == 0:
                l.insert(0, QgsVectorLayer(baseName="no data")) # geen keyword dus 'no data' als bovenste optie in keuzelijst
            else:
                l.append(QgsVectorLayer(baseName="no data")) # wel keyword dus 'no data' als laatste optie in keuzelijst
        return l
		
    def remove_result_layers(self, remove_all=False, delete_source=False):
        layers_to_remove = [layer for layer, flag in settings.l_result_layers_to_remove if remove_all or flag]
        ins = QgsProject.instance()
        ##ins = QgsMapLayerRegistry.instance()
        ##layers = ins.mapLayersByName()
        ##layers = QgsProject.instance().mapLayers().values() # For QGIS 3, QgsMapLayerRegistry's functionality has been moved to QgsProject: https://gis.stackexchange.com/questions/26257/iterating-over-map-layers-in-qgis-python/125003
        layers = QgsProject.instance().mapLayers().values()

        for layer in layers:
            source = layer.source()
            name = layer.name()
            if name in layers_to_remove:
                print_log("remove layer {}".format(name), "d")
                ins.removeMapLayer(layer.id())


            if name in layers_to_remove:
                #ins.removeMapLayer(layer.id())
                if delete_source:
                    print_log("remove layer.source {}".format(name), "d")
                    if '.shp' in source.lower():
                        result = QgsVectorFileWriter.deleteShapeFile(source)
                    elif '.gpkg' in source.lower():
                        try:
                            path = source.split("|")[0]
                            for path_ in [path, path+"-wal", path+"-shm"]:
                                if os.path.exists(path_):
                                    os.remove(path_)
                            result = True
                        except Exception as e:
                            print_log(e, "e", self.iface)
                            result = False
                    elif '.csv' in source.lower():
                        try:
                            os.remove(source)
                            result = True
                        except Exception as e:
                            print_log(e, "e", self.iface)
                            result = False
                    if not result:
                        print_log("Tool afgebroken! Kan resultaat ({}) niet verwijderen i.v.m. locking. Resultaten kunnen niet overschreven worden en dienen (handmatig) te worden verwijderd.".format(source), "e", self.iface)
                        return
						
    def select_output_folder(self):
        # filename = QFileDialog.getSaveFileName(self.dlg, "Select output folder ", "", '*.txt')
        # outputFolder = QFileDialog.getExistingDirectory(self.dlg, "Select Output Folder", QDir.currentPath())
        outputFolder = QFileDialog.getExistingDirectory(self.dlg, 'Select Output Folder')
        self.dlg.lineEdit.setText(outputFolder)
		
    def run(self):
        """Run method that performs all the real work"""
        self.remove_result_layers(remove_all=True, delete_source=True)
        layers = QgsProject.instance().mapLayers().values()
        if not layers:
            print_log("Tool afgebroken! Geen layers gevonden. Voeg eerst layers toe", "e", self.iface)
            return
        layer_points, layer_lines, layer_polygons = [], [], []
        if b_QgsWKBTypes:
            for i, layer in enumerate(layers):
                if hasattr(layer, "wkbType"):
                    # qgis.core.QgsWKBTypes.displayString(int(vl.wkbType()))
                    if "point" in QgsWkbTypes.displayString(int(layer.wkbType())).lower(): ## QGis.WKBPoint:
                        layer_points.append(layer)
                    elif "line" in QgsWkbTypes.displayString(int(layer.wkbType())).lower(): ##QGis.WKBLineString:
                        layer_lines.append(layer)
                    elif "polygon" in QgsWkbTypes.displayString(int(layer.wkbType())).lower(): ##QGis.WKBPolygon:
                        layer_polygons.append(layer)
                    else:
                        pass
            layer_1 = layer_points[:] # more on slicing: https://www.afternerd.com/blog/python-copy-list/
            layer_2 = layer_lines[:]
            layer_3 = layer_points[:]
            layer_4 = layer_points[:]
            layer_5 = layer_polygons[:]
            layer_6 = layer_polygons[:]
            layer_7 = layer_polygons[:]
        else:
            print_log("ImportError for QgsWKBTypes. Kan geen geometrie herkennen voor layer inputs. \
                        Controleer of juiste layers zijn geselecteerd of upgrade QGIS.",
                "w", self.iface)
            layer_points = layer_lines = layer_polygons = layers
            layer_1 = list(layers)[:]
            layer_2 = list(layers)[:]
            layer_3 = list(layers)[:]
            layer_4 = list(layers)[:]
            layer_5 = list(layers)[:]
            layer_6 = list(layers)[:]
            layer_7 = list(layers)[:]
        layer_1 = self.move_to_front(layer_1, keyword_1)
        layer_2 = self.move_to_front(layer_2, keyword_2)
        layer_3 = self.move_to_front(layer_3, keyword_3)
        layer_4 = self.move_to_front(layer_4, keyword_4)
        layer_5 = self.move_to_front(layer_5, keyword_5)
        layer_6 = self.move_to_front(layer_6, keyword_6)
        layer_7 = self.move_to_front(layer_7, keyword_7)
        self.dlg.comboBox_1.clear()
        self.dlg.comboBox_2.clear()
        self.dlg.comboBox_3.clear()
        self.dlg.comboBox_4.clear()
        self.dlg.comboBox_5.clear()
        self.dlg.comboBox_6.clear()
        self.dlg.comboBox_7.clear()
        self.dlg.comboBox_1.addItems([i.name() for i in layer_1])  # knooppunt
        self.dlg.comboBox_2.addItems([i.name() for i in layer_2])  # afvoerrelatie
        self.dlg.comboBox_3.addItems([i.name() for i in layer_3])  # drinkwater BAG
        self.dlg.comboBox_4.addItems([i.name() for i in layer_4])  # VE's
        self.dlg.comboBox_5.addItems([i.name() for i in layer_5])  # plancap
        self.dlg.comboBox_6.addItems([i.name() for i in layer_6])  # verhard opp
        self.dlg.comboBox_7.addItems([i.name() for i in layer_7])  # bemalingsgebieden
        msg_tooltip = "Kaartlagen met '{}' in naam komen bovenaan de keuzelijst te staan.\
            \nVoor het instellen van een eigen zoekterm: ga naar local_settings.py in de app directory van de plugin."
        self.dlg.comboBox_1.setToolTip(msg_tooltip.format(keyword_1))
        self.dlg.comboBox_2.setToolTip(msg_tooltip.format(keyword_2))
        self.dlg.comboBox_3.setToolTip(msg_tooltip.format(keyword_3))
        self.dlg.comboBox_4.setToolTip(msg_tooltip.format(keyword_4))
        self.dlg.comboBox_5.setToolTip(msg_tooltip.format(keyword_5))
        self.dlg.comboBox_6.setToolTip(msg_tooltip.format(keyword_6))
        self.dlg.comboBox_7.setToolTip(msg_tooltip.format(keyword_7))
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            ##QgsMessageLog.logMessage("sel_index = {}".format(sel_index, level=QgsMessageLog.INFO))
            ##QgsMessageLog.logMessage("layer_index 4 = {}".format(self.move_to_front(layer_points, "VE")[self.dlg.comboBox_4.currentIndex()].name()), level=QgsMessageLog.INFO)
            ##QgsMessageLog.logMessage("layer4 = {}".format([i.name() for i in l4]), level=QgsMessageLog.INFO)
            sel_layers = [
                layer_1[self.dlg.comboBox_1.currentIndex()],
                layer_2[self.dlg.comboBox_2.currentIndex()],
                layer_3[self.dlg.comboBox_3.currentIndex()],
                layer_4[self.dlg.comboBox_4.currentIndex()],
                layer_5[self.dlg.comboBox_5.currentIndex()],
                layer_6[self.dlg.comboBox_6.currentIndex()],
                layer_7[self.dlg.comboBox_7.currentIndex()],
            ]
            for i, layer in enumerate(sel_layers):
                print_log("input {}:\t{}".format(i+1, layer.name()), "i")
            gdb = self.dlg.lineEdit.text() #
            if not gdb or not os.path.exists(gdb):
                print_log("Script afgebroken! Geen geldige output map opgegeven ({}...)".format(gdb), "e", self.iface)
                return
            qgis_warnings_log = settings.qgis_warnings_log
            with open(qgis_warnings_log, 'w') as logfile:
                import time
                logfile.write('{level}: date {time}'.format(level="INFO", time=time.asctime()))
            blokje_log("Veld-info ophalen...", "i")
            INP_FIELDS_XLS = settings.INP_FIELDS_XLS
            INP_FIELDS_CSV = settings.INP_FIELDS_CSV
            try:
                if settings.b_raise_xlrd_import_error:
                    print_log("b_raise_xlrd_import_error = True (zie local_settings.py)", "w", self.iface)
                    raise ImportError # for testing csv
                from xlrd import open_workbook
                d_velden = get_d_velden(INP_FIELDS_XLS, 0, open_workbook)
            except ImportError:     # for compatibility with iMac
                print_log("import error 'xlrd': inp_fields.csv wordt gebruikt als input in plaats van inp_fields.xls",
                          "w", self.iface)
                d_velden = get_d_velden_csv(INP_FIELDS_CSV)
            for fld in d_velden:
                print_log("{}\n{}".format(fld, d_velden[fld]), "d")
            # check for required fields
            vl = sel_layers[0] # knooppunt
            if vl.fields().indexFromName('VAN_KNOOPN') == -1:
                print_log("Script afgebroken! Verplicht veld 'VAN_KNOOPN' niet gevonden in kaartlaag '{}'".format(vl.name()), "e", self.iface)
                return
            vl = sel_layers[1]  # afvoerrelatie
            if vl.fields().indexFromName('VAN_KNOOPN') == -1:
                print_log("Script afgebroken! Verplicht veld 'VAN_KNOOPN' niet gevonden in kaartlaag '{}'".format(vl.name()), "e", self.iface)

            # run module 1
            l_K_ONTV_VAN, inp_polygon_layer = m1.main(self.iface, sel_layers, gdb, d_velden)

            # run module 2
            # temp for testing module 2
            ##l_K_ONTV_VAN =  [{'RGM009': "'RGM005'", '30.6': '', 'RGM005': '', '10.1': '', 'RGM008': '', '400233': "'10.1', 'RGM004', '47.1', 'RGM002', 'RGM001', 'RGM003'", 'RGM004': "'RGM002', 'RGM001', 'RGM003'", 'RGM002': "'RGM001', 'RGM003'", 'RGM003': '', 'RGM001': "'RGM003'", '26.1': '', '18.6': '', '50.1': '', '21.2': '', '38.2': '', '14.1': '', '46.1': '', 'RG-ZV-BE': "'18.6', '21.2'", '14.2': '', '4550': "'4502', '4636', '1611', '4242', '5143', '5246', '4474', '7076'", '4502': '', '4636': '', '1611': '', '4242': '', '5143': '', '5246': '', '4312': '', '47.1': '', '4743': '', 'boostrEDAM': "'0372', '0510', '0339', '0016', 'RGM013', '4306', '4307', '4315', '38.2', '37.1'", '4474': "'7076'", '7076': '', '4306': '', '4307': '', '0372': "'4306', '4307', '4315'", '4315': '', '0510': '', '0339': '', '0016': '', '37.1': '', 'RGM013': "'38.2', '37.1'", 'RGM021N': '', 'RG-ZVRKD': "'30.6', '26.1', '50.1'", 'RWZIkatw': "'4550', '4743', 'boostrEDAM', '4502', '4636', '1611', '4242', '5143', '5246', '4474', '0372', '0510', '0339', '0016', 'RGM013', '7076', '4306', '4307', '4315', '38.2', '37.1'", 'RWZIoosth': "'RGM009', 'RGM008', '400233', '14.1', '46.1', 'RG-ZV-BE', '14.2', 'RGM021N', '10.1', 'RGM004', '47.1', '18.6', '21.2', 'RGM005', 'RGM002', 'RGM001', 'RGM003'"}, {'RGM009': "'RGM005'", '30.6': '', 'RGM005': '', '10.1': '', 'RGM008': '', '400233': "'10.1', 'RGM004', '47.1'", 'RGM004': "'RGM002'", 'RGM002': "'RGM001'", 'RGM003': '', 'RGM001': "'RGM003'", '26.1': '', '18.6': '', '50.1': '', '21.2': '', '38.2': '', '14.1': '', '46.1': '', 'RG-ZV-BE': "'18.6', '21.2'", '14.2': '', '4550': "'4502', '4636', '1611', '4242', '5143', '5246', '4474'", '4502': '', '4636': '', '1611': '', '4242': '', '5143': '', '5246': '', '4312': '', '47.1': '', '4743': '', 'boostrEDAM': "'0372', '0510', '0339', '0016', 'RGM013'", '4474': "'7076'", '7076': '', '4306': '', '4307': '', '0372': "'4306', '4307', '4315'", '4315': '', '0510': '', '0339': '', '0016': '', '37.1': '', 'RGM013': "'38.2', '37.1'", 'RGM021N': '', 'RG-ZVRKD': "'30.6', '26.1', '50.1'", 'RWZIkatw': "'4550', '4743', 'boostrEDAM'", 'RWZIoosth': "'RGM009', 'RGM008', '400233', '14.1', '46.1', 'RG-ZV-BE', '14.2', 'RGM021N'"}]
            ##INP_POLYGON_COPY = r'G:\GISDATA\QGIS\geodyn_gem_qgis3\data\tmp\inp_polygon_copy.shp'
            ##inp_polygon_layer = QgsVectorLayer(INP_POLYGON_COPY, "inp_polygon_layer", "ogr")

            m2.main(self.iface, sel_layers, gdb, d_velden, l_K_ONTV_VAN, inp_polygon_layer)
            if settings.b_remove_results_after_run:
                self.remove_result_layers(remove_all=False, delete_source=False)
            ##self.iface.mainWindow().statusBar().showMessage("dit is de mainWindow")
            warnings = []
            with open(qgis_warnings_log, 'r') as log_file:
                for line in log_file.readlines():
                    if "WARNING" in line:
                        warnings.append(line)
            msg = QMessageBox()
            if len(warnings) > 0:
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Script completed")
                msg.setText("{} warnings were encountered when running script".format(len(warnings)))
                msg.setInformativeText("For more information see details below or view log panel")
                detailedText = "The details are as follows:"
                detailedText += "\n" + "".join(warnings)
                detailedText += "\nlogfile: {}".format(settings.logFile)
                msg.setDetailedText(detailedText)
                msg.setStyleSheet("QLabel{min-width: 300px;}")
            else:
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Script completed")
                msg.setText("No problems were encountered when running script!")
            retval = msg.exec_()
            ##QMessageBox.information(msg, "Info", "Script completed!")
            QgsMessageLog.logMessage("Script completed!", level=Qgis.Info)
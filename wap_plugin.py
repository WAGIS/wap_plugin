# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WAPlugin
                                 A QGIS plugin
 Provides access to all the WaPOR data and includes it in the QGIS canvas as another raster layer, providing WaPOR data easy access to the QGIS users. Moreover, the water accounting and productivity component of the plugin will help the water management, providing the opportunity of calculating water accounting indicators, through the creation of maps and reports.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-12-01
        git sha              : $Format:%H$
        copyright            : (C) 2020 by WAP Team
        email                : waplugin.qgis@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QDate, QTime, QDateTime, Qt
from qgis.PyQt.QtGui import QIcon 
from qgis.PyQt.QtWidgets import QAction, QApplication, QMessageBox

from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from qgis.core import QgsRasterLayer

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .wap_plugin_dialog import WAPluginDialog
import os.path
import os  

try:
    from .utils.managers import WaporAPIManager, FileManager, CanvasManager
    from .utils.indicators import IndicatorCalculator, INDICATORS_INFO
    from .utils.tools import CoordinatesSelectorTool

except ModuleNotFoundError as e:
    print('Module [{}] required and not found please install it'.format(e.name))
    QMessageBox.information(None, "Module import error", '''<html><head/><body>
    <p>Module [<b>{}</b>] required and not found please install it. You can find
     some instructions on how to do it with <b>OSGeo4W Shell</b> on our <a href=
     "https://github.com/WAGIS/wap_plugin"><span style=" text-decoration: 
     underline; color: #0000ff;">GitHub Repository</span></a>.
    <br>
    <br>
    Closing the plugin with System Exit . . .</p></body></html>'''.format(e.name))
    quit()


class WAPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
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
            'WAPlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&WAPlugin')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        # Path of the code Directory
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        self.layer_folder_dir = os.path.join(self.cwd, "layers")

        ## Default Values
        # self.waterProductivityVar = "GBWP"
        # self.resolutionVar = "100m"  #"250m" or "100m" , maybe "30m" works for some area
        # self.startSeasonVar = "2015-01"  # "YYYY-DK" (Dekad)
        # self.endSeasonVar = "2015-18"  # "YYYY-DK" (Dekad)
        # self.indicator_index = 0
        # self.indicator = "Equity"

        # # Locations
        # self.locListContinental = ["Algeria","Angola","Benin","Botswana","Burkina Faso","Burundi","Cameroon","Canary Islands"
        #     ,"Cape Verde","Central African Republic","Ceuta","Chad","Comoros","Côte d'Ivoire"
        #     ,"Democratic Republic of the Congo","Djibouti","Egypt","Equatorial Guinea","Eritrea","Ethiopia"
        #     ,"Gabon","Gambia","Ghana","Guinea","Guinea-Bissau","Kenya","Lesotho","Liberia","Libya"
        #     ,"Madagascar","Madeira","Malawi","Mali","Mauritania","Mauritius","Mayotte","Melilla"
        #     ,"Morocco"  ,"Mozambique","Namibia","Niger","Nigeria"  ,"Republic of the Congo"
        #     ,"Réunion","Rwanda","Saint Helena","São Tomé and Príncipe","Senegal","Seychelles"
        #     ,"Sierra Leone","Somalia","South Africa","Sudan","Swaziland","Tanzania","Togo","Tunisia"
        #     ,"Uganda","Western Sahara","Zambia","Zimbabwe"]

        # self.locListNational = ["Benin","Burundi","Egypt","Ghana","Iraq","Jordan","Kenya","Lebanon","Mali","Morocco"
        #     ,"Mozambique","Niger","Palestine","Rwanda","South Sudan","Sudan","Syrian Arab Republic"
        #     ,"Tunisia","Uganda","Yemen"]

        # self.locListSubNational = ["Awash, Ethiopia", "Bekaa, Lebanon", "Busia, Kenya", "Gezira, Sudan", "Koga, Ethiopia",
        #         "Lamego, Mozambique", "Office du Niger, Mali", "Zankalon, Egypt"] 

        self.rasters_path = "layers"

        self.api_manag = WaporAPIManager()
        self.file_manag = FileManager(self.plugin_dir, self.rasters_path)
        self.canv_manag = CanvasManager(self.iface, self.plugin_dir, self.rasters_path)
        
        self.indic_calc = IndicatorCalculator(self.plugin_dir, self.rasters_path)

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
        return QCoreApplication.translate('WAPlugin', message)

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

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/wap_plugin/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Water Accounting and Productivity Plugin'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&WAPlugin'),
                action)
            self.iface.removeToolBarIcon(action)

    def signin(self):
        """
            Calls the sign in function of the API manager and updates the UI
            in response to the result.
        """
        self.dlg.signinStateLabel.setText('Signing into your WaPOR profile . . .')
        connected = self.api_manag.signin(self.dlg.apiTokenTextBox.text())

        if connected:
            self.dlg.signinStateLabel.setText('API Token confirmed, access granted!!!')
            self.dlg.saveTokenButton.setEnabled(True)
            self.dlg.signinButton.setEnabled(False)

            self.dlg.progressBar.setValue(0)
            self.dlg.downloadButton.setEnabled(True)
            self.dlg.progressLabel.setText ('Connected to WaPOR database')
        else:
            self.dlg.signinStateLabel.setText('Access denied, please check the API Token provided or the internet connection . . .')
            self.dlg.progressLabel.setText ('Fail to connect to Wapor Database . . .')

    def saveToken(self):
        """
            Calls the save token function of the file manager and updates the UI.
        """
        self.file_manag.save_token(self.dlg.apiTokenTextBox.text())
        self.dlg.signinStateLabel.setText('Token file saved in memory . . .')

    def loadToken(self):
        """
            Calls the load token function of the file manager, connects the 
            plugin with the WaPOR database and updates the UI in response to the 
            result.
        """
        APIToken = self.file_manag.load_token()

        if APIToken is not None:
            self.dlg.signinStateLabel.setText('Loading Token from memory and signing into your WaPOR profile . . .')
            connected = self.api_manag.signin(APIToken)

            if connected:
                self.dlg.signinStateLabel.setText('API Token confirmed, access granted!!!')
                self.dlg.signinButton.setEnabled(False)
                self.dlg.loadTokenButton.setEnabled(False)

                self.dlg.progressBar.setValue(0)
                self.dlg.downloadButton.setEnabled(True)
                self.dlg.progressLabel.setText ('Connected to WaPOR database')
            else:
                self.dlg.signinStateLabel.setText('Access denied, please check the API Token file or the internet connection . . .')
                self.dlg.progressLabel.setText ('Fail to connect to Wapor Database . . .')
        else:
            self.dlg.signinStateLabel.setText('No token file found in memory . . .')

    def listWorkspaces(self):
        """
            Calls the pull workspaces function of the API manager and updates 
            the UI in response to the result.
        """
        self.dlg.workspaceComboBox.clear()
        workspaces = self.api_manag.pull_workspaces()
        self.dlg.workspaceComboBox.addItems(workspaces.values())

        index = self.dlg.workspaceComboBox.findText('WAPOR_2', QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.dlg.workspaceComboBox.setCurrentIndex(index)

    def listRasterMemory(self):
        """
            Calls the list rasters function of the file manager and updates 
            the UI in response to the result.
        """
        rasterFolder = self.dlg.rasterFolderExplorer.filePath()
        self.tif_files = self.file_manag.list_rasters(rasterFolder)
        self.dlg.rasterMemoryComboBox.clear()
        self.dlg.rasterMemoryComboBox.addItems(self.tif_files.keys())
    
    def listRasterCalcMemory(self):
        """
            Calls the list rasters function of the file manager to get the rasters
            for the indicator calculator.
        """
        rasterFolderCalc = self.dlg.rasterFolderCalcExplorer.filePath()
        self.tif_calc_files = self.file_manag.list_rasters(rasterFolderCalc)


    def workspaceChange(self):
        """
            Detects changes on the workspace selection, calls the pull cubes
            function of the API manager, filters the result leaving out the 
            clipped cubes and updates the UI in response to the result.
        """
        QApplication.processEvents()
        self.workspace = self.dlg.workspaceComboBox.currentText()
        self.cubes, timeOptions, countryOptions, levelOptions = self.api_manag.pull_cubes(self.workspace)

        levelOptions.insert(0,'None')
        timeOptions.insert(0,'None')
        countryOptions.insert(0,'None')

        self.dlg.levelFilterComboBox.clear()
        self.dlg.levelFilterComboBox.addItems(levelOptions)
        self.dlg.timeFilterComboBox.clear()
        self.dlg.countryFilterComboBox.clear()
        self.dlg.timeFilterComboBox.addItems(timeOptions)
        self.dlg.countryFilterComboBox.addItems(countryOptions)

    def updateCubesFiltered(self):
        levelFilterValue = self.dlg.levelFilterComboBox.currentText()
        timeFilterValue = self.dlg.timeFilterComboBox.currentText()
        countryFilterValue = self.dlg.countryFilterComboBox.currentText()
        if not self.first_start and \
           not levelFilterValue  == '' and \
           not timeFilterValue == '' and \
           not countryFilterValue == '':
            if self.dlg.workspaceComboBox.currentText() == 'WAPOR_2':
                if timeFilterValue == 'None' and \
                countryFilterValue == 'None' and \
                levelFilterValue == 'None':
                    filters = ['-', 'clipped', ')'] #Can I remove clipped???
                    mode = 'neg'
                else:
                    filters = {'level':levelFilterValue,
                            'time':timeFilterValue,
                            'country':countryFilterValue}
                    mode = 'pos'
                filteredCubes = self.api_manag.filter_cubes(self.cubes, filters, mode)
                if not filteredCubes:
                    filteredCubes =['---']
            else:
                filteredCubes = self.cubes

            self.dlg.cubeComboBox.clear()
            self.dlg.cubeComboBox.addItems(filteredCubes)

    def indicatorChange(self):
        """
            Detects changes on the indicator selection and updates the UI in 
            response to the result.
        """
        self.indicator_key = self.dlg.indicatorListComboBox.currentText()
        self.dlg.indicInfoLabel.setWordWrap(True)
        
        """ Update Indicator Info """
        raster_info = [INDICATORS_INFO[self.indicator_key]['info'] + '\n']
        raster_info.extend(['==' * 20 + '\n'])
        raster_info.extend([raster + ': ' + INDICATORS_INFO[self.indicator_key]['rasters'][raster] + '\n'
                    for raster in INDICATORS_INFO[self.indicator_key]['rasters']])
        raster_info.extend(['--' * 20 + '\n'])
        raster_info.extend([factor + ': ' + INDICATORS_INFO[self.indicator_key]['factors'][factor] + '\n'
                            for factor in INDICATORS_INFO[self.indicator_key]['factors']])
        
        """ Raster Files Filtered Update """
        self.listRasterCalcMemory()

        """ Parameters Update """
        if INDICATORS_INFO[self.indicator_key]['params']['PARAM_1'] == '':
            self.dlg.Param1Label.setText('Not Required')
            self.dlg.Param1ComboBox.setEnabled(False)
        else:
            self.dlg.Param1Label.setText(INDICATORS_INFO[self.indicator_key]['params']['PARAM_1']['label'])
            filteredRasterFiles = self.file_manag.filterRasterFiles(self.tif_calc_files, INDICATORS_INFO[self.indicator_key]['params']['PARAM_1']['type'])
            self.dlg.Param1ComboBox.clear()
            self.dlg.Param1ComboBox.addItems(filteredRasterFiles.keys())
            self.dlg.Param1ComboBox.setEnabled(True)

        if INDICATORS_INFO[self.indicator_key]['params']['PARAM_2'] == '':
            self.dlg.Param2Label.setText('Not Required')
            self.dlg.Param2ComboBox.setEnabled(False)
        else:
            self.dlg.Param2Label.setText(INDICATORS_INFO[self.indicator_key]['params']['PARAM_2']['label'])
            filteredRasterFiles = self.file_manag.filterRasterFiles(self.tif_calc_files, INDICATORS_INFO[self.indicator_key]['params']['PARAM_2']['type'])
            self.dlg.Param2ComboBox.clear()
            self.dlg.Param2ComboBox.addItems(filteredRasterFiles.keys())
            self.dlg.Param2ComboBox.setEnabled(True)

        if INDICATORS_INFO[self.indicator_key]['params']['PARAM_3'] == '':
            self.dlg.Param3Label.setText('Not Required')
            self.dlg.Param3TextBox.setEnabled(False)
        else:
            self.dlg.Param3Label.setText(INDICATORS_INFO[self.indicator_key]['params']['PARAM_3'])
            self.dlg.Param3TextBox.setEnabled(True)

        self.dlg.indicInfoLabel.setText(''.join(raster_info))

        if self.indicator_key == 'Equity':
            self.dlg.outputIndicName.setEnabled(False)
        else:
            self.dlg.outputIndicName.setEnabled(True)


    def cubeChange(self):
        """
            Detects changes on the cube selection, calls the pull dimensions and
            measures functions of the API manager and updates the UI in response
            to the result.
        """
        try:
            QApplication.processEvents()
            self.cube = self.cubes[self.dlg.cubeComboBox.currentText()]['id']
            self.dimensions = self.api_manag.pull_cube_dims(self.workspace,self.cube)
            self.measures = self.api_manag.pull_cube_meas(self.workspace,self.cube)

            self.dlg.measureComboBox.clear()
            self.dlg.measureComboBox.addItems(self.measures.keys())
            self.dlg.dimensionComboBox.clear()
            self.dlg.dimensionComboBox.addItems(self.dimensions.keys())
            if self.cube:
                self.dlg.outputRasterCubeID.setText('_'+self.cube+'.tif')
            else:
                self.dlg.outputRasterCubeID.setText('---')
                
        except (KeyError) as exception:
            pass

    def measureChange(self):
        """
            Detects changes on the measure selection and updates the UI in 
            response to the result.
        """
        try:
            self.measure = self.measures[self.dlg.measureComboBox.currentText()]
        except (KeyError) as exception:
            pass

    def memberChange(self):
        """
            Detects changes on the member selection and updates the UI in 
            response to the result.
        """
        try:
            self.member = self.members[self.dlg.memberComboBox.currentText()]
        except (KeyError) as exception:
            pass

    def dimensionChange(self):
        """
            Detects changes on the dimension selection, calls the pull members
            function of the API manager and updates the UI in response to the 
            result.
        """
        try:
            QApplication.processEvents()
            self.dimension = self.dimensions[self.dlg.dimensionComboBox.currentText()]
            self.members = self.api_manag.pull_cube_dim_membs(self.workspace,self.cube,self.dimension)

            self.dlg.memberComboBox.clear()
            self.dlg.memberComboBox.addItems(self.members.keys())
        except (KeyError) as exception:
                    pass
    
    def downloadCroppedRaster(self):
        """
            Construct the parameters needed to download a cropped raster, the URL
            and calls the query crop raster of the API manager and the download 
            raster function of the file manager, then updates the UI in response
            to the result.
        """
        self.dlg.progressBar.setValue(20)
        self.dlg.progressLabel.setText ('Downloading Raster')
        
        params = dict()
        params['outputFileName'] = self.dlg.outputRasterName.text()+'_'+self.cube+'.tif'
        params['cube_code'] = self.cube
        params['cube_workspaceCode'] = self.workspace
        params['measures'] = [self.measure]
        params['dimensions'] = [{
                                    "code": self.dimension,
                                    "values": [self.member]
                                }]
        if self.dlg.useCanvasCoordCheckBox.checkState():
            params['coordinates'] = [self.coord_select_tool.getCanvasScopeCoord()]
            self.queryCrs = self.getCrs()
        else:
            params['coordinates'] = [self.queryCoordinates]
        params['crs'] = self.queryCrs

        rast_url = self.api_manag.query_crop_raster(params)

        rast_directory = self.dlg.downloadFolderExplorer.filePath()
        self.file_manag.download_raster(rast_url, rast_directory)
        
        self.dlg.progressBar.setValue(100)
        self.dlg.progressLabel.setText ('Raster Download Complete')
        
        self.listRasterMemory()

    def updateRasterFolder(self):
        rasterFolder = self.dlg.rasterFolderExplorer.filePath()
        self.canv_manag.set_rasters_dir(rasterFolder)

        self.listRasterMemory()

        self.dlg.rasterFolderCalcExplorer.setFilePath(rasterFolder)


    def updateRasterFolderCalc(self):
        self.indicatorChange()

    def loadRaster(self):
        """
            Calls the add raster function of the canvas manager.
        """
        raster_name = self.dlg.rasterMemoryComboBox.currentText()
        self.canv_manag.add_rast(raster_name)

    def selectCoordinatesTool(self):
        """
            Changes the active tool of Qgis to the coordinates selection tool 
            and storages the previous tool.
        """
        self.dlg.getEdgesButton.setEnabled(False)
        self.dlg.resetToolButton.setEnabled(True)
        self.prev_tool = self.iface.mapCanvas().mapTool()
        self.coord_select_tool.activate()
        self.iface.mapCanvas().setMapTool(self.coord_select_tool)
    
    def savePolygon(self):
        """
            Closes the polygon generated by the coordinates selection tool, saves
            its coordinates in a local list, records the active CRS reference,
            restores the previous tool used in Qgis and  updates the UI in 
            response to the resulting polygon.
        """
        self.dlg.savePolygonButton.setEnabled(False)
        self.queryCoordinates = self.coord_select_tool.getCoordinatesBuffer()
        self.queryCrs = self.getCrs()
        print(self.queryCrs)
        self.coord_select_tool.deactivate()
        self.iface.mapCanvas().setMapTool(self.prev_tool)
        if self.queryCoordinates:
            self.dlg.TestCanvasLabel.setText ('The polygon selected has {} edges'.format(len(self.queryCoordinates)-1))
        else:
            self.dlg.TestCanvasLabel.setText ('Polygon not valid.')

    def resetTool(self):
        """ 
            Cleans the polygon and the CRS reference from the local memory and
            updates the UI.
        """
        self.coord_select_tool.reset()
        self.queryCoordinates = None
        self.queryCrs = None
        self.dlg.TestCanvasLabel.setText ('Coordinates cleared, using default ones . . .')
        self.dlg.getEdgesButton.setEnabled(True)
        self.dlg.resetToolButton.setEnabled(False)

    def useCanvasCoord(self):
        if self.dlg.useCanvasCoordCheckBox.checkState():
            self.dlg.getEdgesButton.setEnabled(False)
            self.dlg.savePolygonButton.setEnabled(False)
            self.dlg.resetToolButton.setEnabled(False)
        else:
            self.dlg.getEdgesButton.setEnabled(True)
            self.dlg.savePolygonButton.setEnabled(True)
            self.dlg.resetToolButton.setEnabled(True)

    def calculateIndicator(self):
        """ 
            Calculates the selected indicator.
        """
        print('Calculating . . . ')
        
        param1_name = self.dlg.Param1ComboBox.currentText()
        param2_name = self.dlg.Param2ComboBox.currentText()

            
        output_name = self.dlg.outputIndicName.text()+".tif"
        
        print(self.indicator_key)
        if self.indicator_key == 'Equity':
            self.indic_calc.equity(raster=param1_name)
        elif self.indicator_key == 'Beneficial Fraction':
            self.indic_calc.beneficial_fraction(param1_name, param2_name, output_name)
            self.canv_manag.add_rast(output_name)
        elif self.indicator_key == 'Adequacy':
            try:
                param3_name = float(self.dlg.Param3TextBox.text())
            except ValueError:
                print("Param 3 Input is not a float. Using Default value 1.25 instead")
                self.dlg.Param3TextBox.setText('1.25')
                param3_name = 1.25
                
            self.indic_calc.adequacy(param1_name, param2_name, output_name, Kc=param3_name)
            self.canv_manag.add_rast(output_name)
        elif self.indicator_key == 'Relative Water Deficit':
            self.indic_calc.relative_water_deficit(param1_name, output_name)
            self.canv_manag.add_rast(output_name)
        else:
            raise NotImplementedError("Indicator: '{}' not implemented yet.".format(self.indicator))
    
    def getCrs(self):
        """
            Returns the active CRS reference in Qgis.
        """
        return self.iface.mapCanvas().mapSettings().destinationCrs().authid()

    def run(self):
        """Run method that performs all the real work"""
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = WAPluginDialog()
            
            # self.dlg.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.dlg.setFixedSize(self.dlg.size())

            self.dlg.indicatorListComboBox.addItems(INDICATORS_INFO.keys())

            self.coord_select_tool = CoordinatesSelectorTool(self.iface.mapCanvas(),
                                                           self.dlg.TestCanvasLabel,
                                                           self.dlg.savePolygonButton)

            self.dlg.downloadButton.setEnabled(False)

            self.dlg.saveTokenButton.setEnabled(False)
            
            self.dlg.savePolygonButton.setEnabled(False)
            self.dlg.resetToolButton.setEnabled(False)

            self.dlg.useCanvasCoordCheckBox.clicked.connect(self.useCanvasCoord)

            self.dlg.signinButton.clicked.connect(self.signin)
            self.dlg.saveTokenButton.clicked.connect(self.saveToken)
            self.dlg.loadTokenButton.clicked.connect(self.loadToken)

            self.dlg.rasterFolderExplorer.setFilePath(self.layer_folder_dir)
            self.dlg.rasterFolderCalcExplorer.setFilePath(self.layer_folder_dir)
            self.dlg.downloadFolderExplorer.setFilePath(self.layer_folder_dir)
            self.dlg.downloadButton.clicked.connect(self.downloadCroppedRaster)
            self.dlg.loadRasterButton.clicked.connect(self.loadRaster)
            self.dlg.RasterRefreshButton.clicked.connect(self.listRasterMemory)

            self.dlg.rasterFolderExplorer.fileChanged.connect(self.updateRasterFolder)
            self.dlg.rasterFolderCalcExplorer.fileChanged.connect(self.updateRasterFolderCalc)

            self.dlg.workspaceComboBox.currentIndexChanged.connect(self.workspaceChange)
            self.dlg.cubeComboBox.currentIndexChanged.connect(self.cubeChange)
            self.dlg.dimensionComboBox.currentIndexChanged.connect(self.dimensionChange)
            self.dlg.memberComboBox.currentIndexChanged.connect(self.memberChange)
            self.dlg.measureComboBox.currentIndexChanged.connect(self.measureChange)

            self.dlg.levelFilterComboBox.currentIndexChanged.connect(self.updateCubesFiltered)
            self.dlg.timeFilterComboBox.currentIndexChanged.connect(self.updateCubesFiltered)
            self.dlg.countryFilterComboBox.currentIndexChanged.connect(self.updateCubesFiltered)

            self.dlg.indicatorListComboBox.currentIndexChanged.connect(self.indicatorChange)
            self.dlg.calculateButton.clicked.connect(self.calculateIndicator)

            self.dlg.getEdgesButton.clicked.connect(self.selectCoordinatesTool)
            self.dlg.savePolygonButton.clicked.connect(self.savePolygon)
            self.dlg.resetToolButton.clicked.connect(self.resetTool)

            self.listWorkspaces()
            self.indicatorChange()
            self.listRasterMemory()

            self.queryCoordinates = None
            self.queryCrs = None
            self.dlg.useCanvasCoordCheckBox.setChecked(True)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
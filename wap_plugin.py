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
        email                : waporteam17@gmail.com
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
from qgis.PyQt.QtWidgets import QAction, QApplication

from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from qgis.core import QgsRasterLayer

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .wap_plugin_dialog import WAPluginDialog
import os.path

from .managers import WaporAPIManager, FileManager, CanvasManager
from .indicators import IndicatorCalculator

# from PyQt5.QtGui import *
import requests
import json
import wget
import os  

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

        # Default Values
        self.waterProductivityVar = "GBWP"
        self.resolutionVar = "100m"  #"250m" or "100m" , maybe "30m" works for some area
        self.startSeasonVar = "2015-01"  # "YYYY-DK" (Dekad)
        self.endSeasonVar = "2015-18"  # "YYYY-DK" (Dekad)

        # Locations
        self.locListContinental = ["Algeria","Angola","Benin","Botswana","Burkina Faso","Burundi","Cameroon","Canary Islands"
            ,"Cape Verde","Central African Republic","Ceuta","Chad","Comoros","Côte d'Ivoire"
            ,"Democratic Republic of the Congo","Djibouti","Egypt","Equatorial Guinea","Eritrea","Ethiopia"
            ,"Gabon","Gambia","Ghana","Guinea","Guinea-Bissau","Kenya","Lesotho","Liberia","Libya"
            ,"Madagascar","Madeira","Malawi","Mali","Mauritania","Mauritius","Mayotte","Melilla"
            ,"Morocco"  ,"Mozambique","Namibia","Niger","Nigeria"  ,"Republic of the Congo"
            ,"Réunion","Rwanda","Saint Helena","São Tomé and Príncipe","Senegal","Seychelles"
            ,"Sierra Leone","Somalia","South Africa","Sudan","Swaziland","Tanzania","Togo","Tunisia"
            ,"Uganda","Western Sahara","Zambia","Zimbabwe"]

        self.locListNational = ["Benin","Burundi","Egypt","Ghana","Iraq","Jordan","Kenya","Lebanon","Mali","Morocco"
            ,"Mozambique","Niger","Palestine","Rwanda","South Sudan","Sudan","Syrian Arab Republic"
            ,"Tunisia","Uganda","Yemen"]

        self.locListSubNational = ["Awash, Ethiopia", "Bekaa, Lebanon", "Busia, Kenya", "Gezira, Sudan", "Koga, Ethiopia",
                "Lamego, Mozambique", "Office du Niger, Mali", "Zankalon, Egypt"] 

        # MODIFICATIONS AFTER OOP
        self.rasters_path = "layers"

        self.api_manag = WaporAPIManager()
        self.file_manag = FileManager(self.plugin_dir)
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

    def wapor_connect(self):
        connected = self.api_manag.connectWapor()    
        if connected:
            self.dlg.progressBar.setValue(20)
            self.dlg.progressLabel.setText ('Conncected to WaPOR database')
            self.dlg.downloadButton.setEnabled(True)
        else:
            self.dlg.progressLabel.setText ('Fail to connect to Wapor Database . . .')

    def listWorkspaces(self):
        self.dlg.workspaceComboBox.clear()
        workspaces = self.api_manag.pull_workspaces()
        self.dlg.workspaceComboBox.addItems(workspaces)

    def workspaceChange(self):
        workspace = self.dlg.workspaceComboBox.currentText()
        cubes = self.api_manag.pull_cubes(workspace)

        self.dlg.cubeComboBox.clear()
        self.dlg.cubeComboBox.addItems(cubes)

    def cubeChange(self):
        workspace = self.dlg.workspaceComboBox.currentText()
        cube = self.dlg.cubeComboBox.currentText()
        dimensions = self.api_manag.pull_cube_dims(workspace,cube)
        measures = self.api_manag.pull_cube_meas(workspace,cube)

        self.dlg.measureComboBox.clear()
        self.dlg.measureComboBox.addItems(measures)
        self.dlg.dimensionComboBox.clear()
        self.dlg.dimensionComboBox.addItems(dimensions)

    def dimensionChange(self):
        workspace = self.dlg.workspaceComboBox.currentText()
        cube = self.dlg.cubeComboBox.currentText()
        dimension = self.dlg.dimensionComboBox.currentText()
        members = self.api_manag.pull_cube_dim_membs(workspace,cube,dimension)

        self.dlg.dimensionMemberComboBox.clear()
        self.dlg.dimensionMemberComboBox.addItems(members)

    def waterProductivityChange(self, i):
        if i is 0:
            print("Selected GBWP")
            self.waterProductivityVar = "GBWP"
        elif i is 1:
            print("Selected NBWP")
            self.waterProductivityVar = "NBWP"

    def resolutionListChange(self, i):
        self.dlg.location.clear() 
        if i is 0:
            print("Selected 200 Meters")
            self.resolutionVar = "200m"
            self.dlg.location.addItems(self.locListContinental) 

        elif i is 1:
            print("Selected 100 Meters")
            self.resolutionVar = "100m"
            self.dlg.location.addItems(self.locListNational) 

        elif i is 2:
            print("Selected 30 Meters")
            self.resolutionVar = "30m"
            self.dlg.location.addItems(self.locListSubNational) 

        # adding list of items to combo box 

    def locationChanged(self, i):
        pass

    def onStartDateChanged(self, qDate):
        # print('{0}/{1}/{2}'.format(qDate.day(), qDate.month(), qDate.year()))
        self.startSeasonVar = str(qDate.year()) + "-" + str(qDate.day())
        print("Set Start Date: ", self.startSeasonVar)

    def onEndDateChanged(self, qDate):
        # print('{0}/{1}/{2}'.format(qDate.day(), qDate.month(), qDate.year()))
        self.endSeasonVar = str(qDate.year()) + "-" + str(qDate.day())
        print("Set End Date: ", self.endSeasonVar)

    def clickOK(self):
        self.dlg.connectLabel.setText ('OK detected')
        self.wapor_connect()

    def test(self):
        # print("Inside Test function")
        path = os.path.join(self.cwd, "json", "test.json") 
        testJsonFile = open(path,) 
        request_json = json.load(testJsonFile) 

        url=r'https://io.apps.fao.org/gismgr/api/v1/query/'

        # Update json with current settings
        # request_json["params"]["waterProductivity"] = self.waterProductivityVar
        # request_json["params"]["resolution"] = self.resolutionVar
        # request_json["params"]["startSeason"] = self.startSeasonVar
        # request_json["params"]["endSeason"] = self.endSeasonVar

        request_headers = {
                    'Authorization': "Bearer " + self.AccessToken}

        response = requests.post(
                        url,
                        json=request_json,
                        headers=request_headers)
        response_json=response.json()
        print(response_json)

        if response_json['message']=='OK':
            job_url = response_json['response']['links'][0]['href']
        else:
            print('Fail to get job url')
            response = requests.get(
                                job_url)
            response.json()

        print('Waiting WaPOR')
        self.dlg.downloadButton.setEnabled(False)
        self.dlg.downloadLabel.setText ('Waiting WaPOR')
        self.dlg.progressLabel.setText ('Getting links to download Rasters ...')
        while True:
            QApplication.processEvents()
            response = requests.get(job_url)
            response_json=response.json()
            if response_json['response']['status']=='COMPLETED':
                gbwp = response_json['response']['output']['bwpDownloadUrl']
                tbp = response_json['response']['output']['tbpDownloadUrl']
                aeti = response_json['response']['output']['wtrDownloadUrl']
                self.dlg.downloadLabel.setText ('Url in memory')
                break
                
        print('Link to download GBWP',gbwp)
        print('Link to download TBP',tbp)
        print('Link to download AETI',aeti)
        self.dlg.progressBar.setValue(50)
        self.dlg.progressLabel.setText ('Received links to download Rasters')
        url= aeti
        file_name = url.rsplit('/', 1)[1]
        file_dir = os.path.join(self.cwd, "layers", file_name)
        wget.download(url, file_dir)
        self.dlg.progressLabel.setText ('Downloading Rasters ...')
        while True:
            QApplication.processEvents()
            if os.path.isfile(file_dir):
                self.dlg.downloadLabel.setText ('File in memory')
                self.dlg.downloadButton.setEnabled(True)
                break
        self.dlg.progressBar.setValue(100)
        self.dlg.progressLabel.setText ('Downloaded Rasters')
        
    def listRasters(self):
        tif_files_dir, tif_names = self.file_manag.listRasters(self.rasters_path)
        print(tif_names)

    def load(self):
        self.listRasters()
        self.canv_manag.add_rast("L2_GBWP_1501-1518.tif")

    def refreshRasters(self):
        indic_dir = os.path.join(self.layer_folder_dir, "indic")
        self.raster1 = []
        self.raster1_dir = []
        for _, _, files in os.walk(indic_dir):
            for name in files:
                self.raster1_dir.append(os.path.join(indic_dir, name))
            self.raster1 = list(files)
        self.raster2 = self.raster1
        self.raster2_dir = self.raster1_dir

        self.dlg.raster1.clear()
        self.dlg.raster2.clear()

        self.dlg.raster1.addItems(self.raster1)
        self.dlg.raster2.addItems(self.raster2)

    def calculateIndex(self):
        print('Calculating . . . ')

        tbp_name = "L3_BKA_TBP_18s1.tif"
        aeti_name = "L3_BKA_AETI_1806M.tif"
        output_name = self.dlg.outputIndicName.text()+".tif"

        self.indic_calc.test_calc(tbp_name,aeti_name,output_name)

        self.canv_manag.add_rast(tbp_name)
        self.canv_manag.add_rast(aeti_name)
        self.canv_manag.add_rast(output_name)


    def run(self):
        """Run method that performs all the real work"""
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = WAPluginDialog()

            self.dlg.downloadButton.setEnabled(False)

            self.dlg.connectButton.clicked.connect(self.clickOK)
            self.dlg.downloadButton.clicked.connect(self.test)
            self.dlg.loadButton.clicked.connect(self.load)

            # self.dlg.workspaceComboBox.currentIndexChanged.connect(self.workspaceChange)
            # self.dlg.cubeComboBox.currentIndexChanged.connect(self.cubeChange)
            # self.dlg.dimensionComboBox.currentIndexChanged.connect(self.dimensionChange)
            # self.dlg.startDate.dateChanged.connect(self.onStartDateChanged)
            # self.dlg.endDate.dateChanged.connect(self.onEndDateChanged)

            self.dlg.calculateButton.clicked.connect(self.calculateIndex)
            # self.dlg.tabWidget.currentChanged.connect(self.refreshRasters)

            self.listWorkspaces()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
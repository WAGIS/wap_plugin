# WAP Plugin: WAGIS Tools and Services
<img src="https://github.com/WAGIS/wap_plugin/blob/master/img/WaPlugin_Logo.png" width="256">

1. [What is wap_plugin?](#what-is-wap_plugin)
2. [What is wap_plugin for?](#what-is-wap_plugin-for)
3. [What problem does wap_plugin solve?](#what-problem-does-wap_plugin-solve)
4. [How does wap_plugin accomplish its goals?](#how-does-wap_plugin-accomplish-its-goals)
5. [Releases](https://github.com/WAGIS/wap_plugin/releases)

## What is wap_plugin?
The WAPlugin is a tool created on the open-source software QGIS to compute water accounting and crop water productivity indicators based on WaPOR data, the open-access remote sensing database from FAO. The plugin creates a bridge between WaPOR information and QGIS. It offers some tools to process and calculate the indicators, such as the overall consumed ratio, the depleted fraction, the overall field application ratio, etc. Most of these water accounting and productivity indicators reflect agriculture's impact on water resources. Hence, their analysis will help identify specific issues that can be addressed by policymakers, large scheme irrigation managers, river basin authorities, water professionals, among others.

## How to install the plugin?
The installation instructions for the plugin are [here](https://github.com/WAGIS/wap_plugin/wiki/Getting-Started#installation).

## How to use?
Check the [wiki page](https://github.com/WAGIS/wap_plugin/wiki) for detailed tutorials on using this plugin.

## What is wap_plugin for?
The WAPlugin is a bridge that connects WaPOR, the free FAO portal, and QGIS, the open-source software, making the WaPOR data easy to access and providing the possibility to calculate water accounting and productivity indicators for agricultural purposes.

## What problem does wap_plugin solve?
The WAPlugin facilitates the water accounting and productivity analysis by bringing together two powerful open-source platforms for the water and remote sensing community. The plugin reduces the time consuming and enables the easy access and processing of WaPOR data, making this less time consuming for GIS analysts. Furthermore, the indicators will support users by generating maps and reports for further assessment and evaluation, identifying the places of high and low irrigation efficiency and the crop and water productivity behaviour.

## How does wap_plugin accomplish its goals?
It is possible to access the WAPlugin as any other QGIS plugin. The workflow figure below shows that it has two main features: the `WaPOR Catalog` and the `Indicators Calculator`. 

<img src="https://github.com/WAGIS/wap_plugin/blob/master/img/waplugin_workflow.png" width="640">

The `WaPOR Catalog` can bring data from WaPOR to QGIS, providing direct access to the entire catalogue. The selection will depend on the user specifications (date, location, parameter, resolution). The selected map data will appear on the canvas as a raster layer.

The `Indicators Calculator` allows calculating some of the essential water accounting and productivity indicators based on WaPOR data. As in the first feature, the user must specify the primary data like date, location, resolution and units. Depending on the indicator, the input data can also include information provided by the user, apart from the WaPOR data. Finally, the resulting indicator map will be added as a raster layer in the QGIS canvas, facilitating access to WaPOR data for QGIS users and providing compatibility with the QGIS tools for further processing.

from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from qgis.core import QgsRasterLayer

import os

class IndicatorCalculator:
    def __init__(self, plugin_dir, rasters_path):
        self.plugin_dir = plugin_dir
        self.rasters_dir = os.path.join(self.plugin_dir,rasters_path)

    def test_calc(self, tbp_name, aeti_name, output_name):
        ras_tbp_dir = os.path.join(self.rasters_dir, tbp_name)
        ras_tbp = QgsRasterLayer(ras_tbp_dir)
        ras_aeti_dir = os.path.join(self.rasters_dir, aeti_name)
        ras_aeti = QgsRasterLayer(ras_aeti_dir)

        output_dir = os.path.join(self.rasters_dir, output_name)

        entries = []

        ras = QgsRasterCalculatorEntry()
        ras.ref = 'ras@1'
        ras.raster = ras_tbp
        ras.bandNumber = 1
        entries.append(ras)

        ras = QgsRasterCalculatorEntry()
        ras.ref = 'ras@2'
        ras.raster = ras_aeti
        ras.bandNumber = 1
        entries.append(ras)

        calc = QgsRasterCalculator('ras@1 / (ras@2 * 0.1 * 10 * 6)', output_dir, 'GTiff',\
                ras_tbp.extent(), ras_tbp.width(), ras_tbp.height(), entries)
        print(calc.processCalculation())

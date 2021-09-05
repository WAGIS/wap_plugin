"""
    Indicator computation and additional resources and respective links for computation

    - Some common operation with QGIS
        https://docs.qgis.org/3.10/en/docs/pyqgis_developer_cookbook/raster.html
    - A python library to convert raster to numpy array
        https://geoscripting-wur.github.io/PythonRaster/
    - Using python library gdal
        https://www.youtube.com/watch?v=Rv8v9HPVq9M
    - Using Notbook for computations after converting to python array
        https://github.com/wateraccounting/WAPORWP/blob/master/Notebooks/Module_3_CalculatePerformanceIndicators.ipynb

"""
import numpy as np
import gdal
import os

from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from qgis.core import QgsRasterLayer

class IndicatorCalculator:
    def __init__(self, plugin_dir, rasters_path):
        self.plugin_dir = plugin_dir
        self.rasters_dir = os.path.join(self.plugin_dir,rasters_path)

    def equity(self, raster):
        """
        Equity is computed from the formula,
            equity = 0.1 * (AETIsd / AETImean) * 100
                where,
                    AETIsd - (real number) - Standard deviation obtained from a Raster
                        Formula: AETIsd = Standard deviation of a Raster 
                        Raster Types: AETI, PE, ACB
                        Conversion Factor:
                            AETI - 0.1
                            PE - 0.01
                            ACB - 50
                    AETImean - (real number) - Mean obtained from a Raster
                            Formula: AETIsd = Mean of a Raster
                            Raster Types: AETI, PE
                            Conversion Factor:
                                AETI - 0.1
                                PE - 0.01
                    0.1 - (reak number) - Unit conversion factor because the rasters are in different unit from Wapor
            Output:
                equity - real number
        """
        ras_atei_dir = os.path.join(self.rasters_dir, raster)
        ds = gdal.Open(ras_atei_dir)
        atei_band1 = ds.GetRasterBand(1).ReadAsArray()
        atei_band1 = atei_band1.astype(np.float)
        atei_band1[atei_band1 == -9999] = float('nan')
        AETIm   = np.nanmean(atei_band1 * 0.1)
        AETIsd  = np.nanstd(atei_band1 * 0.1)

        equity = (AETIsd / AETIm) * 100
        
        print("Equity for the given Raster is: ", equity)

    def overall_consumption_ratio(self):
        raise NotImplementedError("Indicator: 'Overall Consumption Ratio' not implemented.")

    def water_productivity(self):
        raise NotImplementedError("Indicator: 'Water Productivity' not implemented yet.")

    def overall_field_app_ratio(self):
        raise NotImplementedError("Indicator: 'Overall Field Application Ratio' not implemented yet.")

    def crop_yield(self):
        raise NotImplementedError("Indicator: 'Crop Yield' not implemented yet.")

    def field_app_ratio(self):
        raise NotImplementedError("Indicator: 'Field Application Ratio' not implemented yet.")

    def depleted_fraction(self):
        raise NotImplementedError("Indicator: 'Depletion Fraction' not implemented yet.")

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

        calc = QgsRasterCalculator('ras@1 / (ras@2 * 0.1 * 10 * 6)',
                                    output_dir,
                                    'GTiff',
                                    ras_tbp.extent(),
                                    ras_tbp.width(),
                                    ras_tbp.height(),
                                    entries)
        print(calc.processCalculation())

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
from osgeo import gdal
import os

from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from qgis.core import QgsRasterLayer

"""
    '<NAME_INDICATOR>' : {
        'info' : '<FORMULA_TO_COMPUTE_THE_INDICATOR>',
        'rasters' : { 
            # Pairs code and name of the rasters used 
            '<CODE_RASTER_1>' : '<NAME_RASTER_1>',
            '<CODE_RASTER_2>' : '<NAME_RASTER_2>',
            .
            .
            .
            '<CODE_RASTER_N>' : '<NAME_RASTER_N>' 
        },
        'factors' : {
            # Coeficients used in the formula, might or might not be provided
            # by the user through the UI
            'FACTOR_1' : 'DESCRIPTION_FACTOR_1',
            'FACTOR_2' : 'DESCRIPTION_FACTOR_2',
            .
            .
            .
            'FACTOR_N' : 'DESCRIPTION_FACTOR_N'
        },
        'params' : {
            # Parameters to be readed from the UI
            'PARAM_1' : {'label':'AETI or PE', 'type': ['AETI','PE']},
            'PARAM_2' : '',
            'PARAM_3' : ''
        }
"""

INDICATORS_INFO = {
                    'Equity' : {
                        'info' : 'equity = 0.1 * (sd_raster / mean_raster) * 100',
                        'rasters' : {
                            'AETI' : 'Actual Evapotranspiration and Interception',
                            'PE' : 'Potential Evapotranspitarion'
                            # 'ACB' : 'Name of ACB'
                        },
                        'factors' : {
                            'sd_raster' : 'Standard deviation obtained from the Raster',
                            'mean_raster' : 'Mean obtained from the Raster'
                        },
                        'params' : {
                            'PARAM_1' : {'label':'AETI or PE', 'type': ['AETI','PE']},
                            'PARAM_2' : '',
                            'PARAM_3' : ''
                        }
                    },
                    'Beneficial Fraction' : {
                        'info' : 'BF = (Raster_1 / Raster_2)',
                        'rasters' : {
                            'AETI' : 'Actual Evapotranspiration and Interception',
                            'T' : 'Transpiration'
                        },
                        'factors' : {
                            'Conversion Factor' : '0.1'
                        },
                        'params' : {
                            'PARAM_1' : {'label':'AETI Raster', 'type': ['AETI']},
                            'PARAM_2' : {'label':'T Raster', 'type': ['T']},
                            'PARAM_3' : ''
                        }
                    },
                    'Adequacy' : {
                        'info' : 'AD = (Raster_1 / (Kc * Raster_2))',
                        'rasters' : {
                            'AETI' : 'Actual Evapotranspiration and Interception',
                            'RET' : 'Reference Evapotranspiration'
                        },
                        'factors' : {
                            'Kc' : 'A constant to compute Potential Evapotranspiration'
                        },
                        'params' : {
                            'PARAM_1' : {'label':'AETI Raster', 'type': ['AETI']},
                            'PARAM_2' : {'label':'RET Raster', 'type': ['RET']},
                            'PARAM_3' : 'Kc'
                        }
                    },
                    'Relative Water Deficit' : {
                        'info' : 'RWD = 1 - (Raster / ETx)',
                        'rasters' : {
                            'AETI' : 'Actual Evapotranspiration and Interception'
                        },
                        'factors' : {
                            'ETx' : '99 percentile of the Raster'
                        },
                        'params' : {
                            'PARAM_1' : {'label':'AETI Raster', 'type': ['AETI']},
                            'PARAM_2' : '',
                            'PARAM_3' : ''
                        }
                    },
                    'Overall Consumed Ratio' : {
                        'info' : 'OCR = (AETI - PCP) / V_ws',
                        'rasters' : {
                            'AETI' : 'Actual Evapotranspiration and Interception',
                            'PCP' : 'Precipitation'
                        },
                        'factors' : {
                            'V_ws' : 'Volume of water supplied to command area in mm.'
                        },
                        'params' : {
                            'PARAM_1' : {'label':'AETI Raster', 'type': ['AETI']},
                            'PARAM_2' : {'label':'PCP Raster', 'type': ['PCP']},
                            'PARAM_3' : 'V_ws'
                        }
                    },
                    'Field Application Ratio (efficiency)' : {
                        'info' : 'FAR = (AETI - PCP) / V_wd',
                        'rasters' : {
                            'AETI' : 'Actual Evapotranspiration and Interception',
                            'PCP' : 'Precipitation'
                        },
                        'factors' : {
                            'V_wd' : 'Volume of water delivered to field(s) in mm.'
                        },
                        'params' : {
                            'PARAM_1' : {'label':'AETI Raster', 'type': ['AETI']},
                            'PARAM_2' : {'label':'PCP Raster', 'type': ['PCP']},
                            'PARAM_3' : 'V_wd'
                        }
                    },
                    'Depleted Fraction' : {
                        'info' : 'DF = 1 - AETI / (PCP + V_c)',
                        'rasters' : {
                            'AETI' : 'Actual Evapotranspiration and Interception',
                            'PCP' : 'Precipitation'
                        },
                        'factors' : {
                            'V_c' : 'Volume of water consumed in mm.'
                        },
                        'params' : {
                            'PARAM_1' : {'label':'AETI Raster', 'type': ['AETI']},
                            'PARAM_2' : {'label':'PCP Raster', 'type': ['PCP']},
                            'PARAM_3' : 'V_c'
                        }
                    }
                  }

class IndicatorCalculator:
    def __init__(self, plugin_dir, rasters_path):
        self.plugin_dir = plugin_dir
        self.rasters_dir = os.path.join(self.plugin_dir, rasters_path)

    def setRastersDir(self, newPath):
        self.rasters_dir = os.path.join(self.plugin_dir, newPath)

    def equity(self, raster, outLabel):
        """
        [FORMULA PASSED THE TEST WITH TRUE VALUES]
        Equity is computed from the formula:
            --- equity = 0.1 * (AETIsd / AETImean) * 100
            --- Resolution: Continental, National, Sub-national 
            where:
                -- AETIsd - (real number) - Standard deviation obtained from a Raster:
                --- Formula: AETIsd = Standard deviation of a Raster 
                --- Raster Types: AETI, PE, ACB
                --- Conversion Factor: AETI - 0.1, PE - 0.01, ACB - 50
                -- AETImean - (real number) - Mean obtained from a Raster
                    --- Formula: AETIsd = Mean of a Raster
                        --- Raster Types: AETI, PE
                        --- Conversion Factor: AETI - 0.1, PE - 0.01
                --- 0.1 - (real number) - Unit conversion factor because the rasters are in different unit from Wapor

        Output:
        --- equity - real number
        """
        ras_atei_dir = os.path.join(self.rasters_dir, raster)
        print('test equity')
        print(self.rasters_dir)
        print(ras_atei_dir)
        print(raster)
        ds = gdal.Open(ras_atei_dir)
        atei_band1 = ds.GetRasterBand(1).ReadAsArray()
        atei_band1 = atei_band1.astype(np.float64)
        atei_band1[atei_band1 == -9999] = float('nan')
        AETIm   = np.nanmean(atei_band1 * 0.1)
        AETIsd  = np.nanstd(atei_band1 * 0.1)

        equity = (AETIsd / AETIm) * 100
        
        print("Equity for the given Raster is: ", equity)
        outLabel.setText('Equity {}'.format(equity))

    def beneficial_fraction(self, aeti_dir, ta_dir, output_name):
        """
        [FORMULA PASSED THE TEST WITH TRUE VALUES]
        Beneficial fraction is computed from the formula:
        --- BF = (AETI / TA)
        --- Resolution: Continental, National, Sub-national 
        where:
            -- AETI - (raster) - Actual Evapotranspiration and Interception 
            --- Raster Types: AETI (annual, dekadal)
            --- Conversion Factor: 0.1
            -- TA - (raster) - Mean obtained from a Raster
                --- Raster Types: TA (annual, dekadal)
                --- Conversion Factor: 0.1
        --- Units: decimal or percentage(*100)

        Output:
        --- BF - Raster
        """
        ras_atei_dir = os.path.join(self.rasters_dir, aeti_dir)
        ras_ta_dir = os.path.join(self.rasters_dir, ta_dir)
        output_dir = os.path.join(self.rasters_dir, output_name)

        ras_atei = QgsRasterLayer(ras_atei_dir)
        ras_ta = QgsRasterLayer(ras_ta_dir)

        entries = []

        ras = QgsRasterCalculatorEntry()
        ras.ref = 'ras@1'
        ras.raster = ras_atei
        ras.bandNumber = 1
        entries.append(ras)

        ras = QgsRasterCalculatorEntry()
        ras.ref = 'ras@2'
        ras.raster = ras_ta
        ras.bandNumber = 1
        entries.append(ras)

        calc = QgsRasterCalculator('ras@1 / ras@2',
                                    output_dir,
                                    'GTiff',
                                    ras_atei.extent(),
                                    ras_atei.width(),
                                    ras_atei.height(),
                                    entries)
        print(calc.processCalculation())

    def adequacy(self, aeti_dir, ret_dir, output_name, Kc=1.25):
        """
        [FORMULA PASSED THE TEST WITH TRUE VALUES]
        Adequacy is computed from the formula:
        --- AD = (AETI / PET)
        --- Resolution: Continental
        where:
            -- AETI - (raster) - Actual Evapotranspiration and Interception 
            --- Raster Types: AETI (annual, monthly, dekadal)
            --- Conversion Factor: 0.1
            -- PET - (raster) - Potential Evapotranspiration 
            --- Formula: PET = Kc * RET
            --- Kc (real number) - provided by the user
        --- RET (raster) Reference Evapotranspiration
                --- Raster Types: RET (annual, monthly, dekadal)
                --- Conversion Factor: 0.1
        --- Units: decimal or percentage(*100)

        Output:
        --- AD - Raster
        """
        ras_atei_dir = os.path.join(self.rasters_dir, aeti_dir)
        ras_ret_dir = os.path.join(self.rasters_dir, ret_dir)
        output_dir = os.path.join(self.rasters_dir, output_name)

        ras_atei = QgsRasterLayer(ras_atei_dir)
        ras_ret = QgsRasterLayer(ras_ret_dir)

        entries = []

        ras = QgsRasterCalculatorEntry()
        ras.ref = 'ras@1'
        ras.raster = ras_atei
        ras.bandNumber = 1
        entries.append(ras)

        ras = QgsRasterCalculatorEntry()
        ras.ref = 'ras@2'
        ras.raster = ras_ret
        ras.bandNumber = 1
        entries.append(ras)

        calc = QgsRasterCalculator('(ras@1 * 0.1) / ({} * {})'.format('ras@2 * 0.1', str(Kc)),
                                    output_dir,
                                    'GTiff',
                                    ras_atei.extent(),
                                    ras_atei.width(),
                                    ras_atei.height(),
                                    entries)
        print(calc.processCalculation())


    def relative_water_deficit(self, aeti_dir, output_name):
        """
        [FORMULA PASSED THE TEST WITH TRUE VALUES]
        Relative water deficit is computed from the formula:
        --- RWD = 1 - (AETI / ETx)
        --- Resolution: Continental, National, Sub-national 
        where:
            -- AETI - (raster) - Actual Evapotranspiration and Interception 
            --- Raster Types: AETI (annual, monthly, dekadal)
            --- Conversion Factor: 0.1
            -- ETx - (real number) - 99 percentile of the actual evapotranspiration
        --- Formula: ETx = 99 percentile of a Raster (AETI)
                --- Raster Types: AETI (annual, monthly, dekadal)
                --- Conversion Factor: 0.1
        --- Units: decimal or percentage(*100)

        Output:
        --- RWD - Raster
        """
        ras_atei_dir = os.path.join(self.rasters_dir, aeti_dir)
        output_dir = os.path.join(self.rasters_dir, output_name)
        ras_atei = QgsRasterLayer(ras_atei_dir)

        ds = gdal.Open(ras_atei_dir)
        atei_band1 = ds.GetRasterBand(1).ReadAsArray()
        atei_band1 = atei_band1.astype(np.float)
        atei_band1[atei_band1 == -9999] = float('nan')
        AETI1_1D  = np.reshape(atei_band1,  atei_band1.shape[0] * atei_band1.shape[1])

        ETx = np.nanpercentile(AETI1_1D * 0.1, 99)
        print(ETx)

        entries = []
        ras = QgsRasterCalculatorEntry()
        ras.ref = 'ras@1'
        ras.raster = ras_atei
        ras.bandNumber = 1
        entries.append(ras)
        
        calc = QgsRasterCalculator('1 - (ras@1 * 0.1 / {})'.format(str(ETx)),
                                    output_dir,
                                    'GTiff',
                                    ras_atei.extent(),
                                    ras_atei.width(),
                                    ras_atei.height(),
                                    entries)
        print(calc.processCalculation())

    def overall_consumed_ratio(self, aeti_dir, pcp_dir, output_name, V_ws):
        """
        Overall consumed ratio is computed from the formula:
        --- OCR = 1 - (AETI -PCP)/ V_ws
        --- Resolution: Continental
        where:
            -- AETI - (raster) - Actual Evapotranspiration and Interception 
                --- Raster Types: AETI (annual, monthly, dekadal)
                --- Conversion Factor: 0.1
            -- PCP - (raster) - Precipitation 
                --- Raster Types: PCP (annual, monthly, dekadal)
                --- Conversion Factor: 0.1
            -- V_ws - (real number) - Volume of water supplied to command area 
                --- User input -in mm (1mm=1l/m² or 1mm=10m³/ha) 

        Output:
            --- OCR - Raster

        """
        ras_atei_dir = os.path.join(self.rasters_dir, aeti_dir)
        ras_pcp_dir = os.path.join(self.rasters_dir, pcp_dir)
        output_dir = os.path.join(self.rasters_dir, output_name)

        ras_atei = QgsRasterLayer(ras_atei_dir)
        ras_pcp = QgsRasterLayer(ras_pcp_dir)

        entries = []

        ras = QgsRasterCalculatorEntry()
        ras.ref = 'ras@1'
        ras.raster = ras_atei
        ras.bandNumber = 1
        entries.append(ras)

        ras = QgsRasterCalculatorEntry()
        ras.ref = 'ras@2'
        ras.raster = ras_pcp
        ras.bandNumber = 1
        entries.append(ras)

        calc = QgsRasterCalculator('1.0 - (ras@1 * 0.1 - ras@2 * 0.1) / {}'.format(str(V_ws)),
                                    output_dir,
                                    'GTiff',
                                    ras_atei.extent(),
                                    ras_atei.width(),
                                    ras_atei.height(),
                                    entries)
        print(calc.processCalculation())

    def field_application_ratio(self, aeti_dir, pcp_dir, output_name, V_wd):
        """
        Field appliation ratio is computed from the formula:
        --- FAR = 1 - (AETI - PCP)/Vwd
        --- Resolution: Continental
        where:
            -- AETI - (raster) - Actual Evapotranspiration and Interception 
                --- Raster Types: AETI (annual, monthly, dekadal)
                --- Conversion Factor: 0.1
            -- PCP - (raster) - Precipitation 
                --- Raster Types: PCP (annual, monthly, dekadal)
                --- Conversion Factor: 0.1
            -- Vwd - (real number) - Volume of water delivered to field(s)
                --- User input -in mm (1mm=1l/m² or 1mm=10m³/ha) 

        --- Units: decimal or percentage(*100)

        Output:
        --- FAR - Raster
        """
        ras_atei_dir = os.path.join(self.rasters_dir, aeti_dir)
        ras_pcp_dir = os.path.join(self.rasters_dir, pcp_dir)
        output_dir = os.path.join(self.rasters_dir, output_name)

        ras_atei = QgsRasterLayer(ras_atei_dir)
        ras_pcp = QgsRasterLayer(ras_pcp_dir)

        entries = []

        ras = QgsRasterCalculatorEntry()
        ras.ref = 'ras@1'
        ras.raster = ras_atei
        ras.bandNumber = 1
        entries.append(ras)

        ras = QgsRasterCalculatorEntry()
        ras.ref = 'ras@2'
        ras.raster = ras_pcp
        ras.bandNumber = 1
        entries.append(ras)

        calc = QgsRasterCalculator('1.0 - (ras@1 * 0.1 - ras@2 * 0.1) / {}'.format(str(V_wd)),
                                    output_dir,
                                    'GTiff',
                                    ras_atei.extent(),
                                    ras_atei.width(),
                                    ras_atei.height(),
                                    entries)
        print(calc.processCalculation())


    def depleted_fraction(self, aeti_dir, pcp_dir, output_name, V_c):
        """
        Depleted fraction is computed from the formula:
        --- DF = 1 - AETI /(PCP + Vc)
        --- Resolution: Continental
        where:
            -- AETI - (raster) - Actual Evapotranspiration and Interception 
                --- Raster Types: AETI (annual, monthly, dekadal)
                --- Conversion Factor: 0.1
            -- PCP - (raster) - Precipitation 
                --- Raster Types: PCP (annual, monthly, dekadal)
                --- Conversion Factor: 0.1
            -- Vc - (real number) - Volume of water consumed
                --- User input -in mm (1mm=1l/m² or 1mm=10m³/ha) 
        
        --- Units: decimal or percentage(*100)

        Output:
        --- DF - Raster
        """
        ras_atei_dir = os.path.join(self.rasters_dir, aeti_dir)
        ras_pcp_dir = os.path.join(self.rasters_dir, pcp_dir)
        output_dir = os.path.join(self.rasters_dir, output_name)

        ras_atei = QgsRasterLayer(ras_atei_dir)
        ras_pcp = QgsRasterLayer(ras_pcp_dir)

        entries = []

        ras = QgsRasterCalculatorEntry()
        ras.ref = 'ras@1'
        ras.raster = ras_atei
        ras.bandNumber = 1
        entries.append(ras)

        ras = QgsRasterCalculatorEntry()
        ras.ref = 'ras@2'
        ras.raster = ras_pcp
        ras.bandNumber = 1
        entries.append(ras)

        calc = QgsRasterCalculator('1.0 - ras@1 * 0.1/ (ras@2 * 0.1 + {})'.format(str(V_c)),
                                    output_dir,
                                    'GTiff',
                                    ras_atei.extent(),
                                    ras_atei.width(),
                                    ras_atei.height(),
                                    entries)
        print(calc.processCalculation())


    def crop_yield(self):
        raise NotImplementedError("Indicator: 'Crop Yield' not implemented yet.")

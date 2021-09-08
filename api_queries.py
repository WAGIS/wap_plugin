bbox = [37.95883206252312, 7.89534, 43.32093, 12.3873979377346] #latlon

xmin, ymin, xmax, ymax = bbox[0], bbox[1], bbox[2], bbox[3]

Polygon = [
          [xmin,ymin],
          [xmin,ymax],
          [xmax,ymax],
          [xmax,ymin],
          [xmin,ymin]
        ]

crop_raster_query = {
                    "type": "CropRaster",
                    "params": {
                        "properties": {
                            "outputFileName": "L2_PHE_17s1_s_clipped.tif",
                            "cutline": True,
                            "tiled": True,
                            "compressed": True,
                            "overviews": True
                        },
                        "cube": {
                            "code": "L2_PHE_S",
                            "workspaceCode": "WAPOR",
                            "language": "en"
                        },
                        "dimensions": [
                            {
                                "code": "SEASON",
                                "values": [
                                    "S1"
                                ]
                            },
                            {
                                "code": "STAGE",
                                "values": [
                                    "SOS"
                                ]
                            },
                            {
                                "code": "YEAR",
                                "values": [
                                    "[2017-01-01,2018-01-01)"
                                ]
                            }
                        ],
                        "measures": [
                            "PHE"
                        ],
                        "shape": {
                            "type": "Polygon",
                            "coordinates": [Polygon]
                        }
                    }
                }
import processing
import os
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsColorRampShader
)
from PyQt5 import QtGui
from glob import glob

#time the script
from datetime import datetime
startTime = datetime.now()

#coloring from: 
#https://www.gislounge.com/symbolizing-vector-and-raster-layers-qgis-python-programming-cookbook/

dirs = "/dir/"
list_of_dirs = glob(dirs + "*/")

for j in list_of_dirs:

   dir_of_tiffs = j
   all_files = glob(os.path.join(dir_of_tiffs, "*.tif"))

   for i in all_files:
       #get basename of each tif
       tiff_basename = os.path.basename(i)
       #strip .tif off the i variable
       i = tiff_basename[:-4]
       #path to raster for each i
       tif = ".tif"
       path_to_tif = dir_of_tiffs + i + tif
       #path to OR shp
       OR_shp = "/cb_2018_us_state_20m/oregon.shp"
       #path to output dir of clipped OR tiffs
       clipped_OR_tifs = "/clipped_OR_tifs/" + i + tif
       #clip the raster with OR shapefile
       processing.run('gdal:cliprasterbymasklayer',{'INPUT': path_to_tif,
       'MASK': OR_shp,
       'NODATA': -1,
       'ALPHA_BAND': False,
       'CROP_TO_CUTLINE': True,
       'KEEP_RESOLUTION': True,
       'OPTIONS': "",
       'DATA_TYPE': 0,
       'OUTPUT': clipped_OR_tifs
       })
       print("clipped raster " + i)

       #create layer
       rlayer = QgsRasterLayer(clipped_OR_tifs, i)
       if rlayer.isValid():
           print("loaded")
       else:
          print("failed to load")
       #raster shader and ramp shader objects
       s = QgsRasterShader()
       c = QgsColorRampShader()
       c.setColorRampType(QgsColorRampShader.Interpolated)
       #list to hold color ramp definition and append color ramp values
       j = []
       j.append(QgsColorRampShader.ColorRampItem(0, QtGui.QColor("#f7fbff"), "0"))
       j.append(QgsColorRampShader.ColorRampItem(105, QtGui.QColor("#deebf7"), "105"))
       j.append(QgsColorRampShader.ColorRampItem(210, QtGui.QColor("#c6dbef"), "210"))
       j.append(QgsColorRampShader.ColorRampItem(315, QtGui.QColor("#9ecae1"), "315"))
       j.append(QgsColorRampShader.ColorRampItem(420, QtGui.QColor("#6baed6"), "420"))
       j.append(QgsColorRampShader.ColorRampItem(525, QtGui.QColor("#4292c6"), "525"))
       j.append(QgsColorRampShader.ColorRampItem(630, QtGui.QColor("#2171b5"), "630"))
       j.append(QgsColorRampShader.ColorRampItem(735, QtGui.QColor("#08519c"), "735"))
       j.append(QgsColorRampShader.ColorRampItem(840, QtGui.QColor("#08306b"), "840"))
       #assign color ramp and use raster shaders color ramp
       c.setColorRampItemList(j)
       s.setRasterShaderFunction(c)
       #raster renter object, asign renderer to layer, add to map
       ps = QgsSingleBandPseudoColorRenderer(rlayer.dataProvider(), 1, s)
       rlayer.setRenderer(ps)
       QgsProject.instance().addMapLayer(rlayer)
       #setup html file output
       output_dir = "/data2/" + i
       html = ".html"
       output_html = "/data2/" + i + html
       #make dir to hold each tile file
       os.mkdir(output_dir)
       print("created dir " + i)
       #run qgis:tilesxyzdirectory processing algorithm
       processing.run("qgis:tilesxyzdirectory", {'EXTENT': '-124.520833333,-116.479166666,42.020833333,46.229166667 [EPSG:4269]',
       'ZOOM_MIN': 1,
       'ZOOM_MAX': 12,
       'DPI': 96,
       'TILE_FORMAT': 0,
       'TILE_WIDTH': 256,
       'TILE_HEIGHT': 256,
       'OUTPUT_DIRECTORY': output_dir,
       'OUTPUT_HTML': output_html
       })
       print(i + " has been xyzed")
       #remove layers and start over
       QgsProject.instance().removeAllMapLayers()

endTime = datetime.now()
finalTime = endTime - startTime
print("Took this long to run: " + str(finalTime))


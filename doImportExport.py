
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import numpy
import gdal

def read_shp(tree_layer, gdal_geo_transform):

    pix = gdal_geo_transform[1]
    raster_x_min = gdal_geo_transform[0]
    raster_y_max = gdal_geo_transform[3]
    
    net={}
    
    tree_ly=QgsMapLayerRegistry.instance().mapLayer(tree_layer)
    if not tree_ly.isValid(): return
    
 #   obs_has_ID  = bool( Obs_layer.fieldNameIndex ("ID") + 1)
    i=0
    fs = tree_ly.getFeatures()
    for f in fs:
        geom = f.geometry()
        x = geom.asPolyline()
        i+=1
        l=[]
        for p in x :
            #tuple
            pt = (int((p[0] - raster_x_min) / pix) , 
                  int((raster_y_max - p[1]) / pix)) #reversed ! # not float !

            l.append(pt)
            
                    
        net[l[0]] = [l[-1]] # first to last!
    return net

# cannot write complex lines !!!!
# graph - nodes
def write_shp (file_name, dict_lines,
                 coordinate_ref_system, gdal_geo_transform ,
                 center_pixel=True, shp_type = 'line' ):

    #line = {points: [(4,6), field: val ....}
    
    pix = gdal_geo_transform[1]
    half_pix = pix/2 if center_pixel else 0
    
    raster_x_min = gdal_geo_transform[0]
    raster_y_max = gdal_geo_transform[3]

    
    keys=[]
    fields = QgsFields() #there's a BUG in QGIS here (?), normally : fields = .... 

    for key in dict_lines[dict_lines.keys()[0]]:# take ANY record to read fields 
        if key != 'points':
        
            f_name=str(key[0:-2])

            if key[-2]=="_i":
                fields.append(QgsField(f_name, QVariant.Int,'integer',10))
            elif key[-2]=="_f":
                fields.append(QgsField(f_name, QVariant.Double,'double',10,5))
            else :
                fields.append(QgsField(f_name, QVariant.String, 'string',50))
                
            keys.append([key, f_name, key[-2]])

    if shp_type=='line' : layer_type= QGis.WKBLineString
    elif shp_type=='point': layer_type= QGis.WKBPoint
    
    writer = QgsVectorFileWriter( file_name + ".shp", "CP1250", fields,
                                  layer_type , coordinate_ref_system) #, "ESRI Shapefile"
                                            #CP... = encoding
    if writer.hasError() != QgsVectorFileWriter.NoError:
        QMessageBox.information(None, "ERROR!", "Cannot write network file (?)")
        return 0
       

    for r in dict_lines:
 
       # coords=[r]+graph[r] # FOR COMPEX LINES !!
        coords= dict_lines[r]['points']
        pts=[]
        for c in coords: # for each target node - new line !!!

           #pts=[  QgsPoint (r[0]*pix + raster_x_min + half_pix, (raster_y_max - r[1]*pix) - half_pix)]
            pts.append(QgsPoint (c[0]*pix + raster_x_min + half_pix, (raster_y_max - c[1]*pix) - half_pix))              
        
        feat = QgsFeature() # create a new feature

        if shp_type == 'line': feat.setGeometry(QgsGeometry.fromPolyline(pts))
        elif shp_type == 'point':feat.setGeometry(QgsGeometry.fromPoint(pts[0]))
    ##            # do not cast ID to string: unicode problem  -- angle * distance in pixels -- distance * pixel_size
    ##            #feat.setAttributes([ str(r[0]), str(r[3]), bool(r[6]), float(r[7] * r[8]),  ])
            
        if keys:
            feat.setFields(fields)
            for key in keys:  #list of keys and field names (key - [-2] + type of value)
                try:
                    val= dict_lines[r][key[0]]
                    if key[2]=="_i": v= int(val)
                    elif key[2]=="_f": v= float(val)
                    else : v= str(val)
                    feat[key[1]] = v#first and last give the name
                except: pass
                
        writer.addFeature(feat) 
   #     del feat

    del writer
    layer = None
    return file_name + ".shp"




def write_csv(data_list, output_file, draw_to_center =True): #FALI JOS UDALJENOST KUT ITD : sve je vec u data list !!
    wkt_list=[]
    half_pix = pix/2 if draw_to_center else 0 # to obtain center coord, rather than the top left corner of a pixel
    with open(output_file + ".csv", 'w', 3)  as csvfile:
        wr = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        wr.writerow([ "WKT","ID","Step"])
        for r in data_list:
    #GLOBAL!
    #adfGeoTransform[0] /* top left x */
    #adfGeoTransform[1] /* w-e pixel resolution */
    #adfGeoTransform[2] /* rotation, 0 if image is "north up" */
    #adfGeoTransform[3] /* top left y */
    #adfGeoTransform[4] /* rotation, 0 if image is "north up" */
    #adfGeoTransform[5] /* n-s pixel resolution */

    #QMessageBox.information(None, "podatak:", str(r))id1,id2,  visibile, pix_x, pix_y ,angle,angle_block,distance
            #OUTPUT LIST: id1,x1,y1,id2,x2,y2, visib, x, y, angle,angle_block,distance
            wr.writerow(["LINESTRING (" + str (r[0][0] * pix + gt[0] + half_pix) + " " + str(gt[3]- r[0][1]*pix -half_pix) +
                                ", " + str(r[1][0] * pix + gt[0] + half_pix) + " " + str(gt[3]- r[1][1] *pix -half_pix) +
                         ")", str(r[2]), r[3]])

##        #addition for writing WKT file
##                if r[6]: #if visible
##                    wkt_list.append(["LINESTRING (" + str (r[1]*pix + gt[0]) + " " + str(gt[3]- half_pix- r[2]*pix) +
##                                    ", " + str(r[4]*pix + gt[0] + half_pix) + " " + str(gt[3]- half_pix- r[5]*pix) + ")",
##                                    r[0], r[3]])
##        if wkt_list:
##            with open(output_file + "_wkt.csv", 'w', 3)  as csvfile:
##                wr = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
##                wr.writerow(["WKT", "ID1","ID2"])
##                for s in wkt_list: wr.writerow(s)
    #QMessageBox.information(None, "tocka ", str(wkt_list))

def write_graph(data_list, output_file, draw_to_center =True): #FALI JOS UDALJENOST KUT ITD : sve je vec u data list !!
    wkt_list=[]
    half_pix = pix/2 if draw_to_center else 0 # to obtain center coord, rather than the top left corner of a pixel
    with open(output_file + ".csv", 'w', 3)  as csvfile:
        wr = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        wr.writerow([ "Node","ID_entity","X","Y","Step"])
        for r in data_list:
            #QMessageBox.information(None, "podatak:", str(r))id1,id2,  visibile, pix_x, pix_y ,angle,angle_block,distance
            #OUTPUT LIST: id1,x1,y1,id2,x2,y2, visib, x, y, angle,angle_block,distance
            wr.writerow([str (r[0][0]) , str(r[2]),
                         r[0][0][0] * pix + gt[0] + half_pix,  gt[3]- r[0][0][1]*pix -half_pix,
                         r[3]])
            
    with open(output_file + "_edges.csv", 'w', 3)  as csvfile:
        wr = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        wr.writerow([ "Source","Target","test"])
        for r in data_list:
            #QMessageBox.information(None, "podatak:", str(r))id1,id2,  visibile, pix_x, pix_y ,angle,angle_block,distance
            #OUTPUT LIST: id1,x1,y1,id2,x2,y2, visib, x, y, angle,angle_block,distance
            wr.writerow([r[0][0], r[0][1]])

def write_raster(nodes, key, out_file, xsize, ysize, projection, geo_transform): 

    rst_out = numpy.zeros((ysize, xsize),numpy.int)
     ##    spatialReference = osgeo.osr.SpatialReference()
##    spatialReference.ImportFromProj4('+proj=utm +zone=48N +ellps=WGS84 +datum=WGS84 +units=m')
##
##    spatialReference = iface.mapCanvas().mapRenderer().destinationCrs()
    
 #   spatialReference=core.QgsCoordinateReferenceSystem(4326, core.QgsCoordinateReferenceSystem.EpsgCrsId)       
    for k in nodes:
        try: rst_out[k[1], k[0]] = nodes[k][key]
        except: pass #not all nodes have keys or other values!
    driver = gdal.GetDriverByName( "GTiff"  )
    dst_ds = driver.Create(out_file, xsize, ysize, 1,gdal.GDT_Float32 )
    if not dst_ds: print "ERROR OUT!"
       
    dst_ds.SetProjection(projection)
    dst_ds.SetGeoTransform(geo_transform)
                                    #obicni rst_out: "global"
    dst_ds.GetRasterBand(1).WriteArray(rst_out, 0,0)#offset=0 

    return out_file



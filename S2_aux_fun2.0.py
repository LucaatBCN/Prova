# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 09:30:39 2016

@author: l.pipia
"""


def copyFile(src, dest):
    import shutil
    
    try:
        shutil.copy(src, dest)
    # eg. src and dest are the same file
    except shutil.Error as e:
        print('Error: %s' % e)
    # eg. source or destination doesn't exist
    except IOError as e:
        print('Error: %s' % e.strerror)
        
def get_spaced_colors(n):
    max_value = 16581375 #255**3
    interval = int(max_value / n)
    colors = [hex(I)[2:].zfill(6) for I in range(0, max_value, interval)]
    
    return [(float(i[:2], 16), float(i[2:4], 16), float(i[4:], 16)) for i in colors]
    
def md5sum(filename, blocksize=65536):
    
    import hashlib

    hash = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()

def transform_utm_to_wgs84(easting, northing, zone):
    import osr
    utm_coordinate_system = osr.SpatialReference()
    utm_coordinate_system.SetWellKnownGeogCS("WGS84") # Set geographic coordinate system to handle lat/lon
    is_northern = northing > 0    
    utm_coordinate_system.SetUTM(zone, is_northern)
    
    wgs84_coordinate_system = utm_coordinate_system.CloneGeogCS() # Clone ONLY the geographic coordinate system 
    
    # create transform component
    utm_to_wgs84_geo_transform = osr.CoordinateTransformation(utm_coordinate_system, wgs84_coordinate_system) # (, )
    return utm_to_wgs84_geo_transform.TransformPoint(easting, northing, 0) # returns lon, lat, altitude
    
    
# Hard coded link returning list of matching scenes
# https://scihub.esa.int/twiki/do/view/SciHubUserGuide/5APIsAndBatchScripting#Open_Search
def uniq(input):
  output = []
  for x in input:
    if x not in output:
      output.append(x)
  return output


class S2_granule_info:
    # Class retrieving the information contained in GRANULE XML file
    def __init__(self, tree_GRANULE):

        for ff in tree_GRANULE.getiterator():

            if ff.tag =='SENSING_TIME':
                self.SENSING_TIME =ff.text
    
            if ff.tag =='HORIZONTAL_CS_NAME':
                self.HORIZONTAL_CS_NAME =ff.text
                self.FUSE = ff.text[-3:-1]
    
            if ff.tag =='HORIZONTAL_CS_CODE':
                self.HORIZONTAL_CS_CODE =ff.text
            
            if ff.tag == 'Size':
                temp_items  =ff.items()[0][1]
                if  temp_items=='10':
                    self.NL_10m = float(ff[0].text)
                    self.NC_10m = float(ff[1].text)
                elif  temp_items=='20':
                    self.NL_20m = float(ff[0].text)
                    self.NC_20m = float(ff[1].text)
                elif  temp_items=='60':
                    self.NL_60m = float(ff[0].text)
                    self.NC_60m = float(ff[1].text)
        
            
            if ff.tag == 'Geoposition':
                temp_items  =ff.items()[0][1]
                if  temp_items=='10':
                    self.ULX_10m  = float(ff[0].text)
                    self.ULY_10m  = float(ff[1].text)
                    self.XDIM_10m = float(ff[2].text)
                    self.YDIM_10m = float(ff[3].text)
                    
                elif  temp_items=='20':
                    self.ULX_20m   = float(ff[0].text)
                    self.ULY_20m   = float(ff[1].text)
                    self.XDIM_20m  = float(ff[2].text)
                    self.YDIM_20m  = float(ff[3].text)
    
                elif  temp_items=='60':
                    self.ULX_60m   = float(ff[0].text)
                    self.ULY_60m   = float(ff[1].text)
                    self.XDIM_60m  = float(ff[2].text)
                    self.YDIM_60m  = float(ff[3].text)
                    
            if ff.tag =='Sun_Angles_Grid':
                # ZENITH
                self.SUN_Zenith_col_step = ff[0][0].text
                self.SUN_Zenith_row_step = ff[0][1].text
                SUN_Zenith_DATA= []
                for ii in range(len(ff[0][2])):
                    SUN_Zenith_DATA.append(ff[0][2][ii].text)
                self.SUN_Zenith_DATA=SUN_Zenith_DATA
                
                # ZENITH
                self.SUN_Azimuth_col_step = ff[1][0].text
                self.SUN_Azimuth_row_step = ff[1][1].text
                SUN_Azimuth_DATA= []
                for ii in range(len(ff[1][2])):
                    SUN_Azimuth_DATA.append(ff[1][2][ii].text)
                self.SUN_Azimuth_DATA=SUN_Azimuth_DATA    
                
            if ff.tag =='Mean_Sun_Angle':
                self.SUN_Zenith_Ang_MEAN  = ff[0].text
                self.SUN_Azimuth_Ang_MEAN = ff[0].text
                
            if ff.tag == 'Mean_Viewing_Incidence_Angle_List'  :
            
                View_Mean_Inc_ang_band    = []
                View_Mean_Inc_ang_Zenith  = []
                View_Mean_Inc_ang_Azimuth = []
                
                for ii in range(len(ff)):
                    View_Mean_Inc_ang_band.append(ff[ii].items()[0][1])
                    View_Mean_Inc_ang_Zenith.append(ff[ii][0].text)
                    View_Mean_Inc_ang_Azimuth.append(ff[ii][1].text)
                self.View_Mean_Inc_ang_band    = View_Mean_Inc_ang_band
                self.View_Mean_Inc_ang_Zenith  = View_Mean_Inc_ang_Zenith
                self.View_Mean_Inc_ang_Azimuth = View_Mean_Inc_ang_Azimuth
                
            if ff.tag =='CLOUDY_PIXEL_PERCENTAGE':
               self.CLOUDY_PIXEL_PERCENTAGE= ff.text
                
        self.Pol10m_ULX  =  [self.ULX_10m   ,  self.ULX_10m+(self.NC_10m-1)*self.XDIM_10m ,self.ULX_10m+(self.NC_10m-1)*self.XDIM_10m, self.ULX_10m]
        self.Pol10m_ULY  =  [self.ULY_10m   ,  self.ULY_10m , self.ULY_10m+(self.NL_10m-1)*self.YDIM_10m,  self.ULY_10m+(self.NL_10m-1)*self.YDIM_10m]
        self.Pol10m_ULXY = 'POLYGON(('+str(self.Pol10m_ULX[0])+' '+str(self.Pol10m_ULY[0])+','+str(self.Pol10m_ULX[1])+' '+str(self.Pol10m_ULY[1])+','+str(self.Pol10m_ULX[2])+' '+str(self.Pol10m_ULY[2])+','+str(self.Pol10m_ULX[3])+' '+str(self.Pol10m_ULY[3])+'))'
       
        self.Pol20m_ULX  =  [self.ULX_20m   ,  self.ULX_20m+(self.NC_20m-1)*self.XDIM_20m ,self.ULX_20m+(self.NC_20m-1)*self.XDIM_20m, self.ULX_20m]
        self.Pol20m_ULY  =  [self.ULY_20m   ,  self.ULY_20m , self.ULY_20m+(self.NL_20m-1)*self.YDIM_20m,  self.ULY_20m+(self.NL_20m-1)*self.YDIM_20m]
        self.Pol20m_ULXY = 'POLYGON(('+str(self.Pol20m_ULX[0])+' '+str(self.Pol20m_ULY[0])+','+str(self.Pol20m_ULX[1])+' '+str(self.Pol20m_ULY[1])+','+str(self.Pol20m_ULX[2])+' '+str(self.Pol20m_ULY[2])+','+str(self.Pol20m_ULX[3])+' '+str(self.Pol20m_ULY[3])+'))'
       
        self.Pol60m_ULX  =  [self.ULX_60m   ,  self.ULX_60m+(self.NC_60m-1)*self.XDIM_60m ,self.ULX_60m+(self.NC_60m-1)*self.XDIM_60m, self.ULX_60m]
        self.Pol60m_ULY  =  [self.ULY_60m   ,  self.ULY_60m , self.ULY_60m+(self.NL_60m-1)*self.YDIM_60m,  self.ULY_60m+(self.NL_60m-1)*self.YDIM_60m]
        self.Pol60m_ULXY = 'POLYGON(('+str(self.Pol60m_ULX[0])+' '+str(self.Pol60m_ULY[0])+','+str(self.Pol60m_ULX[1])+' '+str(self.Pol60m_ULY[1])+','+str(self.Pol60m_ULX[2])+' '+str(self.Pol60m_ULY[2])+','+str(self.Pol60m_ULX[3])+' '+str(self.Pol60m_ULY[3])+'))'



def image_MGRS_info(xml_file):
        import xml.etree.ElementTree as etree
 
        tree_IMG    = etree.parse(xml_file)

        datastripIdentifier = []
        granuleIdentifier   = []
        granules_image_ID   = []
        bands_name          = []
        physical_gains      ={}
        granuleIdentifier
        
        granuleMGRS_ID      = []
        
        for ff in tree_IMG.getiterator():
            
           if ff.tag == 'PHYSICAL_GAINS':
              physical_gains[ff.items()[0][0]+ff.items()[0][1]]=ff.text
             
           if ff.tag == 'Solar_Irradiance_List':
              solar_irradiance  = dict((ig.keys()[0]+ig.items()[0][1], ig.text) for ig in ff )
                   
           if ff.tag == 'Query_Options':
               for ii in range(len(ff[3])):
                   temp = ff[3][ii].text
                   if len(temp)==2:
                       temp=temp[0]+'0'+temp[1]
                       bands_name.append(temp) 
           if ff.tag == 'Product_Organisation':
                for ii in range(len(ff)):
                    temp = ff[ii][0].items()
                    datastripIdentifier.append(temp[0][1])
                    granuleIdentifier.append(temp[2][1])
                    granuleMGRS_ID.append(temp[2][1][-13:-7])
                    list_tmp =[]
            
                    for kk in range(len(ff[ii][0])):
                        list_tmp.append(ff[ii][0][kk].text)
                    granules_image_ID.append(list_tmp)
           if ff.tag == 'Cloud_Coverage_Assessment':
                 Cloud_Coverage_Assessment=ff.text

        info = {'physical_gains'            : physical_gains,
                'solar_irradiance'          : solar_irradiance,
                'bands_name'                : bands_name,
                'datastripIdentifier'       : datastripIdentifier, 
                'granuleIdentifier'         : granuleIdentifier,
                'granuleMGRS_ID'            : granuleMGRS_ID,
                'granules_image_ID'         : granules_image_ID,
                'Cloud_Coverage_Assessment' : Cloud_Coverage_Assessment}
                   
        return info



def entry_info_retrieval(entries):

        # List Inizialization 
        relativeorbitnumber   = []
        platformname          = []
        beginposition         = []
        endposition           = []
        cloudcoverpercentage  = []
        footprint             = []
        footprint2plot        = []
        orbitdirection        = []
        ingestiondate         = []
        uuid_element          = []     
        title_element         = []

        
        info = []
        for entry in range(len(entries)):

            uuid_element.append(  entries[entry].find('{http://www.w3.org/2005/Atom}id').text)
            title_element.append( entries[entry].find('{http://www.w3.org/2005/Atom}title').text)

            for i_entry in range(len(entries[entry])):

                if entries[entry][i_entry].get('name') == 'ingestiondate':
                    ingestiondate.append(entries[entry][i_entry].text)
                if entries[entry][i_entry].get('name') == 'orbitdirection':
                    orbitdirection.append(entries[entry][i_entry].text)
                if entries[entry][i_entry].get('name') == 'relativeorbitnumber':
                    relativeorbitnumber.append(entries[entry][i_entry].text)
                if entries[entry][i_entry].get('name') == 'platformname':
                    platformname.append(entries[entry][i_entry].text)
                if entries[entry][i_entry].get('name') == 'beginposition':
                    beginposition.append(entries[entry][i_entry].text)
                if entries[entry][i_entry].get('name') == 'endposition':
                    endposition.append(entries[entry][i_entry].text)
                if entries[entry][i_entry].get('name') == 'cloudcoverpercentage':
                    cloudcoverpercentage.append(entries[entry][i_entry].text)
                if entries[entry][i_entry].get('name') == 'footprint':
                    footprint.append(entries[entry][i_entry].text)
                    footprint2plot.append(((entries[entry][i_entry].text).replace('POLYGON ((','')).replace('))','').replace(',',' ').split(' '))
        
        Ind_tmp =sorted((e,i) for i,e in enumerate(beginposition))
        
        Ind_order_vec = []
        for entry in range(len(entries)):
            Ind_order_vec.append(Ind_tmp[entry][1])
            
        uuid_element         = [ uuid_element[i]         for i in Ind_order_vec]    
        title_element        = [ title_element[i]        for i in Ind_order_vec]    
        ingestiondate        = [ ingestiondate[i]        for i in Ind_order_vec]    
        orbitdirection       = [ orbitdirection[i]       for i in Ind_order_vec]    
        relativeorbitnumber  = [ relativeorbitnumber[i]  for i in Ind_order_vec]    
        platformname         = [ platformname[i]         for i in Ind_order_vec]    
        beginposition        = [ beginposition[i]        for i in Ind_order_vec]    
        endposition          = [ endposition[i]          for i in Ind_order_vec]    
        footprint            = [ footprint[i]            for i in Ind_order_vec]    
        footprint2plot       = [ footprint2plot[i]       for i in Ind_order_vec]    

        if platformname[0] == 'Sentinel-2':
            
           cloudcoverpercentage = [ cloudcoverpercentage[i] for i in Ind_order_vec]    
       
           info = {'uuid_element'         : uuid_element,
                    'title_element'        : title_element,
                    'ingestiondate'        : ingestiondate,
                    'orbitdirection'       : orbitdirection, 
                    'relativeorbitnumber'  : relativeorbitnumber,
                    'platformname'         : platformname,
                    'beginposition'        : beginposition,
                    'endposition'          : endposition,
                    'cloudcoverpercentage' : cloudcoverpercentage,
                    'footprint'            : footprint,
                    'footprint2plot'       : footprint2plot}
        elif platformname[0] == 'Sentinel-1':
           
           info = {'uuid_element'         : uuid_element,
                   'title_element'        : title_element,
                   'ingestiondate'        : ingestiondate,
                   'orbitdirection'       : orbitdirection, 
                   'relativeorbitnumber'  : relativeorbitnumber,
                   'platformname'         : platformname,
                   'beginposition'        : beginposition,
                   'endposition'          : endposition,
                   'cloudcoverpercentage' : cloudcoverpercentage,
                   'footprint'            : footprint,
                   'footprint2plot'       : footprint2plot}
        return info


def granules_display(destination_QuickLook,granule_info,granuleIdentifier,reference_map = None):
    
        from matplotlib import pylab as plt
        import matplotlib.image as mpimg

        img=mpimg.imread(destination_QuickLook)
        
        Fig_X =10
        Fig_Y =5
        fig, ax = plt.subplots()
        fig.set_size_inches(Fig_X, Fig_Y)
        plt.imshow(img)
        plt.close() 

        fig, ax = plt.subplots()
        fig.set_size_inches(Fig_X, Fig_Y)
        
        for ff in range(len(granuleIdentifier)):
            tmp=granule_info[ff]            

            Pol10m_UL_lon =[]
            Pol10m_UL_lat =[]
            for gg in range(len(tmp.Pol10m_ULX)):
                
                out_tmp = transform_utm_to_wgs84(tmp.Pol10m_ULX[gg],tmp.Pol10m_ULY[gg],int(granuleIdentifier[ff][-12:-10]))
                Pol10m_UL_lon.append(out_tmp[0])
                Pol10m_UL_lat.append(out_tmp[1])
                    
            plt.fill(Pol10m_UL_lon,Pol10m_UL_lat,fill=False)        
            plt.axis('equal')
            Xc =0.8*Pol10m_UL_lon[0]+0.2*Pol10m_UL_lon[1];
            Yc =0.5*Pol10m_UL_lat[0]+0.5*Pol10m_UL_lat[2];
            ax.text(Xc,Yc,'['+str(ff)+']',fontsize = 10)
            
        if reference_map:     
            x_map = []
            y_map = []
            #reference_map = data_storage+'catalunya_WGS84_GEOG.map'
            f = open(reference_map, 'r')
            for line in f:
                line = line.strip()
                if line:
                    x_map.append(float(line.split()[0]))
                    y_map.append(float(line.split()[1]))    
            f.closed
            plt.fill(x_map,y_map,'ro',fill=False)
        
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        plt.show()
        plt.close() 

        
        print " Image's GRANULES LIST "
        
        for ff in range(len(granuleIdentifier)):
            print '['+str(ff)+'] : ' + granuleIdentifier[ff][-13:-7]
         
         
def granules_layout_display(granule_info,granuleIdentifier,reference_map =None,fuse_vec=None,output_im =None, xlim = None, ylim = None):
    
        from matplotlib import pylab as plt

        Fig_X =6
        Fig_Y =4
        
        fig_vec = []
        for hh in fuse_vec:
        
            fig, ax = plt.subplots()
            fig.set_size_inches(Fig_X, Fig_Y)
            plt.axis('equal')

            fig.suptitle('UTM FUSE : ' +  hh, fontsize=12, fontweight='bold')

            for ff in range(len(granuleIdentifier)):
                tmp=granule_info[ff]      

                if tmp.FUSE == hh:
                    Pol10m_UL_lon =[]
                    Pol10m_UL_lat =[]
                    for gg in range(len(tmp.Pol10m_ULX)):
                        
                        out_tmp = transform_utm_to_wgs84(tmp.Pol10m_ULX[gg],tmp.Pol10m_ULY[gg],int(granuleIdentifier[ff][-12:-10]))
                        Pol10m_UL_lon.append(out_tmp[0])
                        Pol10m_UL_lat.append(out_tmp[1])
                            
                    plt.fill(Pol10m_UL_lon,Pol10m_UL_lat,fill=False)        
                    plt.axis('equal')
                    Xc =0.8*Pol10m_UL_lon[0]+0.2*Pol10m_UL_lon[1];
                    Yc =0.5*Pol10m_UL_lat[0]+0.5*Pol10m_UL_lat[2];

                    #ax.text(Xc,Yc,'['+str(ff)+']',fontsize = 10)
                    ax.text(Xc,Yc,'['+ granuleIdentifier[ff][-13:-7] +']',fontsize = 8)
                    
            
                    
            if reference_map:     
                x_map = []
                y_map = []
                #reference_map = data_storage+'catalunya_WGS84_GEOG.map'
                f = open(reference_map, 'r')
                for line in f:
                    line = line.strip()
                    if line:
                        x_map.append(float(line.split()[0]))
                        y_map.append(float(line.split()[1]))    
                f.closed
                plt.fill(x_map,y_map,'ro',fill=False)
            
            ax.set_xlabel('Longitude(WGS84)')
            ax.set_ylabel('Latitude(WGS84)')
            plt.show()
            plt.close() 

            
            if xlim and ylim:
                ax.set_ylim = ylim
                ax.set_xlim = xlim

            fig_vec.append(fig)
                             
                
            for hh in range(len(fig_vec)):
                if output_im:
                    fig_vec[hh].savefig(output_im[hh])  

       
def downloading_block(sentinel_link,destinationpath,sentinel_chk_sum_link=None):
    from pathlib_revised import Path2
    import urllib2
    import os
    import sys

    PATH_MAX_limit = 260;
    
    old_work_dir =os.getcwd()
    os.chdir(os.path.dirname(destinationpath))
    if len(destinationpath)>PATH_MAX_limit:
        LEN_cnd = True
        destinationfile_fin = os.path.basename(destinationpath)
        destinationfile = 'tmp'
        path_tmp = Path2(os.getcwd()+'//tmp')
        path_fin = Path2(os.getcwd()+ "//" +destinationfile_fin)
    else:
        LEN_cnd = False
        destinationfile = os.path.basename(destinationpath)
        path_fin = Path2('error')
    
    
    if sentinel_chk_sum_link:
        while True:
                try:
                    downloadfile_chk = urllib2.urlopen(sentinel_chk_sum_link)
                    check_sum  = downloadfile_chk.read()
                    downloadfile_chk.close()
                    break
                except urllib2.HTTPError, error:
                    print "ERROR: ", error.read()
                except urllib2.URLError, error:
                    print "ERROR: ", error.read()

    while True:
            try:
                downloadfile_QV = urllib2.urlopen(sentinel_link)
                metaQV        = downloadfile_QV.info()
                downloadfile_QV.close()
                fQV_size       = int(metaQV.getheaders("Content-Length")[0])
                loop=1
                break
            except urllib2.HTTPError, error:
                print "ERROR: ", error.read()
            except urllib2.URLError, error:
                print "ERROR: ", error.read()
    
    if os.path.exists(destinationpath) or path_fin.exists():
        if LEN_cnd:
            print destinationfile_fin
            print 'File already downloaded....'
            loop = 0
        else:
            existSizeQV = os.path.getsize(destinationpath)
            if existSizeQV == fQV_size:
                print destinationfile
                print 'File already downloaded....'
                loop = 0
    while loop:
       #Check if file already was downloaded
       if os.path.exists(destinationfile) and not(LEN_cnd):
           existSizeQV = os.path.getsize(destinationfile)

           #Check if file was partially downloaded
           print 'Downloading incompleted, process being resumed...'
           
           try :
               req = urllib2.Request(sentinel_link)
               req.add_header("Range","bytes=%s-" % (existSizeQV))
               
               fQV_size_dl = existSizeQV
               fQV = open(destinationfile, 'ab')
           except:
               fQV_size_dl = 0
               fQV = open(destinationfile, 'wb')
    
       else:
           req = urllib2.Request(sentinel_link)

           fQV_size_dl = 0
           fQV = open(destinationfile, 'wb')
       
       cnt=0
       while True:
           if cnt<4:
               try:
                   downloadfile_QV = urllib2.urlopen(req)
                   break
               except urllib2.HTTPError, error:
                   print "ERROR: ", error.read()
                   cnt+=1
               except urllib2.URLError, error:
                   print "ERROR: ", error.read()
                   cnt+=1
           else:
               fQV_size_dl = 0
               fQV = open(destinationfile, 'wb')
               break

       #Download file and read
       print "Downloading File : "
       if LEN_cnd:
           print destinationfile_fin
       else :
           print LEN_cnd
       print "Files Size[Bytes]: %s" % (fQV_size)
    
    
       block_sz  = 16384

       # Downloading precess is started/resumed   
       while True:
           try:
               buffer = downloadfile_QV.read(block_sz)
               if not buffer:
                   break
           
               fQV_size_dl += len(buffer)
               fQV.write(buffer)
#               i=int(fQV_size_dl * 100. / fQV_size)
#               sys.stdout.write("\r%d%%" % i)

               progress=float(fQV_size_dl)/float(fQV_size)
               title = 'Downloading '
               #print "\r%s: [%s] %.1f%%" % (title, ('#' * int(progress * 50)).ljust(50), progress * 100)
               sys.stdout.write("\r%s: [%s] %.1f%%" % (title, ('#' * int(progress * 50)).ljust(50), progress * 100))
               
               
#               def update_progress(title, progress, fh=sys.stdout):
#    """Printa un progress bar en command-line.
#    Args:
#       title (string): El títol del procés que s'està fent (Ex. Processant)
#       progress (float): Float entre 0 i 1 que indica el percentatge de progrés.
#       fh: File handle. Per defecte sys.stdout
#    """
#    print >>fh, ("\r%s: [%s] %.1f%%" % (title, ('#' * int(progress * 50)).ljust(50), progress * 100)),




               sys.stdout.flush()

           except TypeError:
               break
               
       fQV.close()
       downloadfile_QV.close()
       
       if fQV_size == fQV_size_dl:
           if sentinel_chk_sum_link:
               hexdigest_ = md5sum(destinationfile,block_sz)
                            
               if hexdigest_.upper()==check_sum.upper():
                   print ""                   
                   print "File downloaded correctly!!"
                   loop = 0
                   if LEN_cnd and not(os.path.exists(destinationfile_fin)):
                      
                       Path2(path_tmp).rename(path_fin)
        
               else:
                   print "File downloaded incorrectly!! File will be removed and downloading restarted..."
                   os.remove(destinationfile)
                
           else:     
               print ""                   
               print "File downloaded correctly!!"
               loop = 0
               
               if LEN_cnd and not(os.path.exists(destinationfile_fin)):
                   
                   Path2(path_tmp).rename(path_fin)
               
       else:
          print "Downloaded File incomplete!! Downloading will be resumed" 
          
    print ''
    os.chdir(old_work_dir)
    
def print_red(line):
        
        print "\033[33;1;48m" +line+" \033[0m"  # oh the horror!
        
def print_blue(line):
        
        print "\033[34;1;48m" +line+" \033[0m"  # oh the horror!
        
        
def define_master_envelope(poly_ms,poly_sl,N_im):

    from osgeo import ogr
    
    ms_tmp = poly_ms.GetEnvelope()
    sl_tmp = poly_sl.GetEnvelope()
    
    ms_new = []
    for i_coord in range(len(ms_tmp)):
        ms_new.append((N_im*ms_tmp[i_coord]+sl_tmp[i_coord])/(N_im+1))
    # ms_new = [minX, maxX, minY, maxY] 
    minX =ms_new[0]
    maxX =ms_new[1]
    minY =ms_new[2]
    maxY =ms_new[3]
    
    # Create ring
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(minX, minY)
    ring.AddPoint(maxX, minY)
    ring.AddPoint(maxX, maxY)
    ring.AddPoint(minX, maxY)
    ring.AddPoint(minX, minY)

    # Create polygon
    poly_envelope = ogr.Geometry(ogr.wkbPolygon)
    poly_envelope.AddGeometry(ring)
    
    return poly_envelope

def define_new_master_polygon(poly_ms,poly_sl,N_im):

    from osgeo import ogr
    
    
    
    ms_new = []
    for i_coord in range(len(poly_ms)):
        ms_new.append((N_im*float(poly_ms[i_coord])+float(poly_sl[i_coord]))/(N_im+1))
        
    
    wkt_ms = 'POLYGON (('+ str(ms_new[0]) + ' ' + str(ms_new[1]) + ','  + \
                           str(ms_new[2]) + ' ' + str(ms_new[3]) + ','  + \
                           str(ms_new[4]) + ' ' + str(ms_new[5]) + ','  + \
                           str(ms_new[6]) + ' ' + str(ms_new[7]) + ','  + \
                           str(ms_new[0]) + ' ' + str(ms_new[1]) + '))'  
    
    # Create new MASTER polygon 
    poly_ms     = ogr.CreateGeometryFromWkt(wkt_ms)
    
    return wkt_ms, ms_new


def polygon_sort(ms_coord):

    import numpy as np
    
    ms_lon = np.array(ms_coord[0:7:2])
    ms_lat = np.array(ms_coord[1:8:2])                
    ms_sorted_ind = np.argsort(ms_lon)
    
    ms_lon_ = ms_lon[ms_sorted_ind]
    ms_lat_ = ms_lat[ms_sorted_ind]
    
    if ms_lat_[0]<=ms_lat_[1]:
        DL_lon = ms_lon_[0]
        DL_lat = ms_lat_[0]
        UL_lon = ms_lon_[1]
        UL_lat = ms_lat_[1]
    else:
        DL_lon = ms_lon_[1]
        DL_lat = ms_lat_[1]
        UL_lon = ms_lon_[0]
        UL_lat = ms_lat_[0]
    if ms_lat_[2]<=ms_lat_[3]:
        DR_lon = ms_lon_[2]
        DR_lat = ms_lat_[2]
        UR_lon = ms_lon_[3]
        UR_lat = ms_lat_[3]
    else:
        DR_lon = ms_lon_[3]
        DR_lat = ms_lat_[3]
        UR_lon = ms_lon_[2]
        UR_lat = ms_lat_[2]
    
    ms_coord = [UL_lon,UL_lat,UR_lon,UR_lat,DR_lon,DR_lat,DL_lon,DL_lat,UL_lon,UL_lat]
    
    return ms_coord
    
    
def generate_HTML_S1(list_stacks,Stacks_sorted_ind,html_file,info_entries,O_im_stack,url,reference_map = None,):
    
    from matplotlib import pylab as plt
    import OO_Create_HTML as HTML
    import os
 
    
    im_ref_name = []
    for i_stacks in range(len(list_stacks)):
        im_ref_name.append('stack_im'+str(i_stacks))
    
    
    if reference_map:     
        x_map = []
        y_map = []
        f = open(reference_map, 'r')
        for line in f:
            line = line.strip()
            if line:
                x_map.append(float(line.split()[0]))
                y_map.append(float(line.split()[1]))    
        f.closed
                
            
    
    if os.path.isfile(html_file): 
        os.remove(html_file)
    
    html_fid = HTML.create_HTML(html_file)
    
    HTML.Open_HTML_file(html_fid,'Institut Cartographic i Geològic de Catalunya (ICGC)')
    
    HTML.Open_HTML_paragraph(html_fid)
    HTML.Write_HTML_text_ref(html_fid,'arial','22','#000000','Sentinel2 Collection','PageStart')
    #HTML.Write_HTML_text(html_fid,'arial','22','#000000','Sentinel2 Collection')
    HTML.Close_HTML_paragraph(html_fid)
    
    HTML.Open_HTML_paragraph(html_fid)
    HTML.Close_HTML_paragraph(html_fid)
    
    HTML.Open_HTML_paragraph(html_fid)
    HTML.Write_HTML_text(html_fid,'arial','16','#000000','Number of STACKs found over the INPUT Polygon[Geo - WGS86]: ' + str(len(list_stacks)))
    HTML.Close_HTML_paragraph(html_fid)
    
    HTML.Open_HTML_paragraph(html_fid)
    HTML.Close_HTML_paragraph(html_fid)
    
    HTML.Open_HTML_paragraph(html_fid)
    HTML.Write_HTML_text(html_fid,'arial','14','#000000','List of Available Collections (ordered by STACK Cardinality)')
    HTML.Close_HTML_paragraph(html_fid)
    
    HTML.Open_HTML_paragraph(html_fid)
    for i_stacks in range(len(list_stacks)):
        HTML.Write_HTML_text_link(html_fid,'arial','12','#0000FF','STACK number : ' + str(i_stacks) + ' # of images : '+ str(len(list_stacks[Stacks_sorted_ind[i_stacks]])),im_ref_name[i_stacks])
       
    HTML.Close_HTML_paragraph(html_fid)
    HTML.Open_HTML_paragraph(html_fid)
    HTML.Write_HTML_text(html_fid,'arial','14','#000000','\n')
    HTML.Close_HTML_paragraph(html_fid)
        
        
        
    Im_X_Fprint = '400'  # Quickview Horiz Length [Pixels]
    Im_Y_Fprint = '300'  # Quickview Vert Length [Pixels]
    
    Im_X = '200'  # Quickview Horiz Length [Pixels]
    Im_Y = '150'  # Quickview Vert Length [Pixels]
    
    
    fig_vec = [];
    QL_files_vec  = []
    
    colors_vec = 'rgbcmykr' # get_spaced_colors(len(list_stacks))
    for i_stacks in range(len(list_stacks)):
    
    
        HTML.Open_HTML_paragraph(html_fid)
        
        HTML.Write_HTML_text_ref(html_fid,'arial','14','#000000','STACK : '+ str(i_stacks),im_ref_name[i_stacks])
       
        #HTML.Write_HTML_text(html_fid,'arial','14','#000000','STACK : '+ str(i_stacks))
        HTML.Close_HTML_paragraph(html_fid)
    
        fig, ax = plt.subplots()
        
        fig_vec.append(fig)
        plt.fill(x_map,y_map,'ro',fill=False)
        n_im =len(list_stacks[Stacks_sorted_ind[i_stacks]])
        
        fig.suptitle('Orbit : ' + O_im_stack[Stacks_sorted_ind[i_stacks]] + ' - Stack : ' +str(i_stacks) + ' -  # of images: ' + str(n_im), fontsize=12, fontweight='bold')
    
        for ii in range(n_im) :
            results = [float(i) for i in info_entries['footprint2plot'][list_stacks[Stacks_sorted_ind[i_stacks]][ii]]]
            x =  results[0:len(results)-1:2]
            y =  results[1:len(results):2]
            plt.fill(x,y,fill=False,color=colors_vec[i_stacks%len(colors_vec)])
            plt.axis('equal')
        plt.show()
        plt.close() 

        ax.set_xlabel('LONGITUDE(WGS84)')
        ax.set_ylabel('LATITUDE(WGS84)')
        
        tmp_folder = os.path.dirname(html_file)
        file_im = tmp_folder + '//Stack' + str(i_stacks)+'.jpg'
        fig.savefig(file_im)    
        
        #Write_HTML_figure_ref(fid,image,height,width,name):
        #HTML.Write_HTML_figure_ref(html_fid,'Stack' + str(i_stacks)+'.jpg',Im_Y_Fprint,Im_X_Fprint,im_ref_name[i_stacks])
    
        HTML.Write_HTML_figure(html_fid,'Stack' + str(i_stacks)+'.jpg',Im_Y_Fprint,Im_X_Fprint)
        HTML.Write_HTML_text_link(html_fid,'arial','16','#0000FF','[Stacks List]','PageStart')
    
        HTML.Open_HTML_paragraph(html_fid)
        HTML.Write_HTML_text(html_fid,'arial','14','#000000',' \n')
        HTML.Close_HTML_paragraph(html_fid)
        HTML.Open_HTML_paragraph(html_fid)
        HTML.Write_HTML_text(html_fid,'arial','12','#000000','Adquisitions Preview and Basic Info')
        HTML.Close_HTML_paragraph(html_fid)
            
        print " "        
        print 'STACK : '+ str(i_stacks)
        print " "
        
        QuickLook_files = [];
    
        for ii in range(n_im) :
            entry = list_stacks[Stacks_sorted_ind[i_stacks]][ii]
            
            uuid_element  = info_entries['uuid_element'][entry]   # entries[entry].find('{http://www.w3.org/2005/Atom}id').text
            title_element = info_entries['title_element'][entry]   #entries[entry].find('{http://www.w3.org/2005/Atom}title').text
            tmp_line      = 'Acquisition Date : ' + info_entries['beginposition'][entry] + ' Image : ' + title_element + '.zip'  
            
            
            print '[', ii, ']  ',tmp_line
            
            #sentinel_QL_link      = url+"odata/v1/Products('" + uuid_element + "')/Products('Quicklook')/$value"
            sentinel_QL_link      = url+"odata/v1/Products('" + uuid_element + "')/Products('Quicklook')/$value"
            destination_QuickLook = tmp_folder+'//'+uuid_element+'Quicklook.jpg'
            if not os.path.isfile(destination_QuickLook): 
                downloading_block(sentinel_QL_link,destination_QuickLook)
    
            HTML.Write_HTML_figure(html_fid,uuid_element+'Quicklook.jpg',Im_Y,Im_X)
            
            
            HTML.Open_HTML_paragraph(html_fid)
    
            HTML.Write_HTML_text(html_fid,'arial','10','#000000','Position within Stack : '+'['+ str(ii) + ']  '+ 'Acquisition Date : ' + info_entries['beginposition'][entry])
            HTML.Write_HTML_text(html_fid,'arial','10','#000000','Image Name : ' + title_element + '.zip')
            HTML.Write_HTML_text(html_fid,'arial','10','#000000','Orbit Relative Number : ' + info_entries['relativeorbitnumber'][entry] )
            HTML.Write_HTML_text(html_fid,'arial','10','#000000','Image UUID: ' + uuid_element)
            HTML.Write_HTML_link(html_fid, url+"odata/v1/Products('" + uuid_element + "')/$value")
           
            HTML.Close_HTML_paragraph(html_fid)
            QuickLook_files.append(destination_QuickLook)
        
        QL_files_vec.append(QuickLook_files)   
    
    HTML.Close_HTML_file(html_fid)
    
    os.system('start chrome  ' +html_file)
    
    return QL_files_vec,fig_vec
    
    
def generate_HTML_S2(list_stacks,Stacks_sorted_ind,html_file,info_entries,O_im_stack,url,reference_map = None,):
    
    import xml.etree.ElementTree as etree
    from matplotlib import pylab as plt
    import OO_Create_HTML as HTML
    import os

    im_ref_name = []
    for i_stacks in range(len(list_stacks)):
        im_ref_name.append('stack_im'+str(i_stacks))
    
    if reference_map:  
        map_flag =1
        x_map = []
        y_map = []
        f = open(reference_map, 'r')
        for line in f:
            line = line.strip()
            if line:
                x_map.append(float(line.split()[0]))
                y_map.append(float(line.split()[1]))    
        f.closed
        
    
    if os.path.isfile(html_file): 
        os.remove(html_file)
    
    html_fid = HTML.create_HTML(html_file)
    
    HTML.Open_HTML_file(html_fid,'Institut Cartographic i Geològic de Catalunya (ICGC)')
    
    HTML.Open_HTML_paragraph(html_fid)
    HTML.Write_HTML_text_ref(html_fid,'arial','22','#000000','Sentinel1 Collection','PageStart')
    HTML.Close_HTML_paragraph(html_fid)
    
    HTML.Open_HTML_paragraph(html_fid)
    HTML.Close_HTML_paragraph(html_fid)
    
    HTML.Open_HTML_paragraph(html_fid)
    HTML.Write_HTML_text(html_fid,'arial','16','#000000','Number of STACKs found over the INPUT Polygon[Geo - WGS86]: ' + str(len(list_stacks)))
    HTML.Close_HTML_paragraph(html_fid)
    
    HTML.Open_HTML_paragraph(html_fid)
    HTML.Close_HTML_paragraph(html_fid)
    
    HTML.Open_HTML_paragraph(html_fid)
    HTML.Write_HTML_text(html_fid,'arial','14','#000000','List of Available Collections (ordered by STACK Cardinality)')
    HTML.Close_HTML_paragraph(html_fid)
    
    HTML.Open_HTML_paragraph(html_fid)
    HTML.Write_HTML_text(html_fid,'arial','14','#000000','\n')
    HTML.Close_HTML_paragraph(html_fid)
    
    HTML.Open_HTML_paragraph(html_fid)
    for i_stacks in range(len(list_stacks)):
        
        HTML.Write_HTML_text_link(html_fid,'arial','12','#0000FF','STACK number : ' + str(i_stacks) + ' # of images : '+ str(len(list_stacks[Stacks_sorted_ind[i_stacks]])),im_ref_name[i_stacks])
        
        
        
    Im_X_Fprint = '400'  # Quickview Horiz Length [Pixels]
    Im_Y_Fprint = '300'  # Quickview Vert Length [Pixels]
    
    Im_X = '200'  # Quickview Horiz Length [Pixels]
    Im_Y = '150'  # Quickview Vert Length [Pixels]
    
    
    fig_vec              = []
    QL_files_vec         = []
    XML_files_vec        = []
    XML_image_info_vec   = []
    XML_granule_info_vec = []
    N_fuse_stack_vec     = []
    
    colors_vec = 'rgbcmykr' # get_spaced_colors(len(list_stacks))
    for i_stacks in range(len(list_stacks)):
         
        Ind_stack =Stacks_sorted_ind[i_stacks]

    
        HTML.Open_HTML_paragraph(html_fid)
        HTML.Write_HTML_text_ref(html_fid,'arial','14','#000000','STACK : '+ str(i_stacks),im_ref_name[i_stacks])
        #HTML.Write_HTML_text(html_fid,'arial','14','#000000','STACK : '+ str(i_stacks))
        HTML.Close_HTML_paragraph(html_fid)
    
        fig, ax = plt.subplots()
    
        fig_vec.append(fig)
        if map_flag:
            plt.fill(x_map,y_map,'ro',fill=False)
        n_im =len(list_stacks[Stacks_sorted_ind[i_stacks]])
        
        fig.suptitle('Orbit : ' + O_im_stack[Stacks_sorted_ind[i_stacks]] + ' - Stack Number : '+str(Ind_stack) + ' -  Number of images : ' + str(n_im), fontsize=12, fontweight='bold')
    
        for ii in range(n_im) :
            results = [float(i) for i in info_entries['footprint2plot'][list_stacks[Stacks_sorted_ind[i_stacks]][ii]]]
            x =  results[0:len(results)-1:2]
            y =  results[1:len(results):2]
            plt.fill(x,y,fill=False,color=colors_vec[i_stacks%len(colors_vec)])
            plt.axis('equal')
        plt.show()

        ax.set_xlabel('LONGITUDE(WGS84)')
        ax.set_ylabel('LATITUDE(WGS84)')
        plt.close() 
        
        ylim = ax.get_ylim()
        xlim = ax.get_xlim()
    
        if xlim and ylim:
            ax.set_ylim = ylim
            ax.set_xlim = xlim
        
        tmp_folder = os.path.dirname(html_file)
        file_im = tmp_folder + '//Stack' + str(i_stacks)+'.jpg'
        fig.savefig(file_im)    
        
        
            
        print " "        
        print 'STACK : '+ str(Ind_stack)
        print " "
        
        QuickLook_files  = []
        XML_files        = []
        XML_image_info   = []
        XML_granule_info = []
        
        HTML.Open_HTML_paragraph(html_fid)
        HTML.Write_HTML_text(html_fid,'arial','12','#000000','Adquisitions Preview and Basic Info')
        HTML.Close_HTML_paragraph(html_fid)
            
        for ii in range(n_im-1,-1,-1) :
            entry = list_stacks[Stacks_sorted_ind[i_stacks]][ii]
            
            uuid_element  = info_entries['uuid_element'][entry]   # entries[entry].find('{http://www.w3.org/2005/Atom}id').text
            title_element = info_entries['title_element'][entry]   #entries[entry].find('{http://www.w3.org/2005/Atom}title').text
            tmp_line      = 'Acquisition Date : ' + info_entries['beginposition'][entry] + ' Image : ' + title_element + '.zip'  
            
            
            print '[', ii, ']  ',tmp_line
            print 'Cloud Coverage : ' + info_entries['cloudcoverpercentage'][entry].split('.')[0] +'%'
            
            sentinel_QL_link      = url+"odata/v1/Products('" + uuid_element + "')/Products('Quicklook')/$value"
            destination_QuickLook = tmp_folder+'//'+uuid_element+'Quicklook.jpg'
            
            if not os.path.isfile(destination_QuickLook): 
                downloading_block(sentinel_QL_link,destination_QuickLook)
    
            # Image XML is downloaded for identifiying GRANULES within each image
            sentinel_XML_link  = url+"/odata/v1/Products('" + uuid_element + "')/Nodes('" +title_element +".SAFE')/Nodes('"+ title_element.replace('_PRD_MSIL1C_', '_MTD_SAFL1C_') + ".xml')/$value"  
            S2image_xml        = tmp_folder+'//'+ title_element.replace('_PRD_MSIL1C_', '_MTD_SAFL1C_') + '.xml'
    
            
            if not os.path.isfile(S2image_xml):
                downloading_block(sentinel_XML_link,S2image_xml)
            XML_files.append(S2image_xml)
            info_MGRS = image_MGRS_info(S2image_xml)
    
            #------------------------#
            # GRANULE INFO RETRIEVAL #
            #------------------------#
            if ii==n_im-1:
                print '------------------------------------------------------------'
                print 'Stack : ' + str(i_stacks) + ': Granules XML downloading     '
                print '------------------------------------------------------------'
                im_n_fuse =[]
                
            
                for ff in range(len(info_MGRS['granuleIdentifier'])):
                    
                     sentinel_granule_XML_link  = url+"odata/v1/Products('" + uuid_element + "')/Nodes('" +title_element +".SAFE')/Nodes('GRANULE')/Nodes('" + info_MGRS['granuleIdentifier'][ff]+ "')/Nodes('" + (info_MGRS['granuleIdentifier'][ff][0:-7]).replace('_MSI_L1C_', '_MTD_L1C_') + ".xml')/$value"  
                     baixades_xml = tmp_folder+'//' + (info_MGRS['granuleIdentifier'][ff][0:-7]).replace('_MSI_L1C_', '_MTD_L1C_') + '.xml'
    
                     if not os.path.isfile(baixades_xml):
                         downloading_block(sentinel_granule_XML_link,baixades_xml)
    
                     gran_info_tmp = S2_granule_info(etree.parse(baixades_xml))
                     XML_granule_info.append(gran_info_tmp)
                     
                     if not (gran_info_tmp.FUSE) in im_n_fuse:
                         im_n_fuse.append(gran_info_tmp.FUSE)
                
                
                im_gran_vec =[]
                im_gran_vec_HTML =[]
                
                for ff in range(len(im_n_fuse)):
                    im_gran_vec.append(tmp_folder +'//Stack' + str(i_stacks)+im_n_fuse[ff]+'.jpg')
                    im_gran_vec_HTML.append('Stack' + str(i_stacks)+im_n_fuse[ff]+'.jpg')

                granules_layout_display(XML_granule_info,info_MGRS['granuleIdentifier'],reference_map,im_n_fuse,im_gran_vec,xlim,ylim)
                if len(im_gran_vec)==1:
                    HTML.Write_HTML_2figure(html_fid,'Stack' + str(i_stacks)+'.jpg',Im_Y_Fprint,Im_X_Fprint,im_gran_vec_HTML[0],Im_Y_Fprint,Im_X_Fprint)
         
                elif len(im_gran_vec)==2:
                    HTML.Write_HTML_3figure(html_fid,'Stack' + str(i_stacks)+'.jpg',Im_Y_Fprint,Im_X_Fprint,im_gran_vec_HTML[0],Im_Y_Fprint,Im_X_Fprint,im_gran_vec_HTML[1],Im_Y_Fprint,Im_X_Fprint)
            
                HTML.Write_HTML_text_link(html_fid,'arial','16','#0000FF','[Stacks List]','PageStart')
    
    
        
            HTML.Open_HTML_paragraph(html_fid)  
            HTML.Write_HTML_text(html_fid,'arial','14','#000000',' \n')
            HTML.Close_HTML_paragraph(html_fid)
            
            
            HTML.Write_HTML_figure(html_fid,uuid_element+'Quicklook.jpg',Im_Y,Im_X)
            
                 
            HTML.Open_HTML_paragraph(html_fid)
    
            HTML.Write_HTML_text(html_fid,'arial','10','#000000','Position within Stack : '+'['+ str(ii) + ']  '+ 'Acquisition Date : ' + info_entries['beginposition'][entry])
            HTML.Write_HTML_text(html_fid,'arial','10','#000000','Image Name : ' + title_element + '.zip')
            HTML.Write_HTML_text(html_fid,'arial','10','#000000','Cloud Coverage : ' + info_entries['cloudcoverpercentage'][entry].split('.')[0] +'%')
           
            HTML.Write_HTML_text(html_fid,'arial','10','#000000','Granules MGRS : ' + str(info_MGRS['granuleMGRS_ID']))
            HTML.Write_HTML_text(html_fid,'arial','10','#000000','Image UUID: ' + uuid_element)
            HTML.Write_HTML_link(html_fid, url+"odata/v1/Products('" + uuid_element + "')/$value")
           
            HTML.Close_HTML_paragraph(html_fid)
            QuickLook_files.append(destination_QuickLook)
            XML_image_info.append(info_MGRS)
    
        
        QL_files_vec.append(QuickLook_files)   
        XML_files_vec.append(XML_files)
        XML_image_info_vec.append(XML_image_info)
        XML_granule_info_vec.append(XML_granule_info)
        N_fuse_stack_vec.append(im_n_fuse)
    
    HTML.Close_HTML_file(html_fid)
        
    
    os.system('start chrome  ' +html_file)
    
    return QL_files_vec,XML_files_vec,XML_image_info_vec,XML_granule_info_vec,N_fuse_stack_vec,fig_vec
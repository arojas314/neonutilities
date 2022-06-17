# -*- coding: utf-8 -*-
"""
Originaly created on Mon Apr  8 08:18:00 2019
@author: bhass

Updated by AR 9.20
"""

import requests, urllib, os, re
import pandas as pd
import geopandas as gpd
import glob
import warnings
import shutil
gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
warnings.filterwarnings("ignore")

def list_available_urls(product,site):
    """
    list_available urls lists the api url for a given product and site
    --------
     Inputs:
         product: the data product code (eg. 'DP3.30015.001' - CHM)
         site: the 4-digit NEON site code (eg. 'SRER', 'JORN')
    --------
    Usage:
    --------
    jorn_chm = list_available_urls('DP3.30015.001','JORN')
    """
    r = requests.get("http://data.neonscience.org/api/v0/products/" + product)
    for i in range(len(r.json()['data']['siteCodes'])):
        if site in r.json()['data']['siteCodes'][i]['siteCode']:
            data_urls=r.json()['data']['siteCodes'][i]['availableDataUrls']
    if len(data_urls)==0:
        print('WARNING: no urls found for product ' + product + ' at site ' + site)
    else:
        return data_urls

def list_available_urls_by_year(product,site,year):
    """
    list_available urls_by_year lists the api url for a given product, site, and year
    --------
     Inputs:
         product: the data product code (eg. 'DP3.30015.001' - CHM)
         site: the 4-digit NEON site code (eg. 'SRER', 'JORN')
         year: the year data was collected (eg. '2017','2018','2019')
    --------
    Usage:
    --------
    jorn_chm_2018 = list_available_urls_by_year('DP3.30015.001','JORN','2018')
    """
    r = requests.get("http://data.neonscience.org/api/v0/products/" + product)
    for i in range(len(r.json()['data']['siteCodes'])):
        if site in r.json()['data']['siteCodes'][i]['siteCode']:
            all_data_urls=r.json()['data']['siteCodes'][i]['availableDataUrls']
    data_urls = [url for url in all_data_urls if year in url]
    if len(data_urls)==0:
        print('WARNING: no urls found for product ' + product + ' at site ' + site + ' in year ' + year)
    else:
        return data_urls
    
def download_urls(url_list,download_folder_root,zip=False):
    """
    Download urls from a list
     Inputs:
         url_list: list of urls from the list_available_urls_by_year() function.
         download_folder_root: folder to store downloaded files 
         zip: zip the data; default False
    --------
    Usage:
    --------
    download_urls(url_list,"data",zip=False)
    """

    #downloads data from urls to folder, maintaining month-year folders
    for url in url_list:
        month = url.split('/')[-1]
        download_folder = download_folder_root + month + '/'
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        r=requests.get(url)
        files=r.json()['data']['files']
        for i in range(len(files)):
            if zip==False:
                if '.zip' not in files[i]['name']:
                    print('downloading ' + files[i]['name'] + ' to ' + download_folder)
                    urllib.request.urlretrieve(files[i]['url'],download_folder + files[i]['name'])
            elif zip==True:
                if '.zip' in files[i]['name']:
                    print('downloading ' + files[i]['name'] + ' to ' + download_folder)
                    urllib.request.urlretrieve(files[i]['url'],download_folder + files[i]['name'])

def DownloadFile(url,filename):
    r = requests.get(url)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return 

def download_aop_files(data_product_id,site,year=None,download_folder='./data',poly=None):
    """
    download_aop_files downloads NEON AOP files from the AOP for a given data product, site, and 
    optional year, download folder
    
    Updated to include new features (AR 9.22)
    --------
     Inputs:
         required:
             data_product_id: the data product code (eg. 'DP1.30003.001' - Discrete Lidar)
             site: the 4-digit NEON site code (eg. 'SRER', 'HARV')
         
         optional:
             year: year (eg. '2020'); default (None) is all years
             download_folder: folder to store downloaded files; default (./data) in current directory
             poly: area of interest to filter through AOP tiles (shapefile or geodataframe); default None
    --------
    Usage:
    --------
    download_aop_files('DP1.30003.001','HARV','2019','./data/HARV_2019/lidar','./HARV_poly.shp')
    """
    #get a list of the urls for a given data product, site, and year (if included)
    if year is not None:
        urls = list_available_urls_by_year(data_product_id,site,year)
    else:
        urls = list_available_urls(data_product_id, site)
    print(urls)
    
    #make the download folder if it doesn't already exist
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    # ----------------------if poly param is None, download all
    if poly is None:
        for url in urls:
            r = requests.get(url)
            files = r.json()['data']['files']
            for i in range(len(files)):
                # skip erroneous data
                if files[i]['name'] in [".cpg",".shp",".dbf",".prj",".shx", ".kmz",".kml"]:
                    continue 
                print('downloading ' + files[i]['name'] + ' to ' + download_folder)
                try:
                    DownloadFile(files[i]['url'],os.path.join(download_folder,files[i]['name']))
                except requests.exceptions.RequestException as e:
                    print(e)
    
    # ----------------------Get the AOP shapefiles if a polygon parameter is included
    else:

        shapeUrls = list_available_urls_by_year('DP1.30003.001', site, year)
        # open the poly file
        if type(poly) == gpd.GeoDataFrame:
            gdf_poly = poly
        elif type(poly) == str:
            gdf_poly = gpd.read_file(poly)

        # Create a folder for the shapefiles
        footprintDir = os.path.join(download_folder,"aop_footprints")
        if not os.path.exists(footprintDir):
            os.makedirs(footprintDir)

        for shapeurl in shapeUrls:
            # Request the data to get the file names and urls for download
            r = requests.get(shapeurl)
            files = r.json()['data']['files']

            kmlDict_list = [i for i in files if i['name'][-4:] in ".kml"]

            # Get all the AOP shapefiles (footprints), and check if AOI intersects with footprint
            for fileDict in kmlDict_list:
                # Download data to folder using the DownloadFile function
                if "unclassified" in fileDict['name'] or "boundary" in fileDict['name']:
                    continue
                try:
                    DownloadFile(fileDict['url'],f"{footprintDir}/{fileDict['name']}")
                except requests.exceptions.RequestException as e:
                    print(e)

            # Get a list of the KML file names
            kmlListFromDir = glob.glob(f"{footprintDir}/*.kml")

            for fn in kmlListFromDir:
                # Read in kml footprint file
                gdf_footprint = gpd.read_file(fn, driver='KML')
                # Get GDF in the same CRS
                if gdf_footprint.crs != gdf_poly.crs:
                    gdf_footprint = gdf_footprint.to_crs(epsg=gdf_poly.crs.to_epsg())

                # Check if AOI and footprint intersect
                intersectBool = gdf_poly.intersects(gdf_footprint.convex_hull)
                if intersectBool.values[0] == True:

                    for url in urls:
                        # skip erroneous data
                        r = requests.get(url)
                        files = r.json()['data']['files']
                        for i in range(len(files)):
                            
                            # skip erroneous data
                            if files[i]['name'][-4:] in [".cpg",".shp",".dbf",".prj",".shx", ".kmz",".kml"]:
                                continue
                            if "horz" in files[i]['name'] or "vert" in files[i]['name']:
                                continue

                            # If coords from filenames match, download data
                            substring = re.search("[0-9]{2,}_[0-9]{2,}", os.path.basename(fn)).group(0)
                            if substring in files[i]['name']:
                                try:
                                    DownloadFile(files[i]['url'],f"{os.path.join(download_folder,files[i]['name'])}")
                                except requests.exceptions.RequestException as e:
                                    print(e)

        # Remove the footprints folder
        shutil.rmtree(footprintDir)




            
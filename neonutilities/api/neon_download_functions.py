# -*- coding: utf-8 -*-
"""
Originaly created on Mon Apr  8 08:18:00 2019
@author: bhass

Updated by AR 9.20
"""

import requests, urllib, os, re
from datetime import datetime
import geopandas as gpd
from shapely import geometry

def list_available_urls(product,site):
    """
    Get a list of all available urls for a data product.

    Parameters
    ----------
        product: str
            The data product code (eg. 'DP1.00024.001')
        site: str
            The 4-digit NEON site code (eg. 'HARV', 'WERF')
    
    Usage
    ------
    list_available_urls_by_range('DP1.00024.001, 'HARV')
    """

    data_urls = []
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
    Get a list of urls for a year.

    Parameters
    ----------
        product: str
            The data product code (eg. 'DP1.00024.001')
        site: str
            The 4-digit NEON site code (eg. 'HARV', 'WERF')
        year: str
            Start date in YYYY format (e.g. '2019')
    
    Usage
    ------
    list_available_urls_by_year('DP1.00024.001, 'HARV', '2019')
    """
    r = requests.get("http://data.neonscience.org/api/v0/products/" + product)
    all_data_urls = []
    for i in range(len(r.json()['data']['siteCodes'])):
        if site in r.json()['data']['siteCodes'][i]['siteCode']:
            all_data_urls=r.json()['data']['siteCodes'][i]['availableDataUrls']

    data_urls = [url for url in all_data_urls if year in url]
    if len(data_urls)==0:
        print('WARNING: no urls found for product ' + product + ' at site ' + site + ' in year ' + year)
    else:
        return data_urls

def list_available_urls_by_range(product,site,start,end):

    """
    Get a list of urls for a given date range.

    Parameters
    ----------
        product: str
            The data product code (eg. 'DP1.00024.001')
        site: str
            The 4-digit NEON site code (eg. 'HARV', 'WERF')
        start: str
            Start date in YYYY-MM format (e.g. '2019-01')
        end: str
            End date in YYYY-MM format (e.g. '2020-12')
    
    Usage
    ------
    list_available_urls_by_range('DP1.00024.001, 'HARV', '2019-01', '2020-12')
    """

    dstart = datetime.strptime(start, "%Y-%m")
    dend = datetime.strptime(end, "%Y-%m")

    r = requests.get("http://data.neonscience.org/api/v0/products/" + product)
    
    data_urls = []
    for i in range(len(r.json()['data']['siteCodes'])):
        if site in r.json()['data']['siteCodes'][i]['siteCode']:
            all_data_urls=r.json()['data']['siteCodes'][i]['availableDataUrls']
            allmonths=r.json()['data']['siteCodes'][i]['availableMonths']
            for j in range(len(allmonths)):
                if dstart <= datetime.strptime(allmonths[j], "%Y-%m") <= dend:
                    data_urls.append(all_data_urls[j])

    if len(data_urls)==0:
        print('WARNING: no urls found for product ' + product + ' at site ' + site + ' for given dates.')
    else:
        return data_urls

def download_urls(urls, download_folder_root=None, package=None, zip=False,meta_only=None):
    """
    Download data using a list of urls.

    Parameters
    ----------
        urls: str or list
            List of urls or string of single url. urls can be found by using the list_available_urls_by_range() function.
        download_folder_root: str
            Folder to store downloaded files
        package: str
            Specify which data package to download
            - 'basic'
            - 'expanded'
        zip: bool
            zip the data; default False
    
    Usage
    ------
    download_urls(url_list,"data",package = "basic", zip=False)
    """
    # If url is string, put in list for easier handling
    if isinstance(urls, str):
        urls = [urls]
    
    # Root output folder
    if download_folder_root is None:
        download_folder_root=os.getcwd()
    elif not os.path.exists(download_folder_root):
        os.makedirs(download_folder_root)
    
    ## 
    if meta_only is not None:
        r = requests.get(urls)
        packs_url = r['data']['packages'][0]['url']
        outf = r.json()['data']['siteCode']+ "." + r.json()['data']['productCode']+ "." +r.json()['data']['release'] + "." + r.json()['data']['packages'][0]['type']+"_meta"
        urllib.request.urlretrieve(packs_url, os.path.join(download_folder_root,outf))

    #downloads data from urls to folder, maintaining month-year folders
    for url in urls:
        
        # request data
        r=requests.get(url)
        files=r.json()['data']['files']
        
        if package is not None:
            # Download only basic package (or expanded)
            if zip==True:
                file_packages = r.json()['data']['packages']
                for i in range(len(file_packages)):
                    if file_packages[i]['type'] ==  package:
                        fn_string = r.json()['data']['siteCode'] + "." + r.json()['data']['productCode'] + "." + r.json()['data']['month'] + "-" + package +".zip"
                        outf = os.path.join(download_folder_root, fn_string)
                        urllib.request.urlretrieve(file_packages[i]['url'],outf)
                        
            else:
                fd_string = r.json()['data']['siteCode'] + "." + r.json()['data']['productCode'] + "." + r.json()['data']['month']
                outfd = os.path.join(download_folder_root, fd_string)
                if not os.path.exists(outfd):
                    os.makedirs(outfd)
                                      
                for i in range(len(files)):
                    if package!="expanded":  
                        if 'expanded' not in files[i]['name']:
                            outf = os.path.join(outfd, files[i]['name'])
                            urllib.request.urlretrieve(files[i]['url'],outf)
                        elif package == "expanded":
                            if 'expanded' in files[i]['url']:
                                outf = os.path.join(outfd, files[i]['name'])
                                urllib.request.urlretrieve(files[i]['url'],outf)

                            
        else:
            # Download all files for month
            
            # create month directory
            fn_string = r.json()['data']['siteCode'] + "." + r.json()['data']['productCode'] + "." + r.json()['data']['month']
            download_folder = os.path.join(download_folder_root, fn_string)
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)
            
            for i in range(len(files)):
                if zip==False:
                    if '.zip' not in files[i]['name']:
                        outf = os.path.join(download_folder, files[i]['name'])
                        urllib.request.urlretrieve(files[i]['url'],outf)
                elif zip==True:
                    if '.zip' in files[i]['name']:
                        outf = os.path.join(download_folder, files[i]['name'])
                        urllib.request.urlretrieve(files[i]['url'],outf)



def download_data(product, site, start=None, end=None,
                year=None, download_folder=None,
                package=None, zip=False, meta_only=None):

    """
    Download data from a given data product 

    Parameters
    ----------
    product: str
        The data product code (eg. 'DP1.00024.001')
    site: str
        The 4-digit NEON site code (eg. 'HARV', 'WERF')
    start: str, optional
        Start date in YYYY-MM format (e.g. '2019-01')
        Downloads entire month worth of data. Use with end parameter to download data from a range
    end: str, optional
        End date in YYYY-MM format (e.g. '2020-12')
        Used in conjunction with start parameter to download a range worth of available data
    year: str, optional
        Year in YYYY format (e.g. '2019')
        Downloads entire year worth of data
    download_folder: str
        Folder to store downloaded files. If none is given, data is downloaded to current directory
    package: str, optional
        Specify either 'basic' or 'expanded' package. Downloaded as zipped folder.
    
    Notes
    -----
    If no year or start parameter is given, all available data will be downloaded for all years.
    It is recommended to include date parameters.
    To download single month worth of data, only use the start parameter.

    Examples
    --------
    >>> import neonutilities as nu
    >>> nu.download_data('DP1.00024.001', "HARV", start="2019-01", end="2019-02", download_folder_root="./data", package="basic")
    """
    
    # Get urls
    if year==None:
        if start==None:
            # urls for all data
            urls = list_available_urls(product,site)
        else:
            # urls for all data in date range
            if end==None:
                # Only start param given, download month
                urls = list_available_urls_by_range(product,site,start,start)
            else:
                urls = list_available_urls_by_range(product,site,start,end)
    else:
        # urls for all data in year
        urls = list_available_urls_by_year(product,site,year)
        
    if urls is None:
        print("No data available in time period.")
        return 1
    
    # Download data from urls
    download_urls(urls, download_folder, package=package, zip=False,meta_only=None)


# Utility function for AOP download
def DownloadFile(url,filename):
    r = requests.get(url)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return 

def download_aop_files(data_product_id,site,year=None,download_folder='./data',poly=None, download_all=False):
    """
    Get NEON AOP data.

    Parameters
    ----------
    data_product_id: str
        The data product code (eg. 'DP1.30003.001' - Discrete Lidar)
    site: str
        the 4-digit NEON site code (eg. 'HARV', 'WERF')
    year: str, optional
        Year (eg. '2020'); default (None) is all years
    download_folder: str, optional
        Folder to store downloaded files; default (./data) in current directory
    poly: str or GeoDataFrame, optional
        Area of interest to filter through AOP tiles (shapefile or geodataframe); default None
        (polygon needs to be in proper UTM for site!)

    Notes
    -----
    Currently, spatial subsetting only works on mosaiced files. This generally refers to discrete return lidar and level 3 spectrometer products.

    Examples
    --------
    >>> import neonutilities as nu
    >>> nu.download_aop_files('DP1.30003.001','HARV','2019','./data/HARV_2019/lidar','./HARV_poly.shp')
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
        
        if download_all is True:
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
        else:
            print("Please include polygon, or set download_all parameter to True.")
            return 1
    
    # ----------------------Get the AOP UL coords and create polygons for spatial filtering if polygon is included
    else:

        # open the poly file
        if type(poly) == gpd.GeoDataFrame:
            gdf_poly = poly
        elif type(poly) == str:
            gdf_poly = gpd.read_file(poly)
            
        for url in urls:
            r = requests.get(url)
            files = r.json()['data']['files']
            # Loop through each file
            for i in range(len(files)):
                filename = files[i]['name']
                # skip erroneous data
                if filename[-4:] in [".cpg",".shp",".dbf",".prj",".shx", ".kmz",".kml"]:
                    continue
                if "horz" in filename or "vert" in filename:
                    continue
                # Get file coords
                try:
                    coords = re.findall("[0-9]{6}_[0-9]{7}", filename)[0].split("_")
                except:
                    # Not a file with utm coords
                    continue
                # Get lower left coords
                x_coord_left = int(coords[0])
                y_coord_bottom = int(coords[1])
                # Get upper right coords
                x_coord_right = x_coord_left + 1000
                y_coord_top = y_coord_bottom + 1000
                # create a shapely polygon
                poly = geometry.Polygon([[x_coord_left, y_coord_bottom], [x_coord_left, y_coord_top],
                                        [x_coord_right,y_coord_top], [x_coord_right, y_coord_bottom]])
                # Check for intersection, if so, download data
                if gdf_poly.intersects(poly).any():
                    try:
                        DownloadFile(files[i]['url'],f"{os.path.join(download_folder,filename)}")
                    except requests.exceptions.RequestException as e:
                        print(e)


## Version 4 whitebox from neonUtilities_dev
import numpy as np
import numpy.lib.recfunctions as rfn
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
cur_wd = os.getcwd()
import sys
from shapely import geometry
from pyproj import CRS
import glob
import shutil
import seaborn as sns
import math
from random import randrange
from datetime import timedelta
import seaborn as sns
sns.set() # for pretty plotting

from whitebox import whitebox_tools
# Set the whitebox tools to current directory
wbt = whitebox_tools.WhiteboxTools()
wbt.set_verbose_mode(False)
# Change back to current working directory
os.chdir(cur_wd)

    

# ---------------------------------------READ METADATA---------------- #

# Initialize the dictinoaries contaiing the latlon and towerheights and number of levels

# latlon_dict has the sitename_id as the key, and the associated value is a tuple of (lat,lon)
latlon_dict = {'BART': (44.063889, -71.287375), 'HARV': (42.53691, -72.17265), 'HOPB': (42.471941, -72.329526), 'BLAN': (39.033698, -78.041788),
 'LEWI': (39.095637, -77.983216), 'POSE': (38.89431, -78.147258), 'SCBI': (38.892925, -78.139494), 'SERC': (38.890131, -76.560014),
 'BARC': (29.675982, -82.008414), 'DSNY': (28.12505, -81.43619), 'FLNT': (31.185424, -84.437403), 'JERC': (31.194839, -84.468623),
 'OSBS': (29.689282, -81.993431), 'SUGG': (29.68778, -82.017745), 'CUPE': (18.11352, -66.98676), 'GUAN': (17.96955, -66.8687),
 'GUIL': (18.17406, -66.79868), 'LAJA': (18.021261, -67.076889), 'CRAM': (46.209675, -89.473688), 'LIRO': (45.998269, -89.704767),
 'STEI': (45.50894, -89.58637), 'TREE': (45.49369, -89.58571), 'UNDE': (46.23391, -89.537254), 'KING': (39.105061, -96.603829),
 'KONA': (39.110446, -96.612935), 'KONZ': (39.100774, -96.563075), 'MCDI': (38.945861, -96.443022), 'UKFS': (39.040431, -95.19215),
 'GRSM': (35.68896, -83.50195), 'LECO': (35.690428, -83.50379), 'MLBS': (37.378314, -80.524847), 'ORNL': (35.964128, -84.282588),
 'WALK': (35.957378, -84.279251), 'BLWA': (32.541529, -87.798151), 'DELA': (32.541727, -87.803877), 'LENO': (31.853861, -88.161181),
 'MAYF': (32.960365, -87.407688), 'TALL': (32.95047, -87.393259), 'TOMB': (31.853431, -88.158872), 'DCFS': (47.16165, -99.10656),
 'NOGP': (46.76972, -100.91535), 'PRLA': (47.15909, -99.11388), 'PRPO': (47.129839, -99.253147), 'WOOD': (47.1282, -99.241334),
 'ARIK': (39.758206, -102.44715), 'CPER': (40.815536, -104.74559), 'RMNP': (40.275903, -105.54596), 'STER': (40.461894, -103.02929),
 'BLUE': (34.444218, -96.624201), 'CLBJ': (33.40123, -97.57), 'OAES': (35.410599, -99.058779), 'PRIN': (33.378517, -97.782312),
 'BLDE': (44.95011, -110.58715), 'YELL': (44.95348, -110.53914), 'COMO': (40.034962, -105.54416), 'MOAB': (38.248283, -109.38827),
 'NIWO': (40.05425, -105.58237), 'WLOU': (39.891366, -105.9154), 'JORN': (32.590694, -106.84254), 'SRER': (31.91068, -110.83549),
 'SYCA': (33.750993, -111.50809), 'ONAQ': (40.177599, -112.45245), 'REDB': (40.783934, -111.79789), 'ABBY': (45.762439, -122.33032),
 'MART': (45.790835, -121.93379), 'MCRA': (44.259598, -122.16555), 'WREF': (45.82049, -121.95191), 'BIGC': (37.059719, -119.25755),
 'SJER': (37.10878, -119.73228), 'SOAP': (37.03337, -119.26219), 'TEAK': (37.00583, -119.00602), 'TECR': (36.955931, -119.02736),
 'BARR': (71.28241, -156.61936), 'OKSR': (68.669753, -149.14302), 'TOOK': (68.630692, -149.61064), 'TOOL': (68.66109, -149.37047),
 'BONA': (65.15401, -147.50258), 'CARI': (65.153224, -147.50397), 'DEJU': (63.88112, -145.75136),
 'HEAL': (63.875798, -149.21335), 'PUUM': (19.55309, -155.31731)}

# toewr_dict has the sitename_id as the key, and the associated value is a tuple of the (tower height, number of levels)
tower_dict = {'ABBY': (19, 5, 365),
 'BARR': (9, 4, 4),
 'BART': (35, 6, 274),
 'BLAN': (8, 4, 183),
 'BONA': (19, 5, 230),
 'CLBJ': (22, 5, 272),
 'DEJU': (22, 5, 517),
 'DELA': (42, 6, 25),
 'GRSM': (45, 6, 575),
 'GUAN': (23, 5, 125),
 'HARV': (39, 6, 348),
 'JERC': (42, 6, 47),
 'LENO': (47, 6, 13),
 'MLBS': (29, 6, 1170),
 'OSBS': (35, 6, 46),
 'PUUM': (32, 6, 1685),
 'RMNP': (25, 5, 2742),
 'SCBI': (52, 6, 352),
 'SERC': (62, 6, 33),
 'SJER': (39, 6, 400),
 'SOAP': (52, 6, 1210),
 'SRER': (8, 4, 997),
 'STEI': (22, 6, 476),
 'TALL': (35, 5, 166),
 'TEAK': (59, 7, 2149),
 'TREE': (36, 6, 467),
 'UKFS': (35, 6, 322),
 'UNDE': (39, 6, 521),
 'WREF': (74, 8, 351),
 'YELL': (18, 5, 2133)}

 # PAR sensor information in dictionary as tuple (lat,lon,elev,zOffset for each sensor)
par_sp_dict = {'BART': (44.063889, -71.287375, 274.05, [0.73, 3.11, 16.13, 19.83, 26.11, 35.59]), 'HARV': (42.53691, -72.17265, 348.13, [0.36, 5.13, 16.13, 23.63, 29.37, 39.09]), 'HOPB': (42.472, -72.3306, 211.48, []), 'BLAN': (39.060272, -78.071633, 182.71, [0.73, 2.3, 4.31, 8.65]), 'LEWI': (39.094663, -77.981746, 126.97, []), 'POSE': (38.894329, -78.147092, 277.19, []), 'SCBI': (38.892925, -78.139494, 352.43, [0.21, 6.06, 22.87, 32.36, 
36.31, 51.72]), 'SERC': (38.890131, -76.560014, 32.53, [0.9, 4.44, 19.45, 35.83, 41.33, 61.8]), 'BARC': (29.67696, -82.009789, 27.41, []), 'DSNY': (28.125053, -81.436193, 20.33, [0.35, 2.15, 4.31, 8.54]), 'FLNT': (31.18476, -84.439248, 33.26, []), 'JERC': (31.194846, -84.468629, 46.65, [0.32, 6.15, 15.26, 22.65, 28.67, 
42.44]), 'OSBS': (29.689289, -81.993431, 46.03, [0.87, 2.43, 9.17, 15.04, 25.14, 35.57]), 'SUGG': (29.688413, -82.013638, 35.07, []), 'CUPE': (18.108677, -66.984942, 173.97, []), 'GUAN': (17.969511, -66.868664, 125.32, [0.21, 3.56, 6.93, 12.28, 22.96]), 'GUIL': (18.17465, -66.797528, 559.17, []), 'LAJA': (18.021261, -67.076889, 16.44, [0.24, 2.07, 4.17, 8.54]), 'CRAM': (46.211279, -89.475738, 514.05, []), 'LIRO': (46.000952, -89.704038, 495.9, []), 'STEI': (45.50895, -89.58636, 475.73, [0.9, 5.06, 8.42, 12.57, 15.93, 22.4]), 'TREE': (45.493703, -89.58571, 466.57, [0.86, 2.69, 10.25, 23.67, 27.02, 35.9]), 'UNDE': (46.23391, -89.537254, 520.97, [0.87, 16.07, 16.07, 23.5, 26.89, 38.66]), 'KING': (39.105157, -96.604011, 327.65, []), 'KONA': (39.110452, -96.612942, 323.29, [0.28, 1.33, 4.13, 8.35]), 'KONZ': (39.100781, -96.563083, 414.43, [0.27, 1.32, 4.16, 8.37]), 'MCDI': (38.94797, -96.4427, 383.59, []), 'UKFS': (39.040431, -95.19215, 321.58, [0.86, 1.69, 8.53, 19.58, 24.77, 35.71]), 'GRSM': (35.689114, -83.501933, 575.4, [0.36, 8.08, 19.8, 31.54, 36.56, 45.84]), 'LECO': (35.689286, -83.503267, 559.46, []), 'MLBS': (37.378306, -80.524836, 1169.67, [0.19, 3.46, 11.93, 19.54, 23.58, 29.03]), 'ORNL': (35.964135, -84.282592, 343.79, [0.85, 6.66, 16.6, 25.95, 31.95, 39.01]), 'WALK': (35.958666, -84.279345, 266.74, [3.05]), 'DELA': (32.541733, -87.803883, 25.01, [0.89, 5.13, 19.24, 33.07, 38.16, 41.97]), 'LENO': (31.85386, -88.16118, 13.25, [0.28, 3.16, 20.08, 36.68, 42.85, 47.09]), 'MAYF': (32.960404, -87.407571, 73.54, []), 'TALL': (32.950461, -87.393269, 166.19, [0.3, 1.78, 21.89, 28.54, 35.64]), 'DCFS': (47.161658, -99.106569, 575.3, [0.29, 1.52, 4.34, 8.58]), 'NOGP': (46.769727, -100.91536, 588.63, [0.89, 2.03, 4.21, 8.39]), 'PRLA': (47.160181, -99.11319, 567.96, []), 'PRPO': (47.129671, -99.25059, 592.44, []), 'WOOD': (47.128223, -99.241321, 590.87, [0.27, 1.52, 3.09, 8.53]), 'ARIK': (39.756546, 
-102.450966, 1191.8, []), 'CPER': (40.815538, -104.74559, 1653.92, [0.32, 1.77, 3.94, 8.41]), 'RMNP': (40.275903, -105.545955, 2741.57, [0.89, 4.87, 11.16, 16.23, 25.28]), 'STER': (40.461927, -103.02929, 1364.63, [0.25, 2.46, 4.94, 8.42]), 'BLUE': (34.442398, -96.624037, 290.38, []), 'CLBJ': (33.401231, -97.570033, 272.27, [0.31, 3.68, 11.63, 15.53, 22.49]), 'OAES': (35.4106, -99.058779, 518.94, [0.26, 2.05, 4.22, 8.44]), 'PRIN': (33.377189, -97.781746, 259.49, []), 'BLDE': (44.951368, -110.588459, 2030.41, []), 'YELL': (44.953477, -110.539165, 2132.57, [0.92, 4.63, 8.76, 12.65, 18.03]), 'COMO': (40.035097, -105.544602, 3026.89, []), 
'MOAB': (38.248341, -109.388256, 1798.84, [0.76, 2.55, 2.55, 8.44]), 'NIWO': (40.054269, -105.58238, 3489.99, [0.52, 1.37, 4.37, 8.41]), 'WLOU': (39.891508, -105.914674, 2918.26, []), 'JORN': (32.590694, -106.842542, 1323.55, [0.71, 2.11, 4.28, 8.49]), 'SRER': (31.910711, -110.83547, 997.48, [0.84, 2.14, 4.48, 8.25]), 'SYCA': (33.752705, -111.508696, 655.13, []), 'ONAQ': (40.177599, -112.452429, 1662.39, [0.81, 2.63, 4.65, 8.65]), 'REDB': (40.78237, -111.80589, 1715.91, []), 'ABBY': (45.762439, -122.330317, 364.55, [0.83, 5.08, 10.05, 13.33, 18.55]), 'MART': (45.79168, -121.931853, 341.54, []), 'MCRA': (44.258705, -122.165893, 867.32, []), 'WREF': (45.820486, -121.951967, 351.26, [0.33, 12.1, 23.91, 35.81, 41.7, 53.54, 59.44, 74.19]), 'BIGC': (37.057195, -119.254928, 1131.24, []), 'SJER': (37.108717, -119.732242, 399.84, [0.22, 1.54, 5.42, 19.72, 25.54, 39.42]), 'SOAP': (37.0334, -119.262197, 1209.89, [0.29, 5.14, 11.79, 19.27, 28.61, 52.45]), 'TEAK': (37.005842, -119.006039, 2149.26, [0.9, 3.42, 10.11, 18.64, 26.85, 32.71, 59.17]), 'TECR': (36.954665, -119.023774, 2012.65, []), 'BARR': (71.282425, -156.619319, 4.47, [0.8, 2.65, 4.73, 8.92]), 'OKSR': (68.669947, -149.142357, 768.58, []), 'TOOK': (68.630443, -149.586952, 729.1, []), 'TOOL': (68.66109, -149.37047, 832.06, [0.27, 1.85, 3.36, 8.96]), 'BONA': (65.154044, -147.502561, 230.5, [0.86, 3.44, 5.78, 10.9, 19.37]), 'CARI': (65.153232, -147.503393, 229.05, []), 'DEJU': (63.881125, -145.751333, 517.4, [0.79, 2.58, 6.6, 13.47, 22.33]), 'HEAL': (63.875701, -149.21334, 677.12, [0.78, 2.71, 5.13, 8.8]), 'PUUM': (19.553144, -155.317242, 1689.66, [0.93, 5.04, 12.26, 20.51, 25.16, 32.42])}

# -------------------------DEFINE THE CLASS STRUCTURE FOR LIDAR PAR DATA------------------------- #
class GapDs:


    """This is a data structure that processes discrete lidar data from NEON using a point number density (PND)
    approach to get gap probability and foliage profile.
    
    :param name: name of object
    :type name: str
    :param height: height in meters
    :type height: array
    :param thetaL: Angle of lidar (in degrees)
    :type thetaL: float
    :param gap: gap probability profile
    :type gap: array
    :param accumFoliage: accumulated foliage profile
    :type accumFoliage: array
    :param foliageDensity: foliage density profile
    :type foliageDensity: array
    :param ptDensity: point density profile
    :type ptDensity: array
    
    """

    # initialize the object with values
    def __init__(self, gap=None, thetaL=None, height=None, name=None):
        if gap is not None:
            # if user initializes with gf values
            if not isinstance(gap, np.ndarray):
                gf = np.array(gap) # convert list to numpy if not already
            if not isinstance(height, np.ndarray):
                height = np.array(height) # convert list to numpy if not already
            # if the user passes the gf, get foliage density and accum profile
            vert_gf_arr_zero_masked = np.array(gf)
            vert_gf_arr_zero_masked[vert_gf_arr_zero_masked == 0] = np.nan
            accum_foliage = -1 * np.log(vert_gf_arr_zero_masked)
            foliage_dens_prof = np.absolute(np.diff(accum_foliage, axis=0))
            self.accumFoliage = accum_foliage
            self.foliageDensity = foliage_dens_prof
        
        self.gap = gap
        self.thetaL = thetaL # value should be converted to radians in analysis
        self.height = height
        self.name = name
        
    def par_direct_trans(self, szn):

        """Get the PAR transmission profile at a given solar zenith (in degrees)

        :param szn: xolar zenith (in degrees)
        :type szn: float

        :return: returns the transmission profile at the given solar zenith
        :rtype: array

        """
        # print(f"GF is {self.gf} and {var} will be calculated...")
        ## Calculate the par transmission using the lidar GF values
        # PAR_transmission = exp(1 * cos(thetaL)/cos(szn) * log(gf))
        
        # # big gamma calculation ?? assume 1 ??
        # b_r_const = 1.8
        # big_gamma = ((1 + (b_r_const**2) * (tan(row['sun_alt_rad'])**2)) / (1+ tan(row['sun_alt_rad'])**2))**(1/2)
        
        szn_rad = szn * (np.pi/180)
        try:
            thetaL_rad = self.thetaL * (np.pi/180)
            gf_zero_masked = self.gap.copy() # mask out zero values for calculation
            gf_zero_masked[gf_zero_masked == 0] = np.nan
            log_gf = np.log(gf_zero_masked)
            par_transmission = np.exp(1 * (np.cos(thetaL_rad) / np.cos(szn_rad)) * log_gf)
        except:
            print("No values for gap fraction. Make sure to pass the gap, thetaL, and heights attributes, or calculate it using the las_gf_from_dir")
        
        return par_transmission

    
    def par_absorption(self, szn):

        """Get the normalized PAR absorption profile at a given solar zenith (in degrees)

        :param szn: xolar zenith (in degrees)
        :type szn: float

        :return: returns the absorption profile at the given solar zenith
        :rtype: array

        """
        # Calculate PAR absorption and normalize
        szn_rad = szn * (np.pi/180)
        try:
            thetaL_rad = self.thetaL * (np.pi/180)
            gf_zero_masked = self.gap # mask out zero values for calculation
            gf_zero_masked[gf_zero_masked == 0] = np.nan
            log_gf = np.log(gf_zero_masked)
            gap_transmission = np.exp(1 * (np.cos(thetaL_rad) / np.cos(szn_rad)) * log_gf)
        except:
            print("No values for gap fraction. Make sure to pass the gap, thetaL, and heights attributes, or calculate it using the las_gf_from_dir")
        
        # calculate absorption (difference between two intervals)
        # Calculate the n-th discrete difference along the given axis, and get the absolute value
        par_absorp = np.absolute(np.diff(gap_transmission, axis=0, prepend=gap_transmission[0]))
        par_absorp = par_absorp / (np.absolute(np.diff(self.height, axis=0,prepend=self.height[0])))
        par_absorp[0] = np.nan
        return par_absorp
        
    def plot_data(self, x, y, xlab=None, ylab=None, output=None):
        # user needs to pass the self.attribute (e.g. LasParStruct().par_trans(30))
        # initialize a plot
        fig, ax = plt.subplots(figsize=(8,8))
        
        ax.plot(x,y)
        ax.set_xlabel(xlab)
        ax.set_ylabel(ylab)
        if output is not None:
            if output.endswith(".png"):
                fig.savefig(output)
            fig.savefig(f"{output}.png")
        plt.show()
        
    def gap_from_las_dir(self, directory, aoi, buffer=None, output=None, use_tower_height=False, dzVal=1.5):


        """Reads discrete lidar data (in .las format), calculates gap probability and saves data to attributes.
        Can read a directory of many lidar files, extracts the files where points fall within the area of interest (aoi),
        and then merges all files to filter for points that fill within the aoi.

        :param directory: path to directory containing discrete lidar files (.las format)
        :type directory: str
        :param aoi: list containing point coordinate [lat,lon] or a string with the directory path containing a shapefile
        :type aoi: list or str
        :param buffer: distance from point coordinate in aoi (used if aoi is a list)
        :type buffer: float or int, optional
        :param output: option to create folder and save filtered lidar files and other ancillary data
        :type output: str, optional
        :param use_tower_height: use NEON flux tower heights as the vertical resolution for calculating gap, etc. defaults to False
        :type use_tower_height: bool, optional
        :param dzVal: vertical height resolution if use_height_tower is set to false, defaults to 1.5
        :type dzVal: float, optional

        :return: gap probability, foliage profile, point density profile, and other lidar metrics saved to object
        :rtype: multiple data types

        """


        ## directory: path/to/directory
        ## lat: latitude
        ## lon: longitude
        ## buffer: search for all lidar returns within a specified distance from the lat lon (in meters)

        # ------------SET ARGUMENTS TO VARIABLES------------ #
        # Get all the arguments into variables
        las_dir = directory # might have to be an absolute path

        buffer_dist = buffer
        # Save the output to a variable
        output_dir = output
        if output is None:
            # if the output was empty, create a random file name, and dont forget to delete the output_dir later!
            output_dir = f"temp_from_NU{randrange(100, 500)}_{randrange(50, 500)}"


        # ------------SET UP WORKSPACE------------ #
        import pathlib
        # Set up the temporary output folders
        temp_directory = os.path.abspath(os.path.join(pathlib.Path().resolve(), f"./temp_outputNU"))
        # set the final output file
        out_directory = os.path.abspath(os.path.join(pathlib.Path().resolve(),  f"./{output_dir}"))

        # Handling directories
        if os.path.isdir(temp_directory)==True:
            shutil.rmtree(temp_directory)
        # make the temporary directory
        os.makedirs(temp_directory)

        if os.path.isdir(out_directory)==True:
            print(f"There is already an output folder named '{out_directory}' in the current working directory.\nExiting...")
            shutil.rmtree(temp_directory)
            sys.exit()
        else:
            os.makedirs(out_directory)
        
        if isinstance(aoi, list) and len(aoi)==2:
            gdf_aoi = latlonToUTMgpd(aoi[0],aoi[1]) # returns a geodataframe with point shape in the proper UTM zone

            # First, get the polygon for filtering las tiles, which needs to be larger than 25 meter plot polygon
            gdf_poly_for_filter = gdf_aoi.copy()
            gdf_poly_for_filter['geometry'] = gdf_poly_for_filter.buffer(750)

            # buffer for the 25m plot
            gdf_aoi['geometry'] = gdf_aoi.buffer(buffer_dist) # pass the argument buffer_dist

            ## EXPORT THE CIRCULAR BUFFER AROUND POINT TO SHAPEFILE
            gdf_poly_for_filter.to_file(f"{temp_directory}/aoi_poly_for_search.shp") # removing this folder at end to clean space

            # Save the 25m buffer around location to both the output folder and current working directory
            gdf_aoi.to_file(f"{out_directory}/aoi_poly.shp")

            shapefileForLasFilter = f"{temp_directory}/aoi_poly_for_search.shp"
            shapefileAOI = f"{out_directory}/aoi_poly.shp"
            
        elif isinstance(aoi, str) and aoi.endswith(".shp"):

            gdf_aoi = gpd.read_file(aoi)
            gdf_aoi['geometry'] = gdf_aoi.buffer(500)
            gdf_aoi.to_file(f"{temp_directory}/aoi_poly_for_search.shp")
            shapefileForLasFilter = f"{temp_directory}/aoi_poly_for_search.shp"
            shapefileAOI = aoi
            

        # ------------SELECTING LIDAR TILES AND CLIPPING TO POLYGON------------ #

        ## Select LiDAR tiles by the POI
        wbt.select_tiles_by_polygon(
            indir=las_dir, 
            outdir=temp_directory, 
            polygons=shapefileForLasFilter
        )

        if len(glob.glob(f"{temp_directory}/*.las")) > 1:
            # Merge the lidar tiles that were selected in the polygon
            lidarFilesToJoin = glob.glob(f"{temp_directory}/*.las")
            wbt.lidar_join(
                inputs = ", ".join(lidarFilesToJoin), 
                output = f"{temp_directory}/lidarMerged.las"
            )

            # clip lidar to polygon (harvard polot AOI)
            wbt.clip_lidar_to_polygon(
                i= f"{temp_directory}/lidarMerged.las", 
                polygons = shapefileAOI,
                output = f"{out_directory}/lidarClip.las"
            )

        elif len(glob.glob(f"{temp_directory}/*.las")) == 1:
            # clip lidar to polygon (harvard polot AOI)
            wbt.clip_lidar_to_polygon(
                i= f"{temp_directory}/*.las", 
                polygons = shapefileAOI,
                output = f"{out_directory}/lidarClip.las"
            )

        elif len(glob.glob(f"{temp_directory}/*.las")) == 0:
            print("No LiDAR files available in selected area. Check the coordinate inputs provided.")

        # lets try the wb lasground tools to get ground and height above ground
        # Classify ground (2) and non-ground points (1)
        wbt.lidar_ground_point_filter(
            f"{out_directory}/lidarClip.las", 
            f"{temp_directory}/lidarClip_ground.las", 
            radius=5.0, 
            min_neighbours=8, 
            slope_threshold=45.0, 
            height_threshold=1.0, 
            classify=True, 
            slope_norm=True, 
            height_above_ground=False
        )

        # Normalize to height above ground
        wbt.height_above_ground(
            i=f"{temp_directory}/lidarClip_ground.las", 
            output=f"{out_directory}/lidarClip_classified.las"
        )

        ## No noise removal performed (AR 9.24)

        # ------------CONVERTING LAS TO ASCII FOR ANALYSIS------------ #
        ## Convert the las file to an ascii
        wbt.las_to_ascii(
            inputs=f"{out_directory}/lidarClip_classified.las"
        )

        # ------------GAP FRACTION ANALYSIS------------ #

        # Open the LiDAR ASCII file and the polygon for the buffer area
        df_lidarTotal = pd.read_csv(f"{out_directory}/lidarClip_classified.csv")
        # df_lidarTotal = df_lidarTotal.loc[(df_lidarTotal['Z']<=0) | (df_lidarTotal['Z']>=1.0)].copy().reset_index(drop=True)

        ## FUNCTION FOR CALCULATING GF
        def innerFunction_lidarGF(las_df): # pass the df_lidarTotal df as the las_df
            
        #     def remove_outliers_DBSCAN(df,eps,min_samples):
        #         # DBSCN to remove outliers
        #         outlier_detection = DBSCAN(eps = eps, min_samples = min_samples)
        #         clusters = outlier_detection.fit_predict(df.values)
        #         data = pd.DataFrame()
        #         data['cluster'] = clusters
        #         return data['cluster']

        #     ## XYZ dbscan to remove real outliers (return pulses from atmosphere, far belowe ground, etc)
        #     # Some sites should not remove any outliers, like DEJU
        #     clusters=remove_outliers_DBSCAN((las_df[["X","Y",'Z']]),5.0,5)
        #     # clusters.value_counts().sort_values(ascending=False)

        #     # get the indices of the outliers
        #     df_cluster=pd.DataFrame(clusters)
        #     ind_outlier=df_cluster.index[df_cluster['cluster']==-1]
        #     # Filter the DF by removing the outlier points
        #     las_df = las_df.drop(ind_outlier)
            
            ######
            ###### Get the average ground value for analysis (!look for other methods to get ground val)

            # if use_tower_height is True:
            #     lidar_avg_g_elev = par_sp_dict[self.name][2]
            # else:
            #     # lidar_avg_g_elev = las_df_concat.loc[las_df_concat['CLASS'] == 2]['Z'].mean() # min elevation to calculate height above ground
            #     lidar_gpoints_df= las_df.loc[las_df['CLASS'] == 2].copy()
            #     p_98 = lidar_gpoints_df["Z"].quantile(0.98)
            #     lidar_q_df = lidar_gpoints_df[lidar_gpoints_df["Z"].ge(p_98)]
            #     lidar_avg_g_elev = lidar_q_df['Z'].mean()
            #     lidar_avg_g_elev = par_sp_dict[self.name][2] # AR 9.15
            # # print(lidar_avg_g_elev)
            # # lidar_avg_g_elev_meta = tower_dict[self.name][2]
            # # print(lidar_avg_g_elev)
            # temp_var = lidar_avg_g_elev - las_df[las_df['CLASS'].isin(veg_class_list)]['Z'].min()
            # if temp_var > 0:
            #     # calculate height using the average from ground points
            #     las_df['height'] = las_df['Z'] - lidar_avg_g_elev + temp_var
            # else:
            #     las_df['height'] = las_df['Z'] - lidar_avg_g_elev 
            
            # # Use the meta data to calculate height values for each lidar point
            # lidar_min_veg_height = las_df[las_df['CLASS'].isin(veg_class_list)]['height'].min()
            # lidar_max_veg_height = las_df[las_df['CLASS'].isin(veg_class_list)]['height'].max()

            ######
            ######


            dz=dzVal # get the dz value

            ## Filter out the tower points (AR 9.15)
            towHts = par_sp_dict[self.name][3]
            las_df = las_df.loc[las_df['Z'] <= (towHts[-1]-5)]

            # get an array containing the elevation intervals
            if use_tower_height is True:
                # if the use_tower_height boolean is True, get the height intervals correspondingto the site location
                height_list = np.array(par_sp_dict[self.name][3])
                # intialize the elevation and height lists
            elif use_tower_height is False:
                height_range_arr = np.arange(las_df['Z'].min(), las_df['Z'].max(), dz)
                # append value at the end (last value + dz)
                height_list = np.append(height_range_arr, height_range_arr[-1]+dz)

            # reverse to get the highest elevation to lowest
            height_arr_rev = height_list[::-1] #

            # Laser returns from canopy top to ground (total number of points in plot area) (Rv0 + Rg0)
            n_points = len(las_df.loc[las_df['Z'] <= height_arr_rev[0]]) # n_points is the total number of veg plus the total number of ground points

            # get the average scan angle
            avg_scan_ang = las_df['SCAN_ANGLE'].mean()

            # init lists to save GF and height values
            vert_gf_list = []

            # remove the negative values from the height array
            # height_arr_rev = height_arr_rev[height_arr_rev>0]

            for i in range(len(height_arr_rev)):
                top_of_canopy = height_arr_rev[0]
                lower_elev_intv = height_arr_rev[i]

                # Filter for points in height interval 
                df_filt = las_df.loc[(las_df['Z'] <= top_of_canopy) & (las_df['Z'] >= lower_elev_intv)]

                if df_filt.empty is True:
                    ###################
                    # add vertical gap fraction as 0 to the list
                    gf_value = 1.0

                    ## add values to lists
                    # append the GF value to the vert_gf_list
                    vert_gf_list.append(gf_value)
                    # Save the height value

                else:
                    # else if there are returns in the elevation interval
                    vegPtsInInterv = df_filt.loc[df_filt['Z']>0]['Z'].count()

                    gf_value = 1 - (vegPtsInInterv / (n_points))

                    # append the GF value to the vert_gf_list
                    vert_gf_list.append(round(gf_value,3))
                    # Save elevation to the vert_htList

            ##########   
            ## POINT DENSITY CALCULATION IN EACH HEIGHT INTERVAL
            ##########
            # initialize a pt density list to add values

            ptDensityList = []
            for i in range(len(height_arr_rev)-1):
                # get the elevation values for the interval
                upper_elev = height_arr_rev[i]
                lower_elev = height_arr_rev[i+1]

                # Filter for points in height interval 
                df_filt = las_df.loc[(las_df['Z'] > lower_elev) & (las_df['Z'] <= upper_elev)]
                # df_filt = df_filt.loc[df_filt['CLASS'] != 2] # should we exclue ground points?

                if df_filt.empty is True:
                    ###################
                    # add density value
                    ptDensity_val = 0.0
                   
                    ptDensityList.append(ptDensity_val)

                else:

                    ## Calculate point density in elevation interval
                    vegPtsInInterv = df_filt.loc[df_filt['Z']>0]['Z'].count()
                    ptDensity_val = (vegPtsInInterv / (n_points)) 

                    # add values to lists
                    ptDensityList.append(round(ptDensity_val, 3))

            return avg_scan_ang, vert_gf_list, height_arr_rev, ptDensityList
        ####### END INNER FUNCTION FOR CALCULATING GF

        ## Call the lidar_gf function to calculate gf
        theta_lidar, vert_gf_list, height_arr, densityList = innerFunction_lidarGF(df_lidarTotal)

        ## get the foliage density profile from gap fraction ## <------------review
        vert_gf_arr_zero_masked = np.array(vert_gf_list)
        vert_gf_arr_zero_masked[vert_gf_arr_zero_masked == 0] = np.nan
        G = 0.5 # Leaf orientation factor assuming spherical (AR & WN 10.1)
        accum_foliage = (-1 * np.log(vert_gf_arr_zero_masked)) / G 
        foliage_dens_prof = np.absolute(np.diff(accum_foliage, axis=0))
        foliage_dens_prof = foliage_dens_prof / (np.absolute(np.diff(height_arr, axis=0)))

        # Remember, the last value is zero, and may need to be removed later for PAR analysis (or replace zero with NaN)
        vert_gf_arr = np.array(vert_gf_list)
        density_arr = np.array(densityList)
        # density_arr = np.append(density_arr, [0]) # append 0 to the end of the arry to match the same lenght as the input (for plotting)
        
        # save calculate gf to class attribute
        self.gap = vert_gf_arr
        self.height = height_arr
        self.thetaL = theta_lidar
        self.accumFoliage = accum_foliage
        self.foliageDensity = np.insert(foliage_dens_prof, 0, np.nan)
        self.ptDensity = density_arr
        # save the ptDensity divided by dz
        self.dpdz = density_arr / (np.absolute(np.diff(height_arr, axis=0)))

        # Get biomass
        def biomassCalc():
            """
            Calculates biomass
            """

            # get the dz
            dz = np.absolute(np.diff(self.height, axis=0))
            
            # Waveform
            bi = self.dpdz * dz * (self.height[1:]**2)
            self.biW = np.sum(bi)

            # Foliage
            bi = self.foliageDensity[1:] * dz * (self.height[1:]**2)
            self.biF = np.sum(bi)

        # call the biomass function
        biomassCalc()

        # remove temporary directories
        shutil.rmtree(temp_directory)
        # if there was no output passed (output=None), delete the folder with all the saved LAS files and other data...
        if output is None:
            shutil.rmtree(out_directory)
        # print success message
        return


# ============================#END LasParStruct CLASS============================#


def latlonToUTMgpd(lat,lon):
    """Helper function
    """
    poi_latlon = [lat, lon]#  save the lat lon to a list for easy access
    # ------------GET THE UTM ZONE FROM LAT LON------------ #

    # Get the UTM zone for the site (poi_latlon[0]=lat and poi_latlon[1]=lon)
    # Mathematically locate the UTM zone from the lat long coordinates for distance analysis for regular longitude coordinates (AfriSAR data)
    # Get the longitude from one point the data to identify the UTM Zone (https://apollomapping.com/blog/gtm-finding-a-utm-zone-number-easily)
    lat_deg = poi_latlon[0]
    lon_deg = poi_latlon[1]
    # Add 180 to the longitude, then divide by 6 and round up to the next highest whole number
    lon180 = lon_deg + 180
    utmzoneNumber = math.ceil(lon180 / 6)

    # Project the geodataframe to UTM zone
    if lat_deg > 0:
        # North
        crs = CRS.from_string(f"+proj=utm +zone={utmzoneNumber} +north")
    else:
        # Else its south
        crs = CRS.from_string(f"+proj=utm +zone={utmzoneNumber} +south")

    # ------------GET POI INTO GEODATAFRAME AND REPROJECT TO UTM ZONE------------ #

    # Convert the POI to the UTM zone, and then export to shapefile
    dataForGDF = {'lat': poi_latlon[0], 'lon':poi_latlon[1]}
    gdf = gpd.GeoDataFrame(
        dataForGDF, geometry=gpd.points_from_xy([poi_latlon[1]], [poi_latlon[0]]), index=[0])
    # set the CRS to WGS84
    gdf = gdf.set_crs(epsg=4326)

    # Filter for epsg code based on UTM zone calculated above
    gdf = gdf.to_crs(f"EPSG:{crs.to_authority()[1]}")
    ## get a cirular buffer around the point and export to shapefile! (25m diameter to match LVIS footprint)
    
    return gdf

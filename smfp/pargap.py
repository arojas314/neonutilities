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


class GapDS:

    
    def __init__(self, x, y, z, **kwargs):
        
        self.x = x
        self.y = y
        self.z = z
        
        # Get the extra kwargs and save as attributes of same name (e.g szn=[1,2,3,4])
        for attr in kwargs.keys():
            self.__dict__[attr] = kwargs[attr]

        # Call the gap functions
        self.vegGroundSep()
        # Loop through each waveform and call the remaining functions for rhov_rhog, gap, etc.
        for i in range(len(self.wf)):
            self.gap_fol_calc(i)
            try:
                self.bioWF(i)
                self.bioFP(i)
            except:
                self.biWF.append(np.nan)
                self.biFP.append(np.nan)
        
    
    # Define properties for wf and ht data
    @property
    def wf(self):
        return self._wf
    @wf.setter
    def wf(self, value):
        if not isinstance(value, np.ndarray):
            raise TypeError('wf must be an ndarray, where each row is a seperate waveform.')
        self._wf = value

    @property
    def ht(self):
        return self._ht
    @ht.setter
    def ht(self, value):
        if not isinstance(value, np.ndarray):
            raise TypeError('ht must be an ndarray of heights same shape as the waveforms.')
        if value.shape != self.wf.shape:
            raise TypeError("wf and ht arrays are of different shapes.")
        self._ht = value

    @property
    def rh(self):
        return self._rh
    @rh.setter
    def rh(self, value):
        if (not isinstance(value, list)) and (not isinstance(value, np.ndarray)):
            raise TypeError('rh must be a list or an array of values that correspond to the relative' \
                           "heights for each waveform from which gap probability is calculated to the ground.")
        if len(value) != len(self.wf):
            raise TypeError("rh must be same length as the wf and ht arrays.")
        self._rh = value

        
    
    # --------------Functions to calculate gap-------------- #
    
    def vegGroundSep(self):
        
        inbools = self.ht<np.reshape(self.rh, (-1, 1))
        i_veg_first = np.argmax(inbools,axis=1)
        grd = np.where(np.absolute(self.ht) == np.min(np.absolute(self.ht),axis=1).reshape(-1,1))
        i_grd = grd[1]

        # Seperate ground and vegetation
        i_veg_last_list = []
        i_grd_last_list = []
        waveNorm_list = []
        dpdz_list = []
        dz = self.ht[0][0] - self.ht[0][1]

        for i in range(len(i_grd)):

            wf_i = self.wf[i].copy()
            ht_i = self.ht[i].copy()

            noise = 5 * np.std(wf_i[0:i_veg_first[i]])

            grnd_in = (np.where(wf_i[i_grd[i]:] < noise))
            i_grd_last = i_grd[i] + np.min(grnd_in)
            temp_veg = np.min([3.0, -ht_i[i_grd_last]])
            i_veg_last = np.max(np.where(ht_i >= temp_veg))
            i_veg_last_list.append(i_veg_last)
            i_grd_last_list.append(i_grd_last)


             ## Update waveform and heights
            wf_i[0:i_veg_first[i]-1] = np.nan
            wf_i[i_grd_last+1:] = np.nan

            # Normalize waveform
            wfnorm = np.divide(wf_i, np.nansum(wf_i))
            waveNorm_list.append(wfnorm)
            # Add a variable dpdz
            dpdz = wfnorm / dz
            dpdz_list.append(dpdz)

        # Add data to class (as arrays for easier data manipulation)
        self.dz = dz
        self.i_veg_first = i_veg_first
        self.i_grd = i_grd
        self.i_grd_last = np.array(i_grd_last_list)
        self.i_veg_last = np.array(i_veg_last_list)
        self.waveNorm = np.array(waveNorm_list)
        self.dpdz = np.array(dpdz_list)
        
    def gap_fol_calc(self, idx):

        # Get the current wf and indices
        cur_wf = self.waveNorm[idx]
        cur_veg_first = self.i_veg_first[idx]
        cur_veg_last = self.i_veg_last[idx]
        cur_grd_first = self.i_grd[idx]
        cur_grd_last = self.i_grd_last[idx]

        R_cur_v=np.sum(cur_wf[cur_veg_first:cur_veg_last])
        R_cur_g=np.sum(cur_wf[cur_grd_first:cur_grd_last])

        # Calculate vegetation cover
        veg_cover = R_cur_v / (R_cur_v + (self.rhovg)*R_cur_g)
        veg_cover2 = R_cur_v / (R_cur_v + R_cur_g)

        # Calculate gap probability
        pgap = np.empty(cur_wf.shape)
        pgap[:] = np.nan
        R_cur_vz = np.cumsum(cur_wf[cur_veg_first:cur_veg_last])
        pgap[cur_veg_first:cur_veg_last] = 1-(R_cur_vz / (R_cur_v + self.rhovg * R_cur_g))

        if len(pgap) == 0:
            self.cov.append(np.array(np.nan))
            self.covUncorr.append(np.array(np.nan))
            self.gap.append(np.array(np.nan))
            self.fdp.append(np.array(np.nan))
            self.appfdp.append(np.array(np.nan))
            self.lai.append(np.array(np.nan))
            return

        # effective foliage profile
        # assuming leaf orientation factor G(0) = 0.5
        foliage_accum =  -(np.log(pgap)) / 0.5
        # apparent foliage profile is: -(np.log(pgap))
        # Foliage density profile
        foliage_dens = np.diff(foliage_accum, prepend=foliage_accum[0])
        foliage_dens_eff = foliage_dens / self.dz
        foliage_dens_app = (foliage_dens / self.dz) / 2

        # Save vals to attributes
        self.cov.append(veg_cover)
        self.covUncorr.append(veg_cover2)
        self.gap.append(pgap)
        self.fdp.append(foliage_dens_eff)
        self.appfdp.append(foliage_dens_app)
        self.lai.append(foliage_accum)

    def bioWF(self, idx):
        # bioWF (waveform based biomass index):
        ht = self.ht[idx]
        cur_veg_first = self.i_veg_first[idx]
        cur_veg_last = self.i_veg_last[idx]
        gap = self.gap[idx][~np.isnan(self.gap[idx])]

        heightSubset = ht[cur_veg_first:cur_veg_last]
        dp = np.absolute(np.diff(gap, append=gap[-1]))
        bioWf = heightSubset**2 * dp

        self.biWF.append(np.nansum(bioWf))

    def bioFP(self, idx):
        ## bioFP (Foliage profile based biomass index)
        cur_veg_first = self.i_veg_first[idx]
        cur_veg_last = self.i_veg_last[idx]
        heightSubset = self.ht[idx][cur_veg_first:cur_veg_last]
        waveNormSubset = self.waveNorm[idx][cur_veg_first:cur_veg_last]
        gap = self.gap[idx][~np.isnan(self.gap[idx])]

        dp = np.absolute(np.diff(gap, append=gap[-1]))
        biofp = (heightSubset**2 * dp) / gap

        self.biFP.append(np.nansum(biofp))
    

############

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
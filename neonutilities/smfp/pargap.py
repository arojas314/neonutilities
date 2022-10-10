##  Pure Numpy Version

import numpy as np


class GapDS:

    
    def __init__(self, x, y, z, scan_angle, classification, **kwargs):
        
        self.x = x
        self.y = y
        self.z = z
        self.scan_angle = scan_angle
        self.c = classification
        self.dz = 1.5
        
        # Get the extra kwargs and save as attributes of same name (e.g szn=[1,2,3,4])
        for attr in kwargs.keys():
            self.__dict__[attr] = kwargs[attr]

        # calculate gap
        self.calc_gap()
        # call the biomass function
        self.biomassCalc()

    ## FUNCTION FOR CALCULATING GF
    def calc_gap(self): # pass the df_lidarTotal df as the las_df
        
#         use_tower_height = False
#         # get an array containing the elevation intervals
#         if use_tower_height is True:
#             # if the use_tower_height boolean is True, get the height intervals correspondingto the site location
#             height_arr = np.array(par_sp_dict[self.name][3])
#             # intialize the elevation and height lists
#         elif use_tower_height is False:
        
        # height array
        if np.max(self.z)>100:
            height_range_arr = np.arange(-1, np.percentile(self.z, 95), self.dz)
            # append value at the end (last value + dz)
            height_arr = np.append(height_range_arr, height_range_arr[-1]+self.dz)
        else:
            height_range_arr = np.arange(-1, np.max(self.z), self.dz)
            height_arr = np.append(height_range_arr, height_range_arr[-1]+self.dz)

        # reverse to get the highest elevation to lowest
        height_arr = height_arr[::-1] #

        # Laser returns from canopy top to ground (total number of points in plot area) (Rv0 + Rg0)
        n_points = len(self.z[self.z <= height_arr[0]]) # n_points is the total number of veg plus the total number of ground points

        # get the average scan angle
        avg_scan_ang = np.mean(self.scan_angle)

        # init lists to save GF and height values
        gap_list = [1] # add 1 at beginning to make gap and ht array even
        density_list = [0]

        # remove the negative values from the height array
        # height_arr_rev = height_arr_rev[height_arr_rev>0]
        top_of_canopy = height_arr[0]
        for i in range(len(height_arr)-1):
            upper_elev_intv = height_arr[i]
            lower_elev_intv = height_arr[i+1]

            # Filter for points in height interval 
            gap_pts_filter = (self.z <= top_of_canopy) & (self.z >= lower_elev_intv)
            density_pts_filter = (self.z <= upper_elev_intv) & (self.z >= lower_elev_intv)
            gap_pts = self.z[gap_pts_filter]
            density_pts = self.z[density_pts_filter]
            
            # gap
            if len(gap_pts)==0:
                ###################
                # add vertical gap fraction as 0 to the list
                gf_value = 1.0
                gap_list.append(gf_value)

            else:
                # else if there are points in the elevation interval
                vegPtsInInterv = len(gap_pts[gap_pts>0])
                gf_value = 1 - (vegPtsInInterv / (n_points))

                # append the GF value to the vert_gf_list
                gap_list.append(round(gf_value,3))
                
            # point density
            if len(density_pts)==0:
                ###################
                # add density value
                ptDensity_val = 0.0
                
                density_list.append(ptDensity_val)

            else:

                ## Calculate point density in elevation interval
                vegPtsInInterv = len(density_pts[density_pts>=0])
                ptDensity_val = (vegPtsInInterv / (n_points)) 

                # add values to lists
                density_list.append(round(ptDensity_val, 3))
                

        ## get the foliage density profile from gap fraction ## <------------review
        gap_arr = np.array(gap_list)
        gap_arr[gap_arr == 0] = np.nan
        G = 0.5 # Leaf orientation factor assuming spherical (AR & WN 10.1)
        accum_foliage = (-1 * np.log(gap_arr)) / G 
        foliage_dens_prof = np.absolute(np.diff(accum_foliage, axis=0))
        foliage_dens_prof = foliage_dens_prof / (np.absolute(np.diff(height_arr, axis=0)))

        # Remember, the last value is zero, and may need to be removed later for PAR analysis (or replace zero with NaN)
        density_arr = np.array(density_list)

        # save calculate gf to class attribute
        self.gap = np.array(gap_list)
        self.height = height_arr
        self.theta = avg_scan_ang
        self.accumFoliage = accum_foliage
        self.foliageDensity = np.insert(foliage_dens_prof, 0, np.nan)
        self.ptDensity = density_arr
        # save the ptDensity divided by dz
        self.dpdz = density_arr / (np.absolute(np.diff(height_arr, axis=0, prepend=np.nan)))
        

    # Get biomass
    def biomassCalc(self):
        """
        Calculates biomass
        """

        # get the dz
        dz = np.absolute(np.diff(self.height, axis=0, prepend=self.height[0]+1.5))
        
        # Waveform
        bi = self.dpdz * dz * (self.height**2)
        self.biwf = np.sum(bi)

        # Foliage
        bi = self.foliageDensity * dz * (self.height**2)
        self.bifp = np.sum(bi)
        
    
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
            thetaL_rad = self.theta * (np.pi/180)
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
            thetaL_rad = self.theta * (np.pi/180)
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

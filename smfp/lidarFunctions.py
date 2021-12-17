import glob
import os
import subprocess
CWD = os.getcwd()
from whitebox import whitebox_tools

# Set the whitebox tools to current directory
wbt = whitebox_tools.WhiteboxTools()
wbt.set_verbose_mode(False)
os.chdir(CWD)


def filter_discrete(directory, aoi, merge=True):

    """Filter discrete NEON lidar tiles for all returns within an area of interest.

    :param directory: directory with the NEON lidar tiles
    :param aoi: a polygon shapefile for the area of interest.
    :param merge: Merge the filtered lidar files. Default is true

    :return: filtered lidar tiles

    """

    # Set the working directory for whitebox
    absPath = os.path.abspath(directory)
    wbt.set_working_dir(absPath)

    # get las files to merge
    l_files = [os.path.basename(x) for x in glob.glob(f"{absPath}/*.las")]

    # get the file extension
    if len(l_files) > 1:
        # Merge the lidar tiles that were selected in the polygon
        # clip lidar to polygon (harvard polot AOI)
        for f in l_files:

            wbt.clip_lidar_to_polygon(
                i= f, 
                polygons = os.path.abspath(aoi),
                output = f"{f[:-4]}_clip.las"
            )

            # Set the cwd back to the project dir
            os.chdir(absPath)

        if merge == True:
            l_filesToJoin = glob.glob(f"{absPath}/*_clip.las")
            
            wbt.lidar_join(
                inputs = ", ".join(l_filesToJoin), 
                output = f"lidarAOI.las"
            )

            # Set the cwd back to the project dir
            os.chdir(absPath)
            # Remove all clipped files
            os.system(f"rm {absPath}/*_clip.las")


    elif len(l_files) == 1:

        # clip lidar to polygon
        wbt.clip_lidar_to_polygon(
            i= l_files[0], 
            polygons = os.path.abspath(aoi),
            output = f"lidarAOI.las"
        )

        # Set the cwd back to the workign dir
        os.chdir(absPath)


    elif len(l_files) == 0:
        print("No LiDAR files available in selected area. Check the coordinate inputs provided.")
        # Set the cwd back to the project dir
        os.chdir(CWD)
        return


    # Set the cwd back to the project dir
    os.chdir(CWD)

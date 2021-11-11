import glob
import os
import subprocess
CWD = os.getcwd()

from whitebox import whitebox_tools
# Set the whitebox tools to current directory
wbt = whitebox_tools.WhiteboxTools()
wbt.set_verbose_mode(False)
os.chdir(CWD)


def filter_discrete(directory, aoi, merge=True, heights=True):

    """Filter discrete NEON lidar tiles for all returns within an area of interest.

    :param directory: directory with the NEON lidar tiles
    :param aoi: a polygon shapefile for the area of interest.
    :param merge: Merge the filtered lidar files. Default is true
    :param heights: Replace elevatio values with height. Default is False.

    :return: filtered lidar tiles

    """
    # Set the working directory for whitebox
    absPath = os.path.abspath(directory)
    wbt.set_working_dir(absPath)

    os.makedirs(f"{absPath}/ground_classified")
    
    # classify ground and height
    cmdList = f"wine /data/software/wine/LAStools/bin/lasground64.exe -i {absPath}/*laz -odir {absPath}/ground_classified -no_clean -olaz".split()
    subprocess.call(cmdList)

    # get las files to merge
    l_files = [os.path.basename(x) for x in glob.glob(f"{absPath}/ground_classified/*.las")]

    # get the file extension
    if len(l_files) > 1:
        # Merge the lidar tiles that were selected in the polygon
        # clip lidar to polygon (harvard polot AOI)
        for f in l_files:

            wbt.clip_lidar_to_polygon(
                i= f, 
                polygons = os.path.abspath(aoi),
                output = f"{f[:-4]}_clip.laz"
            )

            # Set the cwd back to the project dir
            os.chdir(absPath)

        if merge == True:
            l_filesToJoin = glob.glob(f"{absPath}/*_clip.laz")
            
            wbt.lidar_join(
                inputs = ", ".join(l_filesToJoin), 
                output = f"lidarAOI_temp.laz"
            )

            # Set the cwd back to the project dir
            os.chdir(absPath)
            # Remove all clipped files
            os.system(f"rm {absPath}/*_clip.laz")


    elif len(l_files) == 1:

        # clip lidar to polygon
        wbt.clip_lidar_to_polygon(
            i= l_files[0], 
            polygons = os.path.abspath(aoi),
            output = f"lidarAOI_temp.laz"
        )

        # Set the cwd back to the workign dir
        os.chdir(absPath)


    elif len(l_files) == 0:
        print("No LiDAR files available in selected area. Check the coordinate inputs provided.")
        # Set the cwd back to the project dir
        os.chdir(CWD)
        return


    # Classify ground points
    # wbt.lidar_ground_point_filter(
    #     i="lidarAOI_temp.laz", 
    #     output="lidarAOI.laz", 
    #     radius=10,
    #     min_neighbours=10,
    #     slope_threshold=45.0, 
    #     height_threshold=0.5, 
    #     classify=True, 
    #     slope_norm=True, 
    #     height_above_ground=heights
    # )

    wbt.height_above_ground(
        i="lidarAOI_temp.laz",
        output="lidarAOI.laz"
        )

    # cmdList = f"wine /data/software/wine/LAStools/bin/lasground64.exe -i {os.path.abspath('lidarAOI_temp.laz')} -o {os.path.abspath('lidarAOI.laz')} -compute_height -replace_z".split()
    # subprocess.call(cmdList)

    # Remove the temporary las files
    os.system(f"rm {absPath}/*temp.laz")
    # Set the cwd back to the project dir
    os.chdir(CWD)

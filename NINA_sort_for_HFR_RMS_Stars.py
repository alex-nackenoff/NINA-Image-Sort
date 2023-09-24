import os
from pathlib import Path
import shutil
import sys
from io import StringIO
#comment out this if not using discord alert
from discordwebhook import Discord

#insert discord webhook url below inside quotes, or comment out if not using discord alert 
discord = Discord(url="")
calibration = ["FLAT", "DARK", "DARKFLAT", "BIAS", "SNAPSHOT"]

# My NINA File Structure: $$DATEMINUS12$$\$$TARGETNAME$$\$$IMAGETYPE$$\$$DATETIME$$_$$EXPOSURETIME$$s_$$FRAMENR$$_$$STARCOUNT$$_$$HFR$$_$$RMSARCSEC$$
# eg: pattern preview (including folders): 2015-12-31 › M33 › LIGHT › 2016-01-01_12-00-00_10.21s_0001_3294_3.25_0.65
# rsplit reads from right to left, parsing by separator, here an underscore ('_')
# filtering by Stars = is the -3 position , HFR = -2, RMS = -1
# 
# for an image file: image = '2023-09-06_20-36-56_180.00s_0000_151_3.60_0.99.fits'
# drop the file extension: image_no_ext = Path(image).stem
# this is the output for image_no_ext.rsplit("_")
# ['2023-09-06', '20-36-56', '180.00s', '0000', '151', '3.60', '0.99']

all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
latest_subdir = max(all_subdirs, key=os.path.getmtime)
os.chdir(latest_subdir)
sys.stdout = open('Unfit_Lights_logfile.txt', 'w')

folders = [f for f in os.listdir() if os.path.isdir(f) and f not in calibration]

for folder in folders:
    a = StringIO() 
    counter = 0
    counter_stars = 0
    counter_hfr = 0
    counter_guiding = 0
    
    os.chdir(folder)
    os.chdir("LIGHT")
    sort_folder = "unfit"
    isExist = os.path.exists(sort_folder)
    if not isExist:
        os.makedirs(sort_folder)
        print("Created " + sort_folder + " Folder in " + os.getcwd())
    else:
        print(sort_folder + " Folder Already Exists!")

    images = [f for f in os.listdir() if '.fits' in f.lower()]

    for image in images:
        file_no_ext = Path(image).stem
        abc12345 = file_no_ext.rsplit("_")
        if int(abc12345[-3])<10:
            #STARCOUNT
            new_path = 'unfit/' + image
            shutil.move(image, new_path)
            print("Moved " + image + " in " + folder + " Due to Stars")
            counter += 1
            counter_stars += 1

        elif float(abc12345[-2])>4 or float(abc12345[-2])<0.1:
            #HFR
            #numbers with decimels requires float instead of int (integer)
            new_path = 'unfit/' + image
            shutil.move(image, new_path)
            print("Moved " + image + " in " + folder + " Due to HFR")
            counter += 1
            counter_hfr += 1

        elif float(abc12345[-1])>2.2:
            #RMSARCSEC
            new_path = 'unfit/' + image
            shutil.move(image, new_path)
            print("Moved " + image + " in " + folder +" Due to Guiding")
            counter += 1
            counter_guiding += 1
            
    os.chdir("..")
    os.chdir("..")
    
    test1 = "Moved " + str(counter_stars) + " files due to stars"
    test2 = "Moved " + str(counter_hfr) + " files due to HFR"
    test3 = "Moved " + str(counter_guiding) + " files due to Guiding"
    result = f"{counter/len(images):.0%}"
    
    a.write("Analyzing " + str(folder) +"......"+ "\n    " + "Moved " + str(counter)+ " ("+ result +")" + " total files")
    if counter_stars != 0:
        a.write("\n    " + test1)
    if counter_hfr != 0:
        a.write("\n    " + test2)
    if counter_guiding != 0:
        a.write("\n    " + test3)
    print(a.getvalue())
    # comment out below if you don't want Discord alerts
    discord.post(content=(a.getvalue()))


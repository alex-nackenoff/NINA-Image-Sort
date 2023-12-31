# NINA Image Sorting Script

## Description:
Instead of manually sorting through astrophotography images generated by NINA, I made this script to automatically sort out images that are unusuable for stacking due to wind, major cloud cover, guiding issues, etc. The python script finds the most recent project folder, finds the LIGHT frame subfolder, and analyzes the filename that has the included star count, HFR, and guiding stats. This script is called the .bat file at the end of a NINA Advanced Sequence. This is simply v1 of the script, the parameters are arbitrary, and currently hard coded, so obviously you should taileor to fit your needs. Also I am a novice when it comes to Python, so there are definitely areas of improvement over this first draft. But figured I'd throw it on Github in case it's helpful for anyone. (Now with optional Discord Alerts)

## Requirements/Python Install:
1. Install [miniconda](https://docs.conda.io/projects/miniconda/en/latest/index.html). This will install python and some necessary components. This saves a bit of space over a full anaconda install, but if you already have anaconda installed you can use that.
2. The .bat file is designed to work with miniconda added to PATH, so during the install procedure do check the box to install to PATH. You can always add the folder to PATH if you skipped this step
3. Once install is finished, it's a good idea to ensure conda is happy and working. Open a command prompt window and update conda

```
conda update conda
```

enter y as needed

4. Then, it's best practice to run each python project in its own virtual environment.

```
conda create --name nina
```

again enter y as needed

5. Then lets activate the new virtual environment to ensure things are working

```
conda activate nina
```

if everything is working, you should see something like:

```
(nina) C:\Users\<user>
```

## Optional Discord Alert
I included a Discord alert, mostly since I like to wake up and see on my phone that my mount is in the home position (using the Discord alert NINA plugin), and figured that I would also like to see how many frames got thrown out, and for what target (since I shoot multiple targets in a night). If you don't want this integration, comment out (#) the discord related commands.

To get Discord commands working:
```python
pip install discordwebhook
```

and insert your Discord bot webhook url where noted in the python code

type exit to close

6. Download and extract the zip folder of this repo, and place the .bat and .py file in your default NINA save location. For me that's "Z:\Pictures\Astro\NINA_Ingest"


## .bat File Editing
The .bat file is designed to run at the end of your NINA advanced sequence, but needs to be customized to work in your setup. NINA will run the .bat file from wherever you have it stored, but will try to run it from its program folder. So the .bat file needs to be edited to hard code to change directories to where NINA saves your images by default

```
@echo off
title Sort NINA images

cmd /k "cd /d <folder location here without brackets> && conda activate nina && python NINA_sort_for_HFR_RMS_Stars.py && exit"
```

### Example .bat
```
@echo off
title Sort NINA images 

cmd /k "cd /d Z:\Pictures\Astro\NINA_Ingest && conda activate nina && python NINA_sort_for_HFR_RMS_Stars.py && exit"
```

Once that's ready, add 'External Script' as a new step in your NINA advanced sequence, and point it to your .bat file

## Python Script Behavior

### Assumptions
1. NINA File Structure: 

\$$DATEMINUS12\$$\\$$TARGETNAME\$$\\$$IMAGETYPE\$$\\$$DATETIME\$$\_\$$EXPOSURETIME\$$s\_\$$FRAMENR\$$\_\$$STARCOUNT\$$\_\$$HFR\$$\_\$$RMSARCSEC\$$
+ the odering doesn't matter but the things you want to sort by need to be included in the NINA file structure
2. Sorting, in order of priority:
+ Star Count
+ HFR
+ RMS
3. Sort priority is arbitrary, but the output log file will tell you the first reason an image got sorted out if that is of interest

Below is the python script. Whatever parameters you wish to sort by will need to be hard coded based on the position of that feature in your NINA file naming convention. The script parses the file by the default hyphen "_" separator, counting from the right. In the example below, RMS is the last item, and the first from the right, or the "-1" position, HFR = -2, and star count = -3. Any item that uses a decimel needs to be interpreted with "float" rather than "int", as demonstrated below. 

```python
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

```

## Example Discord Alert Output

Inside the analysis loop, reports analyzed target (ie the current parent folder), reports total number of rejected frames, including in the context of the total number of sub-exposures. Only includes details if any trigger was satisfied.

```
Analyzing Andromeda Galaxy......
    Moved 1 (6%) total files
    Moved 1 files due to HFR
Analyzing Veil Nebula......
    Moved 7 (7%) total files
    Moved 7 files due to HFR
```
@echo off
title Sort NINA images

cmd /k "cd /d Z:\Pictures\Astro\NINA_Ingest && conda activate nina && python NINA_sort_for_HFR_RMS_Stars.py && exit"

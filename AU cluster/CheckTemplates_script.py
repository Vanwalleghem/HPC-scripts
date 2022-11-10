from CheckTemplatesFix import CheckTemplateAndFix
import glob
import os
import sys

tif_file_folder=sys.argv[1]
print(tif_file_folder)
CheckTemplateAndFix(tif_file_folder)



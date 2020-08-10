import sys
import os
import tempfile
import cv2
from math import ceil
import sys

print(len(sys.argv) > 1)

# files = []
# input_directory_path = os.path.join(os.getcwd(), input_directory)
# # r=root, d=directories, f = files
# for r, d, f in os.walk(input_directory_path):
#     for file in f:
#         if '.pdf' in file:
#             files.append(os.path.join(r, file))
#
# for x in files:
#     print(x)
#
# current_dir = os.getcwd()
# output_directory = os.path.join(input_directory_path, "out")
# if not os.path.exists(output_directory):
#     os.mkdir(output_directory)
#
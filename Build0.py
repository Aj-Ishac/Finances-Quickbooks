import time
import cv2

import utility
import pytesseract as tess
import pyImageProcess as pyIP
import readImage as pyRI

if __name__ == "__main__":

    # file_queue = utility.folder_parse("Images-Raw")
    # file_queue = sorted(file_queue)
    # file_queue = ["20220420_213104.jpg", "20220421_001513.jpg", "20220425_200954.jpg", "20220428_031510.jpg"]
    file_queue = ["20220428_031510.jpg"]    # , "20220420_213104.jpg", "20220405_232412.jpg", "20220421_001520.jpg"]
    for image_name in file_queue:
        total_time = 0
        image_directory = '..\\Images-Raw\\'
        image_complete_Path = image_directory + image_name
        image_name = image_name[:-4]

        # complete processing package
        start = time.time()
        original_image, processed_image, bordered_image = pyIP.master_image_processor(image_complete_Path)
        end = time.time()
        total_time += end - start
        print("Processing Package Computation Time: ", round(total_time, 2))

        # complete OCR package
        start = time.time()
        date, products, vendor, vendor_url, averageConf = pyRI.master_image_read(image_name, processed_image)
        end = time.time()
        total_time += end - start
        print("Reader Package Computation Time: ", round(total_time, 2))

        cv2.imwrite(f"..\\Images-Converted\\{image_name}_{averageConf}Original.jpg", original_image)
        cv2.imwrite(f"..\\Images-Converted\\{image_name}_{averageConf}Processed.jpg", processed_image)
        cv2.imwrite(f"..\\Images-Converted\\{image_name}_{averageConf}Border.jpg", bordered_image)
        utility.writer(image_name, "Logs.txt", averageConf)
        # config.saveImage('..\\Images-Converted\\', image_name, refinedImage)

# to-do:
# 1. try DPI trick for tess_conf, image_size pyIP l81, thicken text -> median blur, tess alt config for logo reading
# 2. NN text classification model
# 3. improve OCR conf
#    confidence needs to be >95%
# 4. ML model to predict product matching under respective categories
# 5. set up mySQL DB

# ['20220403_171741.jpg',    1 - FAIL       (-215:Assertion failed) reader.ptr != NULL in function 'cvDrawContours'
#  '20220405_232339.jpg',    2 - FAIL       'charmap' codec can't encode character '\ufb01' in position 8: character maps to <undefined>
#  '20220405_232352.jpg',    3 - FAIL 70%   cannot unpack non-iterable NoneType object
#  '20220405_232412.jpg',    4 - PASS 68%   date mismatch, no products?
#  '20220405_232446.jpg',    5 - FAIL 73%   cannot unpack non-iterable NoneType object
#  '20220406_231142.jpg',    6 - FAIL 73%   cannot unpack non-iterable NoneType object
#  '20220417_151151.jpg',    7 - FAIL       local variable 'avg_conf' referenced before assignment
#  '20220418_191924.jpg',    8 - FAIL       'charmap' codec can't encode character '\ufb01' in position 12: character maps to <undefined>
#  '20220420_213104.jpg',    9 - PASS 76%   subtota | sneaked its way into products due to tess inaccuracy, vendor mismatch. consider getting rid of url
#  '20220420_213112.jpg',   10 - FAIL 61%   cannot unpack non-iterable NoneType object
#  '20220420_213119.jpg',   11 - FAIL       'charmap' codec can't encode character '\ufb02' in position 20: character maps to <undefined>
#  '20220420_213127.jpg',   12 - FAIL       (-215:Assertion failed) reader.ptr != NULL in function 'cvDrawContours'
#  '20220420_213134.jpg',   13 - FAIL 78%   cannot unpack non-iterable NoneType object
#  '20220421_001513.jpg',   14 - PASS 57%   missing items, price incorrect
#  '20220421_001520.jpg',   15 - FAIL PROG  'charmap' codec can't encode character '\ufb01' in position 28: character maps to <undefined>
#  '20220425_200947.jpg',   16 - FAIL       (-215:Assertion failed) reader.ptr != NULL in function 'cvDrawContours'
#  '20220425_200954.jpg',   17 - PASS 75%   lstrip product name, vendor/url regex incorrect, parse out "Cash" and "Change"
#  '20220425_201006.jpg',   18 - FAIL       (-215:Assertion failed) reader.ptr != NULL in function 'cvDrawContours'
#  '20220425_201019.jpg',   19 - FAIL       (-215:Assertion failed) reader.ptr != NULL in function 'cvDrawContours'
#  '20220425_201027.jpg',   20 - FAIL 53%   cannot unpack non-iterable NoneType object
#  '20220428_031457.jpg',   21 - FAIL       local variable 'avg_conf' referenced before assignment
#  '20220428_031503.jpg',   22 - FAIL 63%   cannot unpack non-iterable NoneType object
#  '20220428_031510.jpg',   23 - PASS 72%   CHECK
#  '20220428_031519.jpg',   24 - FAIL       'charmap' codec can't encode character '\ufb01' in position 27: character maps to <undefined>
#  '20220428_031527.jpg',   25 - FAIL 36%   cannot unpack non-iterable NoneType object
#  '20220504_120549.jpg',   26 - FAIL       'charmap' codec can't encode character '\ufb02' in position 6: character maps to <undefined>
#  '20220504_120558.jpg',   27 - FAIL 63%   cannot unpack non-iterable NoneType object
#  '20220504_120610.jpg',   28 - FAIL 75%   cannot unpack non-iterable NoneType object
#  '20220504_120619.jpg',   29 - FAIL 44%   cannot unpack non-iterable NoneType object
#  '20220504_120636.jpg',   30 - FAIL       'charmap' codec can't encode character '\ufb01' in position 28: character maps to <undefined>
#  '20220504_120943.jpg',   31 - FAIL       local variable 'avg_conf' referenced before assignment
#  '20220504_120947.jpg',   32 - FAIL       (-215:Assertion failed) reader.ptr != NULL in function 'cvDrawContours'
#  '20220504_120951.jpg',   33 - FAIL       error: (-215:Assertion failed) reader.ptr != NULL in function 'cvDrawContours'
#  '20220505_172117.jpg',   34 - FAIL       local variable 'avg_conf' referenced before assignment
#  '20220508_171459.jpg',   35 - FAIL       local variable 'avg_conf' referenced before assignment
#  '20220508_211331.jpg',   36 - FIX  70%   'charmap' codec can't encode character '\ufb01' in position 1: character maps to <undefined>
#  'bill3.jpg',             37 - FAIL 45%   cannot unpack non-iterable NoneType object
#  'walmart-template.jpg'   38 - FAIL       'NoneType' object is not iterable

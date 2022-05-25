import time
import cv2

import utility
import pytesseract as tess
import pyImageProcess as pyIP
import readImage as pyRI

if __name__ == "__main__":
    tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    # file_queue = utility.folder_parse("Images-Raw")
    # file_queue = sorted(file_queue)

    # batch to process
    file_queue = ["20220420_213112.jpg"]

    total_runtime = []
    for image_name in file_queue:
        curr_runtime, process_runtime = 0, 0
        image_directory = '..\\Images-Raw\\'
        image_complete_path = image_directory + image_name
        image_name = image_name[:-4]

        # Image_Processing Package
        start = time.time()
        original_image, processed_image, bordered_image = pyIP.master_image_processor(image_name, image_complete_path)
        end = time.time()
        curr_runtime += end - start
        process_runtime += curr_runtime

        # Reader Package
        start = time.time()
        processed_image = cv2.imread(f"..\\Images-Converted\\{image_name}_Processed.jpg", 1)
        date, products, vendor, averageConf = pyRI.master_image_read(image_name, processed_image)
        end = time.time()
        curr_runtime += end - start
        process_runtime += curr_runtime
        total_runtime.append(process_runtime)
        print(f"\nReader Package Comp. Time: {round(curr_runtime, 2)}s")
        print(f"Summed Process Comp. Time: {round(process_runtime, 2)}s")

        # cv2.imwrite(f"..\\Images-Converted\\{image_name}_{averageConf}Original.jpg", original_image)
        # cv2.imwrite(f"..\\Images-Converted\\{image_name}_{averageConf}Processed.jpg", processed_image)
        # cv2.imwrite(f"..\\Images-Converted\\{image_name}_{averageConf}Border.jpg", bordered_image)
        utility.writer(image_name, "..\\Build\\Logs.txt", averageConf)
        # config.saveImage('..\\Images-Converted\\', image_name, refinedImage)

    print(f"Total Running Comp. Time: , {round(sum(total_runtime), 2)}s")

# to-do:
# 1. improve OCR conf
#    confidence needs to be >95%, tess alt config for logo reading
# 2. ML model to predict product matching under respective categories
# 3. set up mySQL DB

# ['20220403_171741.jpg',    1 - FAIL       (-215:Assertion failed) reader.ptr != NULL in function 'cvDrawContours'
#  '20220405_232339.jpg',    2 - FAIL       Image not rotated correctly -> TypeError: sequence item 26: expected str instance, float found
#  '20220405_232352.jpg',    3 - PASS 65%   cannot unpack non-iterable NoneType object
#  '20220405_232412.jpg',    4 - PASS 79%   
#  '20220405_232446.jpg',    5 - FAIL 73%   Image not rotated correctly -> AttributeError: 'NoneType' object has no attribute 'group'
#  '20220406_231142.jpg',    6 - FAIL 73%   cannot unpack non-iterable NoneType object
#  '20220417_151151.jpg',    7 - FAIL       local variable 'avg_conf' referenced before assignment
#  '20220418_191924.jpg',    8 - PASS 82%   
#  '20220420_213104.jpg',    9 - PASS 83%   
#  '20220420_213112.jpg',   10 - PASS 75%   cannot unpack non-iterable NoneType object
#  '20220420_213119.jpg',   11 - PASS 80%   tax was not scanned because 4.25's dot was missing from scan. if confidence > threshold, assign extras: total - products
#  '20220420_213127.jpg',   12 - FAIL       (-215:Assertion failed) reader.ptr != NULL in function 'cvDrawContours'
#  '20220420_213134.jpg',   13 - FAIL 78%   cannot unpack non-iterable NoneType object
#  '20220421_001513.jpg',   14 - PASS 72%   
#  '20220421_001520.jpg',   15 - PASS 73%   
#  '20220425_200947.jpg',   16 - FAIL       (-215:Assertion failed) reader.ptr != NULL in function 'cvDrawContours'
#  '20220425_200954.jpg',   17 - PASS 84%   
#  '20220425_201006.jpg',   18 - FAIL       (-215:Assertion failed) reader.ptr != NULL in function 'cvDrawContours'
#  '20220425_201019.jpg',   19 - FAIL       (-215:Assertion failed) reader.ptr != NULL in function 'cvDrawContours'
#  '20220425_201027.jpg',   20 - FAIL 53%   cannot unpack non-iterable NoneType object
#  '20220428_031457.jpg',   21 - FAIL       local variable 'avg_conf' referenced before assignment
#  '20220428_031503.jpg',   22 - FAIL 63%   cannot unpack non-iterable NoneType object
#  '20220428_031510.jpg',   23 - PASS 85%
#  '20220428_031519.jpg',   24 - FAIL       AttributeError: 'NoneType' object has no attribute 'group'
#  '20220428_031527.jpg',   25 - FAIL 36%   cannot unpack non-iterable NoneType object
#  '20220504_120549.jpg',   26 - PASS 72%       
#  '20220504_120558.jpg',   27 - FAIL 63%   cannot unpack non-iterable NoneType object
#  '20220504_120610.jpg',   28 - FAIL 75%   cannot unpack non-iterable NoneType object
#  '20220504_120619.jpg',   29 - FAIL 44%   cannot unpack non-iterable NoneType object
#  '20220504_120636.jpg',   30 - PASS 70%   
#  '20220504_120943.jpg',   31 - FAIL       local variable 'avg_conf' referenced before assignment
#  '20220504_120947.jpg',   32 - FAIL       (-215:Assertion failed) reader.ptr != NULL in function 'cvDrawContours'
#  '20220504_120951.jpg',   33 - FAIL       error: (-215:Assertion failed) reader.ptr != NULL in function 'cvDrawContours'
#  '20220505_172117.jpg',   34 - FAIL       local variable 'avg_conf' referenced before assignment
#  '20220508_171459.jpg',   35 - FAIL       local variable 'avg_conf' referenced before assignment
#  '20220508_211331.jpg',   36 - PASS 80%   
#  'bill3.jpg',             37 - FAIL 45%   cannot unpack non-iterable NoneType object
#  'walmart-template.jpg'   38 - FAIL       'NoneType' object is not iterable

# parsed edge cases 13/37
# file_queue = ["20220421_001520.jpg", "20220405_232412.jpg", "20220425_200954.jpg",
#               "20220421_001513.jpg", "20220420_213104.jpg", "20220428_031510.jpg",
#               "20220418_191924.jpg", "20220420_213119.jpg", "20220504_120636.jpg",
#               "20220508_211331.jpg"]
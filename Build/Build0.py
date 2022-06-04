import time
import cv2
import imutils

import utility
import pytesseract as tess
import pyImageProcess as pyIP
import readImage as pyRI
import db_connector as dbc


if __name__ == "__main__":
    tess.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    # file_queue = utility.folder_parse("Images-Raw")
    # file_queue = sorted(file_queue)

    # batch to process
    file_queue = ["20220428_031510.jpg"]
    total_runtime = []
    for image_name in file_queue:
        process_runtime = 0
        image_directory = "..\\Images-Raw\\"
        image_complete_path = image_directory + image_name
        image_name = image_name[:-4]

        start = time.time()
        # Image_Processing Package
        bordered_image = pyIP.master_image_processor(image_name, image_complete_path)

        # Reader Package
        processed_image = cv2.imread(f"..\\Images-Converted\\Processed\\{image_name}_Processed.jpg", 1)
        scan_results, averageConf = pyRI.master_image_read(image_name, processed_image)

        utility.writer(image_name, "..\\Build\\Logs.txt", averageConf)
        user_data = ["test.w@gmail.com", "Hello", "Hi", "1954/09/02", "pass1954"]
        dbc.Q_add_product_data(scan_results, user_data[0])

        end = time.time()
        process_runtime = end - start
        total_runtime.append(process_runtime)
        print(f"Process Run Time: {process_runtime:.2f}s")
        # os.system("pause")

    print(f"\n  Total Run Time: {sum(total_runtime):.2f}s")
    print(f"Average Run Time: {sum(total_runtime)/len(file_queue):.2f}s")

# to-do:
# 1. improve OCR conf
#    confidence needs to be >95%, tess alt config for logo reading
#    train new fonts
# 2. ML model to predict product matching under respective categories
# 3. set up mySQL DB

#  "20220504_120558.jpg"  - PASS 78%
#  "20220504_120610.jpg"  - PASS 82%
#  "20220504_120619.jpg"  - PASS 78%
#  "20220425_201027.jpg"  - PASS 62%
#  "20220418_191924.jpg"  - PASS 82%
#  "20220420_213104.jpg"  - PASS 83%
#  "20220420_213112.jpg"  - PASS 75%
#  "20220421_001520.jpg"  - PASS 73%
#  "20220425_200954.jpg"  - PASS 84%
#  "20220428_031510.jpg"  - PASS 85%
#  "20220504_120549.jpg"  - PASS 72%
#  "20220525_135810.jpg"  - PASS 70%
#  "20220525_135836.jpg"  - PASS 71%
#  "20220405_232446.jpg"  - PASS 71%
#  "20220405_232412.jpg"  - PASS 79%
#  "20220420_213119.jpg"  - PASS 80%    Empty Product Listing, blacklist triggered off product name
#  "20220508_211331.jpg"  - PASS 80%    Empty Product Listing, blacklist triggered off product name !!!
#  "20220406_231142.jpg"  - PASS 74%    Total off, run check to compare sum(product_listing) vs OCR total
#  "20220405_232352.jpg"  - PASS 65%    Total off, run check to compare sum(product_listing) vs OCR total
#  "20220405_232339.jpg"  - PASS 81%    Font used is detecting space between price points resulting in no products shown
#  "20220421_001513.jpg"  - PASS 72%    Ross: Font used is detecting space between price points resulting in no products shown
#  "20220428_031503.jpg"  - PASS 72%    Ross: Font used is detecting space between price points resulting in no products shown
#  "20220504_120636.jpg"  - PASS 70%    Ross: Font used is detecting space between price points resulting in no products shown
#  "20220525_135758_e.jpg"- PASS 77%    Manual PS Background Remove Fix
#  "20220428_031519_e.jpg"- PASS 77%    Manual PS Background Remove Fix
#  "20220428_031457_e.jpg"- PASS 80%    Manual PS Background Remove Fix
#  "20220522_174911.jpg"  - FAIL        NoContrast Background
#  "20220522_174911.jpg"  - FAIL        NoContrast Background
#  "20220417_151151.jpg"  - FAIL        NoContrast Background
#  "20220428_031457.jpg"  - FAIL        testContour
#  "20220505_172117.jpg"  - FAIL        Reflective Background
#  "20220508_171459.jpg"  - FAIL        Reflective Background
#  "20220504_120943.jpg"  - FAIL        Reflective Background
#  "20220525_135758.jpg"  - FAIL        Could not find four points of contour.
#  "20220428_031519.jpg"  - FAIL        (-215:Assertion failed) reader.ptr != NULL in function "cvDrawContours"
#  "20220525_135828.jpg"  - FAIL        (-215:Assertion failed) reader.ptr != NULL in function "cvDrawContours"
#  "20220525_135731.jpg"  - FAIL        (-215:Assertion failed) reader.ptr != NULL in function "cvDrawContours"
#  "20220525_135720.jpg"  - FAIL        (-215:Assertion failed) reader.ptr != NULL in function "cvDrawContours"
#  "20220420_213127.jpg"  - FAIL        (-215:Assertion failed) reader.ptr != NULL in function "cvDrawContours"
#  "20220425_201019.jpg"  - FAIL        (-215:Assertion failed) reader.ptr != NULL in function "cvDrawContours"
#  "20220403_171741.jpg"  - FAIL        (-215:Assertion failed) reader.ptr != NULL in function "cvDrawContours"
#  "20220425_200947.jpg"  - FAIL        (-215:Assertion failed) reader.ptr != NULL in function "cvDrawContours"
#  "20220425_201006.jpg"  - FAIL        (-215:Assertion failed) reader.ptr != NULL in function "cvDrawContours"
#  "20220504_120947.jpg"  - FAIL        (-215:Assertion failed) reader.ptr != NULL in function "cvDrawContours"
#  "20220504_120951.jpg"  - FAIL        (-215:Assertion failed) reader.ptr != NULL in function "cvDrawContours"
#  "20220428_031527.jpg"  - FAIL        (-215:Assertion failed) reader.ptr != NULL in function "cvDrawContours"
#  "walmart-template.jpg" - FAIL        AttributeError: "NoneType" object is not iterable
#  "bill3.jpg"            - FAIL        AttributeError: "NoneType" object has no attribute "group"

# successful parsed examples
# file_queue = ["20220421_001520.jpg", "20220405_232412.jpg", "20220425_200954.jpg",
#               "20220420_213104.jpg", "20220428_031510.jpg", "20220421_001513.jpg",
#               "20220418_191924.jpg", "20220420_213119.jpg", "20220504_120636.jpg",
#               "20220508_211331.jpg", "20220420_213112.jpg", "20220405_232352.jpg",
#               "20220504_120549.jpg", "20220525_135810.jpg", "20220405_232339.jpg",
#               "20220525_135836.jpg", "20220405_232446.jpg", "20220406_231142.jpg",
#               "20220425_201027.jpg", "20220428_031503.jpg", "20220504_120558.jpg",
#               "20220504_120610.jpg", "20220504_120619.jpg", "20220525_135758_e.jpg",
#               "20220428_031519_e.jpg", "20220428_031457_e.jpg"]

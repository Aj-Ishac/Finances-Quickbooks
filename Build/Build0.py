import time
import cv2

import utility
import pytesseract as tess
import pyImageProcess as pyIP
import readImage as pyRI

if __name__ == "__main__":
    tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    file_queue = utility.folder_parse("Images-Raw")
    for image_name in file_queue:
        # image_name = '20220428_031510.jpg'     # upwards = 62.9125 degrees
        # image_name = '20220405_232412.jpg'     # horizontal = 0 degrees
        # image_name = '20220421_001520.jpg'     # skewed to the left = 5.9315 degrees
        # image_name = '20220417_151151.jpg'     # upwards, heavy background - Fails, look to light preprocess before looking for contours
        total_time = 0
        image_directory = '..\\Images-Raw\\'
        image_complete_Path = image_directory + image_name

        # complete processing package
        start = time.time()
        original_image, processed_image, bordered_image = pyIP.master_image_processor(image_complete_Path)

        image_name = image_name[:-3]
        cv2.imwrite(f"..\\Images-Converted\\{image_name}_Original.jpg", original_image)
        cv2.imwrite(f"..\\Images-Converted\\{image_name}_Processed.jpg", processed_image)
        cv2.imwrite(f"..\\Images-Converted\\{image_name}_Border.jpg", bordered_image)

        # complete OCR package
        date, products, vendor, vendor_url = pyRI.master_image_read(image_name, processed_image)

        end = time.time()
        total_time += end - start
        print("Total Computation Time: ", round(total_time, 2))
        # config.saveImage('..\\Images-Converted\\', image_name, refinedImage)

# to-do:
# 2. NN text classification model
# 3. improve OCR conf
#    confidence needs to be >95%
# 4. ML model to predict product matching under respective categories
# 5. set up mySQL DB

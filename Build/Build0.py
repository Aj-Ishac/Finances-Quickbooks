import numpy as np
import cv2
import imutils
import pytesseract as tess

import utility
import pyImageProcess as pyIP
import readImage


if __name__ == "__main__":
    tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    # image_name = '20220428_031457.jpg'
    image_name = '20220428_031510(1).jpg'
    image_directory = 'E:\\Personal Projects\\ReceiptScanner\\Images-Raw\\'
    image_complete_Path = image_directory + image_name

    og_Image, skewed_Image = pyIP.skew_correct(image_complete_Path)
    processed_Image = pyIP.process_Image(skewed_Image)

    utility.checkConfidence(processed_Image)

    cv2.imshow("Original", imutils.resize(og_Image, height=650))
    cv2.imshow("Skewed", imutils.resize(skewed_Image, height=650))
    cv2.imshow("Processed", imutils.resize(processed_Image, height=650))
    cv2.waitKey(0)

    # config.saveImage('E:\\Personal Projects\\ReceiptScanner\\Images-Converted\\', image_name, refinedImage)

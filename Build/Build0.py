import numpy as np
import cv2
import imutils
import pytesseract as tess

import utility
import pyImageProcess as pyIP
import readImage as pyRI

if __name__ == "__main__":
    tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    image_name = '20220428_031510.jpg'      # upwards = 62.9125 degrees
    # image_name = '20220405_232412.jpg'     # horizontal = 0 degrees
    # image_name = '20220421_001520.jpg'     # skewed to the left = 5.9315 degrees

    image_directory = 'E:\\Personal Projects\\ReceiptScanner\\Images-Raw\\'
    image_complete_Path = image_directory + image_name

    pyIP.prep_image(image_complete_Path)

    # config.saveImage('E:\\Personal Projects\\ReceiptScanner\\Images-Converted\\', image_name, refinedImage)

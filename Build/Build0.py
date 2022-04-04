import pytesseract as tess
from PIL import Image
import pandas as pd
import numpy as np
import os
import cv2
import csv 

import config

def refineImage(imagePath):
    image_raw  = cv2.imread(imagePath, 1)
    image_edit = cv2.resize(image_raw, (0, 0), fx=2, fy=2)
    image_edit = cv2.cvtColor(image_edit, cv2.COLOR_BGR2GRAY)
    image_edit = cv2.bitwise_not(image_edit)
    thresh, image_edit = cv2.threshold(image_edit, 120, 160, cv2.THRESH_BINARY)
    ret3, image_edit = cv2.threshold(image_edit, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)  
    kernel = np.ones((2, 2),np.uint8)
    image_edit = cv2.erode(image_edit, kernel, iterations = 1)
    image_edit = cv2.medianBlur(image_edit, 1)
    image_edit = cv2.morphologyEx(image_edit, cv2.MORPH_OPEN, kernel)


    cv2.imshow('Image', image_edit)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return image_edit

def extractText(image_input, image_name):
    try:
        image_text = tess.image_to_string(image_input, timeout=5)
    except RuntimeError as timeout_error:
        return (f"Timeout Error: {image_name}")
    print(image_text)
    return image_text

def extractBounding(image_input):
    image_text = tess.image_to_string(image_input)
    image_boxes = tess.image_to_boxes(image_input)

    print(image_text)

if __name__ == "__main__":
    tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    image_name = 'walmart-template.jpg'
    #image_name = '1.jpg'
    image_directory = 'E:\\Personal Projects\\ReceiptScanner\\Images-Raw\\'
    image_complete_Path = image_directory + image_name

    refinedImage = refineImage(image_complete_Path)
    config.checkConfidence(refinedImage)
    config.saveImage('E:\\Personal Projects\\ReceiptScanner\\Images-Converted\\', image_name, refinedImage)
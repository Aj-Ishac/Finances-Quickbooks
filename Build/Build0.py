import pytesseract as tess
import numpy as np
import cv2

import config


def refine_Image(image_Path):
    image_raw = cv2.imread(image_Path, 1)
    image_edit = cv2.resize(image_raw, (0, 0), fx=2, fy=2)
    image_edit = cv2.cvtColor(image_edit, cv2.COLOR_BGR2GRAY)
    image_edit = cv2.bitwise_not(image_edit)
    thresh, image_edit = cv2.threshold(image_edit, 120, 160, cv2.THRESH_BINARY)
    ret3, image_edit = cv2.threshold(image_edit, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    kernel = np.ones((2, 2), np.uint8)
    image_edit = cv2.erode(image_edit, kernel, iterations=1)
    image_edit = cv2.medianBlur(image_edit, 1)
    image_edit = cv2.morphologyEx(image_edit, cv2.MORPH_OPEN, kernel)

    cv2.imshow('Image', image_edit)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return image_edit


def extractText(image_input):
    return tess.image_to_string(image_input, lang='eng')


def warpPerspective(image_name):

    config.initializeTrackbars()
    heightImg = 640
    widthImg = 480

    img = cv2.imread(image_name)
    img = cv2.resize(img, (widthImg, heightImg))
    imgBlank = np.zeros((heightImg, widthImg, 3), np.uint8)
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(img, (5, 5), 1)
    thres = config.valTrackbars()
    imgThreshold = cv2.Canny(imgBlur, thres[0], thres[1])
    kernel = np.ones((5, 5))
    imgDial = cv2.dilate(imgThreshold, kernel, iterations=2)
    imgThreshold = cv2.erode(imgDial, kernel, iterations=1)

    # FIND ALL COUNTOURS
    imgContours = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
    imgBigContour = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
    contours, hierarchy = cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)

    # FIND THE BIGGEST COUNTOUR
    biggest, maxArea = config.biggestContour(contours)
    if biggest.size != 0:
        biggest = config.reorder(biggest)
        cv2.drawContours(imgBigContour, biggest, -1, (0, 255, 0), 20)
        imgBigContour = config.drawRectangle(imgBigContour, biggest, 2)
        pts1 = np.float32(biggest)  # PREPARE POINTS FOR WARP
        pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

        # REMOVE 20 PIXELS FORM EACH SIDE
        imgWarpColored = imgWarpColored[20:imgWarpColored.shape[0] - 20, 20:imgWarpColored.shape[1] - 20]
        imgWarpColored = cv2.resize(imgWarpColored, (widthImg, heightImg))

        # APPLY ADAPTIVE THRESHOLD
        imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
        imgAdaptiveThre = cv2.adaptiveThreshold(imgWarpGray, 255, 1, 1, 7, 2)
        imgAdaptiveThre = cv2.bitwise_not(imgAdaptiveThre)
        imgAdaptiveThre = cv2.medianBlur(imgAdaptiveThre, 3)

        # Image Array for Display
        imageArray = ([img, imgGray, imgThreshold, imgContours],
                      [imgBigContour, imgWarpColored, imgWarpGray, imgAdaptiveThre])

    else:
        imageArray = ([img, imgGray, imgThreshold, imgContours],
                      [imgBlank, imgBlank, imgBlank, imgBlank])

    # lables = [["Original", "Gray", "Threshold", "Contours"],
    #          ["Biggest Contour", "Warp Prespective", " Warp Gray", "Adaptive Threshold"]]

    stackedImage = config.stackImages(imageArray, 0.75)
    cv2.imshow("Result", stackedImage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    image_name = 'walmart-template.jpg'
    image_directory = 'E:\\Personal Projects\\ReceiptScanner\\Images-Raw\\'
    image_complete_Path = image_directory + image_name

    # refinedImage = refineImage(image_complete_Path)
    # config.checkConfidence(refinedImage)
    # config.saveImage('E:\\Personal Projects\\ReceiptScanner\\Images-Converted\\', image_name, refinedImage)
    warpPerspective(image_complete_Path)

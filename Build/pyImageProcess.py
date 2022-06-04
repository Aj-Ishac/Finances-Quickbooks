import numpy as np
import cv2
import imutils
import math
from scipy import ndimage

import utility


def order_points(pts):
    # assign rect vertex points in ordered format
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)

    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def four_point_transform(img, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # maximum distance between bottom-right and bottom-left
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # maximum distance between the top-right and bottom-right
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # the set of destination points to obtain top-down view of the image
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # generate warped image from the perspective transform matrix
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))

    # return the warped image
    return warped


def skew_correct(img, ratio):
    orig = img.copy()
    img = imutils.resize(img, height=500)

    # grayscale, blur, and find edges
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # gray = cv2.GaussianBlur(gray, (7, 7), 0)
    edged = cv2.Canny(gray, 75, 200)

    # find the contours in the edged image, keeping only the
    # largest ones, and initialize the screen contour
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    screenCnt = None
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # if our approximated contour has four points, then we
        # can assume that we have found our ROI
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is None:
        raise Exception(("Could not find receipt outline. Try debugging your edge detection and contour steps."))

    cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 2)
    warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
    warped = cv2.resize(warped, (0, 0), fx=3.35, fy=3.35)
    return warped


def extend_rBorder(img):
    if img is None:
        return -1

    img = generate_borders(img)
    BACKGROUND_COLOR = [96, 100, 107]
    right = int(1 * img.shape[1])
    bordered_image = cv2.copyMakeBorder(img, 0, 0, 0, right, cv2.BORDER_CONSTANT, None, value=BACKGROUND_COLOR)
    return bordered_image


def generate_borders(img):
    if img is None:
        return -1

    top = int(0.0025 * img.shape[0])
    bottom = top
    left = int(0.005 * img.shape[1])
    right = left

    bordered_image = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, None, 0)
    return bordered_image


def fix_rotation(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=3)
    lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)

    angles = []
    for [[x1, y1, x2, y2]] in lines:
        # cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        angles.append(angle)

    median_angle = np.median(angles)
    print(f"Detected Angle: {median_angle:.04f}")

    # Adjust angle
    if median_angle < -45:
        median_angle = -(90 + median_angle)
    else:
        median_angle = -median_angle

    img_rotated = ndimage.rotate(img, median_angle)
    return img_rotated


def processMethod3(img):
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 85, 14)
    # 85, 14
    # remove noise
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(thresh, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    no_noise = cv2.medianBlur(image, 3)

    # thicken font
    image = cv2.bitwise_not(no_noise)
    kernel = np.ones((2, 2), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    thick_font = cv2.bitwise_not(image)

    return thick_font


def master_image_processor(image_name, path):
    # packages all pyImageProcess funcs in one general use-case call
    # edge cases will be passed through another tunnel
    image = cv2.imread(path, 1)
    image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)

    # detects angle of the image and aligns it upwards at 90degr
    rotated_Image = fix_rotation(image)

    # collects base shape of the ROI and skews edge vertices to fill return img xy axi
    # isolates ROI of surrounding background, edge case: run calc on contour area, discard all but largest
    ratio = rotated_Image.shape[0] / 500.0
    skewed_image = skew_correct(rotated_Image, ratio)

    # image processing loop to remove light/shadow effects, noise gates and folding artifacts
    processed_image = processMethod3(skewed_image)
    bordered_image = extend_rBorder(skewed_image)

    cv2.imwrite(f"..\\Images-Converted\\Original\\{image_name}_Original.jpg", skewed_image)
    cv2.imwrite(f"..\\Images-Converted\\Processed\\{image_name}_Processed.jpg", processed_image)
    cv2.imwrite(f"..\\Images-Converted\\Boredered\\{image_name}_Border.jpg", bordered_image)
    file_to_dpi = f"..\\Images-Converted\\Processed\\{image_name}_Processed.jpg"
    utility.convert_dpi(file_to_dpi)

    # cv2.imshow("Original", imutils.resize(image, height=850))
    # cv2.imshow("Skewed", imutils.resize(skewed_image, height=850))
    # cv2.imshow("Processed", imutils.resize(processed_image, height=850))

    # "s" press to save to local-saves, exits on any other key press
    utility.conditional_ExitSave("Bordered", bordered_image)
    return bordered_image


# research:
# https://nanonets.com/blog/deep-learning-ocr/#preprocessing
# http://people.tuebingen.mpg.de/burger/neural_denoising/
# EAST (Efficient accurate scene text detector)
# https://nanonets.com/blog/receipt-ocr/

import utility
import pytesseract as tess
from pytesseract import Output
import re
import cv2
import imutils

def checkConfidence(imageTemplate):
    startTime = utility.start_time()
    text = tess.image_to_data(imageTemplate, output_type='data.frame')
    text = text[text.conf != -1]
    lines = text.groupby(['page_num', 'block_num', 'par_num', 'line_num'])['text'].apply(lambda x: ' '.join(list(x))).tolist()
    confs = text.groupby(['page_num', 'block_num', 'par_num', 'line_num'])['conf'].mean().tolist()

    line_conf = []
    for i in range(len(lines)):
        if lines[i].strip():
            line_conf.append((lines[i], round(confs[i], 3)))

    if line_conf:
        average_Conf = format(sum(confs) / len(confs), ".2f")
        line_conf.append(["Average", average_Conf + "%"])

    print(*line_conf, sep='\n')
    utility.export_ConfReport(line_conf, average_Conf)


def readImage(img):
    startTime = utility.start_time()
    custom_config = r'--oem 3 --psm 6'
    source_text = tess.image_to_string(img, config=custom_config).lower()

    utility.end_time(startTime)
    return source_text


def extract_date(source_text):
    match = re.findall(r"[\d]{1,2}/[\d]{1,2}/[\d]{4}", source_text)
    return match


#https://jaafarbenabderrazak-info.medium.com/ocr-with-tesseract-opencv-and-python-d2c4ec097866
def extract_items(source_text):
    source_text = source_text


def match_items(source_text):
    #products = extract_items(source_text)
    #print(products)
    
    date = extract_date(source_text)
    print("Date: ", date)


def region_boundingBox(img):
    bounding_boxes = tess.image_to_data(img, output_type=Output.DICT)

    n_boxes = len(bounding_boxes['text'])
    for i in range(n_boxes):
        if int(bounding_boxes['conf'][i]) > 60:
            (x, y, w, h) = (bounding_boxes['left'][i], bounding_boxes['top'][i],
                            bounding_boxes['width'][i], bounding_boxes['height'][i])
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Bounding Box", imutils.resize(bounding_boxes, height=850))
    cv2.waitKey(0)


# https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html
# https://github.com/cherry247/OCR-bill-detection/blob/master/ocr.ipynb
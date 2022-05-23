import pytesseract as tess
import datetime as dt
import pandas as pd
import re

from zmq import NULL

import utility

def checkConfidence(img_name, imageTemplate):
    text = tess.image_to_data(imageTemplate, output_type='data.frame')
    text = text[text.conf != -1]
    lines = text.groupby(['page_num', 'block_num', 'par_num', 'line_num'])['text'].apply(lambda x: ' '.join(list(x))).tolist()
    confs = text.groupby(['page_num', 'block_num', 'par_num', 'line_num'])['conf'].mean().tolist()

    line_conf = []
    for i in range(len(lines)):
        if lines[i].strip():
            line_conf.append((lines[i], round(confs[i], 3)))

    if line_conf:
        avg_conf = round(sum(confs) / len(confs), 2)
        line_conf.append(["Average", avg_conf])

    print(*line_conf, sep='\n')
    # averageConf = utility.export_ConfReport(img_name, line_conf, avg_conf)
    return avg_conf


def readImage(img):
    custom_config = ('-l eng --oem 1 --psm 4')
    source_text = tess.image_to_string(img, config=custom_config).lower()
    return source_text


def extract_products(source_text):
    products_list = []
    product_regex = r"(\d+\.\d{2})(?!\d)"
    id_regex = r"\d{4,}"

    for line in source_text.split("\n"):
        # scan lines that include a price tag and tokenize [name, price]
        if re.search(product_regex, line):
            item_token = re.split(product_regex, line)[:-1]

            # scan above filtered lines for ID to discard and correct input to [name w/o ID, price]
            if re.search(id_regex, item_token[0]):
                item_token[0] = re.sub(id_regex, '', item_token[0]).strip()

            products_list.append((item_token[0].strip(), float(item_token[1])))

    # remove non-item listing and seperate tax, tip, and max(total) into their own vars
    total, tax, tip, index_of_end_product = 0, 0, 0, 0

    # list of strings to detect as extras
    str_to_catch = ["tip", "cash", "debit", "tax", "change"]
    chars_blacklist = r"^‘$-!"
    # case correct product items and break when product list detected complete
    for index, item in enumerate(products_list):
        if "total" in item[0]:
            index_of_end_product = index
            break
        elif re.compile('|'.join(str_to_catch), re.IGNORECASE).search(item[0]):
            index_of_end_product = index
            break
        else:
            # item[0] = re.sub('[^a-zA-Z0-9 \n\.]', "", products_list[0][0])
            products_list[index] = ((re.sub('[^a-zA-Z0-9 \n\.]', "", item[0])).title(), item[1])

    # iterate from n - 1 to product_list_complete index and assign/remove values accordingly
    for i in range(len(products_list) - 1, index_of_end_product - 1, -1):
        if "total" in products_list[i][0]:
            total = max(total, products_list[i][1])
        elif "tax" in products_list[i][0]:
            tax = products_list[i][1]
        elif "tip" in products_list[i][0]:
            tip = products_list[i][1]
        products_list.remove(products_list[i])

    return products_list, tax, tip, total


def extract_date(source_text):
    # new regex: [- /] delimiters, d/m/Y, m/d/Y, m/d/y, d-m-y, d-m-Y, m-d-Y, m-d-y, d-m-y
    date_regex = r"([0-9]{2}([/-][0-9]{2,4}){2,4})"

    # scan lines that include date_regex format
    date_match = re.search(date_regex, source_text)
    date_match = date_match.group(0)

    if date_match:
        dtFormat_DATE = ('%m/%d/%Y', '%d/%m/%Y', '%m/%d/%y', '%d/%m/%y',
                         '%m-%d-%Y', '%d-%m-%Y', '%m-%d-%y', '%d-%m-%y')
        dtFormat_DATETIME = ('%m/%d/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%m/%d/%y %H:%M:%S', '%d/%m/%y %H:%M:%S',
                             '%m-%d-%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S', '%m-%d-%y %H:%M:%S', '%d-%m-%y %H:%M:%S')     
        old_date = date_match
        if len(date_match) > 10:
            for i in dtFormat_DATETIME:
                if old_date != date_match:
                    break
                try:
                    date_match = dt.datetime.strptime(date_match, i).date()
                except ValueError:
                    pass
        else:
            for i in dtFormat_DATE:
                if old_date != date_match:
                    break
                try:
                    date_match = dt.datetime.strptime(date_match, i).date()
                except ValueError:
                    pass
    return date_match


def extract_vendor(source_text):
    # url_regex = r'(http:\/\/|https:\/\/)?(www.)?([a-zA-Z0-9]+)[a-zA-Z0-9]*.[‌​a-z]{3}\.([a-z]+)'
    url_regex = r'([a-z]{2,}\.[a-z]{2,6}\b)'
    url_match = re.search(url_regex, source_text)
    if url_match is not None:
        vendor_url = url_match.group(0)
        vendor_match = (vendor_url.split('.'))[0]
        return vendor_match.title()
    return "", ""


def master_image_read(img_name, img):
    # unit test of current OCR implementation
    averageConf = checkConfidence(img_name, img)
    source_text = readImage(img)

    products, tax, tip, total = extract_products(source_text)            # list(Item, Price)
    date = extract_date(source_text)                    # date_Date
    vendor = extract_vendor(source_text)    # string_Name, string_Url

    dict_dataScan = {"products": products, "date": date, "vendor": ""}
    df = pd.DataFrame(data=dict_dataScan)
    utility.df_to_cvs(img_name, averageConf, df)

    # print(source_text.strip(), end="\n")
    print(df)
    print("Tip: ", tip, " Tax: ", tax, " Total: ", total)

    return date, products, vendor, averageConf

# https://github.com/cherry247/OCR-bill-detection/blob/master/ocr.ipynb
# https://regex101.com/r/zG0fI5/1
# https://regex-generator.olafneumann.org

# ticket
# 1. price cleanup before leaving item scan
#    run a check on total detected in comparison to sum of item price values
# 2. data cleansing
#    20220420_213104 - vendor will be tied to logo NN learning else pre-address name?
# 3. current folder_files parse only looks for .jpg
# 4. run a check on /d x for multiple quantity
# 5. consider running a seperate tess config pass for logo NN learning

# characters to blacklist from name:
# this needs to run before we title()
# ‘ $ - ! ] [ ]


# research:
# http://www.haralick.org/conferences/71280952.pdf
# https://www.intechopen.com/chapters/330.json
# https://arxiv.org/pdf/1704.03155.pdf
# https://jaafarbenabderrazak-info.medium.com/ocr-with-tesseract-opencv-and-python-d2c4ec097866
# https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html


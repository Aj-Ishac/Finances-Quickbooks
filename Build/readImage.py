import pytesseract as tess
import datetime as dt
import pandas as pd
import re

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
    averageConf = utility.export_ConfReport(img_name, line_conf, avg_conf)
    return averageConf


def readImage(img):
    custom_config = ('-l eng --oem 1 --psm 4')
    source_text = tess.image_to_string(img, config=custom_config).lower()
    return source_text

# 'peddys\nharry & rock\n7906 e. harry\n\nhichita ks 67207\n316.558.9890\n\n
# server:; reg 2 04/26/2022\n91/1 8:41 ph\nquests; 2 20094\nreprint #: 1\n\n

# garlicky chicken 14.49\n
# kids bowl 1.89\n
# sd roast veg 3.99\n
# take out kids bow! 5.99\n
# heaped huznmus 7.49\n
# subtotal 33.99\n
# tax 2.59\n
# t ota | 36 . 50\n
# visa #xxxxxxxxx® ¥x4946 36.50\n
# tip 3.39\n
# total o 39.89\n\n

# auth: 05383g |\nbalance due o . 00\n\nthanks for coming in!\n
# guestsupport@meddys.com\nwxw . mneddys.com\n'

# [('Garlicky Chicxen', 14.49), ('Kids Bow!', 1.99), ('Sd Roast Veg', 3.99),
#  ('Take Out Cids Bow!)', 5.99), ('Heaped Hutmus', 7.49),
# ('Subtota]', 33.95), ('Tax', 2.55), ('Total', 36.5), ('Tip :', 3.39), ('Total Ee', 33.89)]

def extract_products(source_text):
    products_list = []
    product_regex = r"(\d+\.\d{2})(?!\d)"
    id_regex = r" \d{5,} "

    for line in source_text.split("\n"):
        # scan lines that include a price tag and tokenize [name, price]
        if re.search(product_regex, line):
            item_token = re.split(product_regex, line)[:-1]

            # scan above filtered lines for ID to discard and correct input to [name w/o ID, price]
            if re.search(id_regex, item_token[0]):
                product_name = (re.split(id_regex, item_token[0])[0]).strip()
                item_token[0] = product_name

            products_list.append((item_token[0].strip(), float(item_token[1])))

    # remove non-item listing and seperate tax, tip, and max(total) into their own vars
    total, tax, tip, index_of_end_product = 0, 0, 0, 0
    str_to_catch = ["tip", "cash", "debit", "tax", "change"]
    for index, item in enumerate(products_list):
        if "total" in item[0]:
            index_of_end_product = index
            break
        elif re.compile('|'.join(str_to_catch), re.IGNORECASE).search(item[0]):
            index_of_end_product = index
            break
        else:
            products_list[index] = (item[0].title(), item[1])

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
    # collect text that matches date format m/d/Y
    # [\d]{1,2}/[\d]{1,2}/[\d]{4}
    # old regex: only counts mm/dd/yyyy
    # new regex: [- /.] delimiters, dd/mm/yy, dd/mm/yyyy, mm/dd/yy, mm/dd/yyyy
    date_regex = r"([0-9]{2}(/[0-9]{2,4}){2,4})"

    dates_list = []
    for line in source_text.split("\n"):
        # scan lines that include date format [dd/mm/yyyy]
        if re.match(date_regex, line):
            date = line
            break

    if date:
        dtFormat_DATE = ('%m/%d/%Y', '%d/%m/%Y', '%m/%d/%y', '%d/%m/%y',
                         '%m-%d-%Y', '%d-%m-%Y', '%m-%d-%y', '%d-%m-%y')
        dtFormat_DATETIME = ('%m/%d/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%m/%d/%y %H:%M:%S', '%d/%m/%y %H:%M:%S',
                             '%m-%d-%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S', '%m-%d-%y %H:%M:%S', '%d-%m-%y %H:%M:%S')     
        old_date = date
        if len(date) == 10 or len(date) == 8:
            for i in dtFormat_DATE:
                if old_date != date:
                    break
                try:
                    date = dt.datetime.strptime(date, i).date()
                except ValueError:
                    pass
        else:
            for i in dtFormat_DATETIME:
                if old_date != date:
                    break
                try:
                    date = dt.datetime.strptime(date, i).date()
                except ValueError:
                    pass

    return date


def extract_vendor(source_text):
    # url_regex = r'(http:\/\/|https:\/\/)?(www.)?([a-zA-Z0-9]+)[a-zA-Z0-9]*.[‌​a-z]{3}\.([a-z]+)'
    url_regex = r'([a-z]{2,}\.[a-z]{2,6}\b)'
    url_match = re.search(url_regex, source_text)
    if url_match is not None:
        vendor_url = url_match.group(0)
        vendor_match = (vendor_url.split('.'))[0]
        return vendor_match.title(), vendor_url
    return None


def master_image_read(img_name, img):
    # unit test of current OCR implementation
    averageConf = checkConfidence(img_name, img)
    source_text = readImage(img)

    products, tax, tip, total = extract_products(source_text)            # list(Item, Price)
    date = extract_date(source_text)                    # date_Date
    vendor, vendor_url = extract_vendor(source_text)    # string_Name, string_Url

    dict_dataScan = {"products": products, "date": date, "vendor": vendor, "url": vendor_url}
    df = pd.DataFrame(data=dict_dataScan)

    # print(source_text.strip(), end="\n")
    print(df)
    print("Tip: ", tip, " Tax: ", tax, " Total: ", total)

    return date, products,  vendor, vendor_url


# https://github.com/cherry247/OCR-bill-detection/blob/master/ocr.ipynb
# https://regex101.com/r/zG0fI5/1

# ticket
# 1. price cleanup before leaving item scan
# 2. merge regex base lookup
# 3. current folder_files parse only looks for .jpg

# research:
# http://www.haralick.org/conferences/71280952.pdf
# https://www.intechopen.com/chapters/330.json
# https://arxiv.org/pdf/1704.03155.pdf
# https://jaafarbenabderrazak-info.medium.com/ocr-with-tesseract-opencv-and-python-d2c4ec097866
# https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html

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
    # collect lines that include price points with strictly two decimal points
    product_regex = r"\D{3,} \d+\.\d\d(?!\d)\n?"
    product_matches = re.findall(product_regex, source_text)

    # parses the above into list[(product_name, product_price)]
    products, price_regex = [], r"(\d+\.\d{1,2})"
    for item in product_matches:
        tokens = re.split(price_regex, item)
        products.append((tokens[0].strip().replace('\n', ''), float(tokens[1])))

    total, tip, tax = 0, 0, 0
    # remove non-item listing and seperate tax, tip, and max(total) into their own vars
    for index, item in reversed(list(enumerate(products))):
        if "total" in item[0]:
            total = max(total, item[1])
            products.remove(item)
        elif "tip" in item[0]:
            tip = item[1]
            products.remove(item)
        elif "tax" in item[0]:
            tax = item[1]
            products.remove(item)
        else:
            products[index] = (item[0].title(), item[1])

    # products.append(("tax", tax)) if tax > 0 else print("Tax does not exist.")
    # products.append(("tip", tip)) if tip > 0 else print("tip does not exist.")
    # products.append(("total", total)) if total > 0 else print("total does not exist.")

    summed_total = sum([item[1] for item in products]) + tax
    if total != summed_total:
        total = summed_total
        # raise Exception("OCR sum(products)/total mismatch!")

    return products, tax, tip, total


def extract_date(source_text):
    # collect text that matches date format m/d/Y
    # [\d]{1,2}/[\d]{1,2}/[\d]{4}
    # old regex: only counts mm/dd/yyyy
    # new regex: [- /.] delimiters, dd/mm/yy, dd/mm/yyyy, mm/dd/yy, mm/dd/yyyy
    date_regex = r"[\d]{1,2}/[\d]{1,2}/[\d]{4}"
    matches = re.findall(date_regex, source_text)

    dates_list = []
    [dates_list.append(dt.datetime.strptime(match, '%m/%d/%Y')) for match in matches]

    if len(dates_list) > 0:
        date = (min(dates_list)).date()
        return date
    return None


def extract_vendor(source_text):
    url_regex = r'(http:\/\/|https:\/\/)?(www.)?([a-zA-Z0-9]+)[a-zA-Z0-9]*.[‌​a-z]{3}\.([a-z]+)'
    url_match = re.search(url_regex, source_text)
    if url_match is not None:
        url_match = url_match.group(0)
        vendor_match = (url_match.split('.')[:1])[0]
        return vendor_match.title(), url_match
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

    return date, products, vendor, vendor_url, averageConf


# https://github.com/cherry247/OCR-bill-detection/blob/master/ocr.ipynb
# https://regex101.com/r/zG0fI5/1

# ticket
# 1. price cleanup before leaving item scan
# 2. expand on date regex identifier
#    [- /.] delimiters, dd/mm/yy, dd/mm/yyyy, mm/dd/yy, mm/dd/yyyy
# 3. current folder_files parse only looks for .jpg

# research:
# http://www.haralick.org/conferences/71280952.pdf
# https://www.intechopen.com/chapters/330.json
# https://arxiv.org/pdf/1704.03155.pdf
# https://jaafarbenabderrazak-info.medium.com/ocr-with-tesseract-opencv-and-python-d2c4ec097866
# https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html

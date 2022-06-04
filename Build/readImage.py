import pytesseract as tess
import datetime as dt
import pandas as pd
import cv2
import re

import utility

def checkConfidence(imageTemplate):
    text = tess.image_to_data(imageTemplate, output_type="data.frame")
    text = text[text.conf != -1]
    lines = text.fillna("").groupby(["page_num", "block_num", "par_num", "line_num"])["text"].apply(lambda x: " ".join(list(x))).tolist()
    confs = text.groupby(["page_num", "block_num", "par_num", "line_num"])["conf"].mean().tolist()

    line_conf = []
    for i in range(len(lines)):
        if lines[i].strip():
            line_conf.append((lines[i], round(confs[i], 3)))

    if line_conf:
        avg_conf = round(sum(confs) / len(confs), 2)
        line_conf.append(["Average", avg_conf])

        print(*line_conf, sep="\n")
        return avg_conf
    return


def readImage(img):

    #     Page segmentation modes:
    #   0    Orientation and script detection (OSD) only.
    #   1    Automatic page segmentation with OSD.
    #   2    Automatic page segmentation, but no OSD, or OCR.
    #   3    Fully automatic page segmentation, but no OSD. (Default)
    #   4    Assume a single column of text of variable sizes.
    #   5    Assume a single uniform block of vertically aligned text.
    #   6    Assume a single uniform block of text.
    #   7    Treat the image as a single text line.
    #   8    Treat the image as a single word.
    #   9    Treat the image as a single word in a circle.
    #  10    Treat the image as a single character.
    #  11    Sparse text. Find as much text as possible in no particular order.
    #  12    Sparse text with OSD.
    #  13    Raw line. Treat the image as a single text line,
    #        bypassing hacks that are Tesseract-specific.

    custom_config = ("-l eng --oem 1 --psm 4")
    source_text = tess.image_to_string(img, config=custom_config)
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
                item_token[0] = re.sub(id_regex, "", item_token[0]).strip()

            products_list.append((item_token[0].strip(), float(item_token[1])))

    # remove non-item listing and seperate tax, tip, and max(total) into their own vars
    total, tax, tip, index_of_end_product = 0, 0, 0, 0

    # list of strings to detect as extras
    str_to_catch = ["tip", "cash", "debit", "tax", "change", "sale"]
    # refine product name data and mark the end point of when our product listing is determined complete
    for index, item in enumerate(products_list):
        if "total" in item[0].lower():
            index_of_end_product = index
            break
        elif re.compile("|".join(str_to_catch), re.IGNORECASE).search(item[0].lower()):
            index_of_end_product = index
            break
        else:
            # removme all chars not present in this regex list: [^a-zA-Z0-9 \n]
            temp_item = (re.sub("[^a-zA-Z0-9 \n]", " ", item[0]))
            products_list[index] = (" ".join(temp_item.split()).title(), item[1])

    # iterate from [n - 1 to product_list_complete index] and assign/remove values accordingly
    for i in range(len(products_list) - 1, index_of_end_product - 1, -1):
        if "total" in products_list[i][0].lower():
            total = max(total, products_list[i][1])
        elif "tax" in products_list[i][0].lower():
            tax = products_list[i][1]
        elif "tip" in products_list[i][0].lower():
            tip = products_list[i][1]
        products_list.remove(products_list[i])

    return products_list, tax, tip, total


def extract_date(source_text):
    # new regex: [- /] delimiters, d/m/Y, m/d/Y, m/d/y, d-m-y, d-m-Y, m-d-Y, m-d-y, d-m-y
    date_regex = r"([0-9]{2}([/-][0-9]{2}){2,4})"

    # scan lines that include date_regex format
    try:
        date_match = re.search(date_regex, source_text)
        date_match = date_match.group(0)
    except BaseException:
        date_match = "NULL"

    if date_match != "NULL":
        dtFormat_DATE = ["%m/%d/%Y", "%d/%m/%Y", "%m/%d/%y", "%d/%m/%y"]
        dtFormat_DATE2 = ["%m-%d-%Y", "%d-%m-%Y", "%m-%d-%y", "%d-%m-%y"]
        dtFormat_DATETIME = ["%m/%d/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%m/%d/%y %H:%M:%S", "%d/%m/%y %H:%M:%S"]
        dtFormat_DATETIME2 = ["%m-%d-%Y %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%m-%d-%y %H:%M:%S", "%d-%m-%y %H:%M:%S"]

        applicable_dtFormat = []
        old_date = date_match
        if len(date_match) > 10:
            if "-" in date_match:
                applicable_dtFormat = dtFormat_DATETIME2
            else:
                applicable_dtFormat = dtFormat_DATETIME
        else:
            if "-" in date_match:
                applicable_dtFormat = dtFormat_DATE2
            else:
                applicable_dtFormat = dtFormat_DATE

        for i in applicable_dtFormat:
            if old_date != date_match:
                break
            try:
                date_match = dt.datetime.strptime(date_match, i).date()
            except ValueError:
                pass

    return date_match


def extract_vendor(source_text):
    url_regex = r"([a-z]{2,}\.[a-z]{2,6}\b)"
    url_match = re.search(url_regex, source_text)
    if url_match is not None:
        vendor_url = url_match.group(0)
        vendor_match = (vendor_url.split("."))[0]
        return "TEMP_VENDOR"
        return vendor_match.title()

    return "TEMP_VENDOR"


def master_image_read(img_name, img):
    # unit test of current OCR implementation
    averageConf = checkConfidence(img)
    source_text = readImage(img)

    products, tax, tip, total = extract_products(source_text)   # list(Item, Price)
    date_of_scan = extract_date(source_text)                    # date_Date
    vendor_name = extract_vendor(source_text)                   # string_Name

    scan_results = []
    for item in products:
        item_data = []
        item_data.append(item[0])
        item_data.append(item[1])
        item_data.append(date_of_scan)
        item_data.append(vendor_name)
        scan_results.append(item_data)

    dict_dataScan = {"product": products, "date": date_of_scan, "vendor": vendor_name}
    df = pd.DataFrame(data=dict_dataScan)
    utility.df_to_cvs(img_name, df, averageConf)

    print(df)
    print("Tip: ", tip, " Tax: ", tax, " Total: ", total)

    # utility.df_to_cvs(img_name, overall_df)
    return scan_results, averageConf

# ticket
# 1. price cleanup before leaving item scan
#    run a check on total detected in comparison to sum of item price values
#    if total_price of scan is low confidence, adjust by sum(scanned products)
# 2. data cleansing
#    20220420_213104 - vendor will be tied to logo NN learning else pre-address name?
# 3. consider running a seperate tess config pass for logo NN learning
# 4. blacklist false positives fix:
#    scan for caps sensitive blacklisted words before we .lower() evrything

# notes:
# 1. if price is associated with an empty product name, indicates products are not on the same line as price -> call for supervision
# 2. current folder_files parse only looks for .jpg, expand to png after edge case cleanup

# research:
# http://www.haralick.org/conferences/71280952.pdf
# https://www.intechopen.com/chapters/330.json
# https://arxiv.org/pdf/1704.03155.pdf
# https://jaafarbenabderrazak-info.medium.com/ocr-with-tesseract-opencv-and-python-d2c4ec097866
# https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html

# https://arxiv.org/pdf/2103.14470v1.pdf !!
# https://openreview.net/pdf?id=SJl3z659UH !!
# https://arxiv.org/pdf/2103.10213.pdf !!


# https://ec.europa.eu/eurostat/documents/54431/11489222/6+Receipt+scan+analysis.pdf
# https://pyimagesearch.com/2021/10/27/automatically-ocring-receipts-and-scans/ !!!

# https://stackoverflow.com/questions/53761979/how-can-i-train-my-python-based-ocr-with-tesseract-to-train-with-different-natio
# https://i.ytimg.com/vi/1ns8tGgdpLY/maxresdefault.jpg
# https://pretius.com/blog/ocr-tesseract-training-data/
# https://stackoverflow.com/questions/41295527/tesseract-training-for-a-new-font

# https://github.com/cherry247/OCR-bill-detection/blob/master/ocr.ipynb
# https://regex101.com/r/zG0fI5/1
# https://regex-generator.olafneumann.org

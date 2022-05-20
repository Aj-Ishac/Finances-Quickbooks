import utility
import pytesseract as tess
import re
import datetime as dt

def checkConfidence(imageTemplate):
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


# 'meddys\nveddys\nharry & rock\n7906 £. harry\nwichita ks 67207\n316.558.9390\n
# server: reg 2 04/26/2022\n91/1 8:41 ph\nguests; 2 20094 |\nreprint #: 1\n
# garlicky chicxen 14.49\nkids bow! 1.99\nsd roast veg 3.99\ntake out cids bow!) 5.99\n
# heaped hutmus 7.49\nsubtota] 33.95\ntax 2.55\ntotal 36.50\n
# visa sxxxxxxxxxreai9ag 36.50\ntip : 3.39\ntotal ee 33.89\nauth:053830\n
# balance due o.0a00\nthanks for coming in!\nguestsupport@meddys .com\nwvly,meddys .com\n'

# [('Garlicky Chicxen', 14.49), ('Kids Bow!', 1.99), ('Sd Roast Veg', 3.99),
#  ('Take Out Cids Bow!)', 5.99), ('Heaped Hutmus', 7.49), ('Subtota]', 33.95),
#  ('Tax', 2.55), ('Total', 36.5), ('Tip :', 3.39), ('Total Ee', 33.89)]

# get rid of:
# ('Subtota]', 33.95),
# ('Tax', 2.55),
# ('Total', 36.5),
# ('Tip :', 3.39),
# ('Total Ee', 33.89)]

def extract_items(source_text):
    # collect lines that include price points with strictly two decimal points
    product_regex = r"\D{3,} \d+\.\d\d(?!\d)\n?"
    product_matches = re.findall(product_regex, source_text)

    # parses the above into list[(product_name, product_price)]
    products, price_regex = [], r"(\d+\.\d{1,2})"
    for item in product_matches:
        tokens = re.split(price_regex, item)
        products.append((tokens[0].rstrip().replace('\n', '').title(), float(tokens[1])))
    return products


def extract_date(source_text):
    # collect text that matches date format m/d/Y
    regex = r"[\d]{1,2}/[\d]{1,2}/[\d]{4}"
    matches = re.findall(regex, source_text)

    dates_list = []
    [dates_list.append(dt.datetime.strptime(match, '%m/%d/%Y')) for match in matches]
    date = (min(dates_list)).date()
    return date


def match_items(source_text):
    products = extract_items(source_text)
    date = extract_date(source_text)
    return products, date

def master_image_read(img):
    # unit test of current OCR implementation
    checkConfidence(img)
    source_text = readImage(img)
    products, date = match_items(source_text)

    print("-----Item Matches-----")
    print("Products: \n", products, end='\n')
    print("Date: ", date, end='\n')

    return date, products


# https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html
# https://github.com/cherry247/OCR-bill-detection/blob/master/ocr.ipynb
# https://regex101.com/r/zG0fI5/1
# https://jaafarbenabderrazak-info.medium.com/ocr-with-tesseract-opencv-and-python-d2c4ec097866

# ticket
# 1. convert extract_date() data from string to date format
#    if more than one date extracted, look for the earlier data
# 2. figure out a way to discard non-item products
#    data cleanup on products
# 3. add method to look for alt date format
#    (/ - .) (m d y) and (d m y) 

# research:
# http://www.haralick.org/conferences/71280952.pdf
# https://www.intechopen.com/chapters/330.json
# https://arxiv.org/pdf/1704.03155.pdf
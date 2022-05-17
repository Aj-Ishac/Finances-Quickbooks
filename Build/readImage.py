import utility
import pytesseract as tess


def checkConfidence(imageTemplate):
    text = tess.image_to_data(imageTemplate, output_type='data.frame')
    text = text[text.conf != -1]
    lines = text.groupby(['page_num', 'block_num', 'par_num', 'line_num'])['text'].apply(lambda x: ' '.join(list(x))).tolist()
    confs = text.groupby(['page_num', 'block_num', 'par_num', 'line_num'])['conf'].mean().tolist()

    line_conf = []
    for i in range(len(lines)):
        if lines[i].strip():
            line_conf.append((lines[i], round(confs[i], 3)))

    average_Conf = format(sum(confs) / len(confs), ".2f")
    line_conf.append(["Average", average_Conf + "%"])

    print(*line_conf, sep='\n')
    utility.export_ConfReport(line_conf, average_Conf)


def readImage(img):
    custom_config = r'--oem 3 --psm 6'
    tess.image_to_string(img, config=custom_config)
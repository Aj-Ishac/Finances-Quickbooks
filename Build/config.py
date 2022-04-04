from ctypes import sizeof
from distutils.command.config import config
import pytesseract as tess
from PIL import Image
import numpy as np
import pandas as pd
import os
import cv2
import csv 

def checkConfidence(imageTemplate):
    text = tess.image_to_data(imageTemplate, output_type= 'data.frame')
    text = text[text.conf != -1]
    lines = text.groupby(['page_num', 'block_num', 'par_num', 'line_num'])['text'].apply(lambda x: ' '.join(list(x))).tolist()
    confs = text.groupby(['page_num', 'block_num', 'par_num', 'line_num'])['conf'].mean().tolist()

    line_conf = []
    for i in range(len(lines)):
        if lines[i].strip():
            line_conf.append((lines[i], round(confs[i],3)))

    average_Conf = format(sum(confs) / len(confs),".2f")
    print(*line_conf, sep = '\n')
    export_ConfReport(line_conf, average_Conf)

def export_ConfReport(list, prefix):
    indexNum = 0
    path = 'E:\\Personal Projects\\ReceiptScanner\\Confidence Reports\\'
    #increment fileindex if filename exists, create directory if needed
    if not os.path.isdir(path):
        os.makedirs(path)
    while os.path.exists(f"{path}confReporA{prefix}_%s.csv" %indexNum):
        indexNum += 1
        
    #confReportA78_0.csv
    prefix = prefix.rpartition('.')[0]
    file = open((f"{path}confReportA{prefix}_%s.csv" %indexNum), 'w', newline= '')
    with file:
        write = csv.writer(file)
        write.writerows(list)

    print(f'------------------------------------\n\
    CSV Export: {f"confReportA{prefix}_%s.csv" %indexNum} \n\
    Average Confidence: {prefix}')

def saveImage(filePath, imageName, fileName):
    indexNum = 0
    prefix_name = imageName.partition('.')[0]
    postfix_name = imageName.partition('.')[2]

    if not os.path.isdir(filePath):
        os.makedirs(filePath)
    while(os.path.exists(f'{filePath}{prefix_name}_Edit%s.{postfix_name}'%indexNum)):
        indexNum += 1
    
    edited_name = (f'{prefix_name}_Edit%s.{postfix_name}'%indexNum)
    cv2.imwrite(f'{filePath}{edited_name}', fileName)



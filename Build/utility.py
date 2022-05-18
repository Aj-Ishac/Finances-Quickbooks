import os
import cv2
import csv


def export_ConfReport(list, averageConf):
    indexNum = 0
    path = 'E:\\Personal Projects\\ReceiptScanner\\Confidence Reports\\'
    averageConf = averageConf.rpartition('.')[0]

    # increment fileindex if filename exists, create directory if needed
    if not os.path.isdir(path):
        os.makedirs(path)

    while os.path.exists(f'{path}confReport_%s.csv' % indexNum):
        indexNum += 1

    file = open((f"{path}confReport_%s.csv" % indexNum), 'w', newline='')
    with file:
        write = csv.writer(file)
        write.writerows(list)

    print('------------------------------------')
    print(f'CSV Export: confReport_%s.csv' % indexNum)
    print(f'Average Confidence: {averageConf}%\n')


def saveImage(filePath, imageName, fileName):
    indexNum = 0
    prefix_name = imageName.partition('.')[0]
    postfix_name = imageName.partition('.')[2]

    if not os.path.isdir(filePath):
        os.makedirs(filePath)
    while(os.path.exists(f'{filePath}{prefix_name}_Edit%s.{postfix_name}' % indexNum)):
        indexNum += 1
    edited_name = (f'{prefix_name}_Edit%s.{postfix_name}' % indexNum)
    cv2.imwrite(f'{filePath}{edited_name}', fileName)

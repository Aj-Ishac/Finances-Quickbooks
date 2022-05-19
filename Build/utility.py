import os
import cv2
import csv
import sys
import time

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
    print('CSV Export: confReport_%s.csv' % indexNum)
    print(f'Average Confidence: {averageConf}%\n')


def conditional_ExitSave(image_name, image_array, folder_name='Local-Saves'):
    file_name = f'{image_name}'
    file_Path = f'..\\{folder_name}\\'
    postfix = 'jpg'

    k = cv2.waitKey(0)
    if k == ord('s'):       # if 's' key was pressed then save and exit
        indexNum = 0
        if not os.path.isdir(file_Path):
            os.makedirs(file_Path)
        while(os.path.exists(f'{file_Path}{file_name}_%s.{postfix}' % indexNum)):
            indexNum += 1

        edited_name = (f'{file_Path}{file_name}_%s.{postfix}' % indexNum)

        cv2.imwrite(f'{file_Path}{edited_name}', image_array)
        print(f'Mannual Export: {file_Path}{file_name}')
        cv2.destroyAllWindows()
    else:
        cv2.destroyAllWindows()


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


def WHERE(back=0):
    frame = sys._getframe(back + 1)
    return "%s/line%s -> %s()" % (os.path.basename(frame.f_code.co_filename),
                                  frame.f_lineno, frame.f_code.co_name)


def start_time():
    return time.time()


def end_time(start):
    end = time.time()
    print('------------------------------------')
    print(WHERE(1))
    print(f'Computation Time: {round((end - start), 2)}s\
          \n------------------------------------')

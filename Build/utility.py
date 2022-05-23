import os
import cv2
import csv
import sys
import time
from pathlib import Path
from PIL import Image


def export_ConfReport(img_name, list, averageConf):
    path = 'E:\\Personal Projects\\ReceiptScanner\\Confidence Reports\\'
    averageConf = int(averageConf)
    img_name = img_name[:-3]

    if not os.path.isdir(path):
        os.makedirs(path)

    file = open((f"{path}{img_name}_{averageConf}.csv"), 'w', encoding="utf-8", newline='')
    with file:
        write = csv.writer(file)
        write.writerows(list)

    print('------------------------------------')
    print(f'CSV Export: {img_name}_{averageConf}.csv')
    print(f'Average Confidence: {averageConf}%\n')
    return averageConf


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
    # returns func name where WHERE is run
    # 1 as param to return parent func
    frame = sys._getframe(back + 1)
    return "%s/line%s -> %s()" % (os.path.basename(frame.f_code.co_filename),
                                  frame.f_lineno, frame.f_code.co_name)


def start_time():
    # mark start time
    return time.time()


def end_time(start):
    # mark end time and print computation time and where func resides
    end = time.time()
    print('------------------------------------')
    print(WHERE(1))
    print(f'Computation Time: {round((end - start), 2)}s\
          \n------------------------------------')


def folder_parse(folder_name):
    file_queue = []
    for file in os.listdir(f"..\\{folder_name}"):
        if file.endswith(".jpg"):
            file_name = (os.path.join("..\\Images-Raw", file))[14:]
            file_queue.append(file_name)

    return file_queue


def writer(image_name, file_name, averageConf):

    index = 0
    f = open(file_name, "a")
    f.write(f"{str(index)} - {image_name} PASS {str(averageConf)}%\n")
    print(f"{str(index)} - {image_name} PASS {str(averageConf)}%")
    f.close()
    index += 1


def convert_dpi(image_complete_path):
    im = Image.open(image_complete_path)
    im.save(image_complete_path, dpi=(300, 300))


def df_to_cvs(img_name, averageConf, df):
    filepath = Path(f'../Confidence Reports/{img_name}_df{round(averageConf, 0)}.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath)
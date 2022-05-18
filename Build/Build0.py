import pytesseract as tess
import pyImageProcess as pyIP

if __name__ == "__main__":
    tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # image_name = '20220428_031510.jpg'     # upwards = 62.9125 degrees
    # image_name = '20220405_232412.jpg'     # horizontal = 0 degrees
    image_name = '20220421_001520.jpg'     # skewed to the left = 5.9315 degrees
    # image_name = '20220417_151151.jpg'     # upwards, heavy background - Fails, look to light preprocess before looking for contours

    image_directory = 'E:\\Personal Projects\\ReceiptScanner\\Images-Raw\\'
    image_complete_Path = image_directory + image_name

    pyIP.prep_image(image_complete_Path)

    # config.saveImage('E:\\Personal Projects\\ReceiptScanner\\Images-Converted\\', image_name, refinedImage)

# to-do:
# 1. image_process
# 2. NN text classification model
# 3. parse [merchant, date, products, prices] and regex data
#    confidence needs to be >95%, can also compare OCR totalPrice to mannual sum of individual product prices as additional success check
# 4. ML model to predict product matching under respective categories
# 5. set up mySQL DB

# tickets:
# 1. skew_correct has the tendency of picking incorrect ROI to process when lighting is insufficient
#    fix: run calc on all image contours and define ROI by largest contour area
# 2. fix_rotation() leans rotation intent towards 90deg upward state
#    if image is received upside down, end result will still be upside down with rotation fix
#    fix: may need to run a pass on detecting angle of text and invert y-scale if flip detected

import pytesseract as tess
import pyImageProcess as pyIP
import readImage as pyRI

if __name__ == "__main__":
    tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    image_name = '20220428_031510.jpg'     # upwards = 62.9125 degrees
    # image_name = '20220405_232412.jpg'     # horizontal = 0 degrees
    # image_name = '20220421_001520.jpg'     # skewed to the left = 5.9315 degrees
    # image_name = '20220417_151151.jpg'     # upwards, heavy background - Fails, look to light preprocess before looking for contours

    image_directory = '..\\Images-Raw\\'
    image_complete_Path = image_directory + image_name

    # complete processing package via pyImageProcess
    original_image, processed_image = pyIP.master_image_prep(image_complete_Path)

    # unit test of current OCR implementation
    # pyRI.checkConfidence(processed_image)

    source_text = pyRI.readImage(processed_image)
    print(source_text)

    pyRI.region_boundingBox(processed_image)
    # config.saveImage('..\\Images-Converted\\', image_name, refinedImage)

# to-do:
# 2. NN text classification model
# 3. parse [merchant, date, products, prices] and regex data
#    confidence needs to be >95%, can also compare OCR totalPrice to mannual sum of individual product prices as additional success check
# 4. ML model to predict product matching under respective categories
# 5. set up mySQL DB

import cv2
import numpy as np
from base64 import b64decode
from imutils import contours, grab_contours
import settings

def get_image_from_filename(filename):
    """
    Given a filename, returms RGB image as a np.ndarray

    Parameters
    ----------
    filename: str
        image file name
    Returns
    -------
    imgRGB: np.ndarray
        RGB image as a np.ndarray
    """

    filename = settings.invoce_images_folder + filename
    img = cv2.imread(filename)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return imgRGB
    
def decode_image(image_encoded):
    """
    Decode image from encoded string

    Parameters
    ----------
    image_encoded: str
        encoded string
    Returns
    -------
    imageRGB: np.ndarray
        RGB image as a np.ndarray
    """
    encoded = b64decode(image_encoded[22:])
    image = cv2.imdecode(np.frombuffer(encoded,np.uint8), cv2.IMREAD_COLOR)
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return np.array(imageRGB)

def get_contours(img):
    """
    Get all the countours present in a given img

    Parameters
    ----------
    img: np.ndarray
        RGB image as a np.ndarray
    Returns
    -------
    contourss: countours
        Each contour is stored as a point vector.

    """
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (45,1))
    detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    
    # Create structure element for extracting vertical lines through morphology operations
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 10))

    # Apply morphology operations
    thresh = cv2.erode(thresh, verticalStructure)
    thresh = cv2.dilate(thresh, verticalStructure)
    
    contourss = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contourss = grab_contours(contourss)  
    (contourss, _) = contours.sort_contours(contourss)
    return contourss

def get_scaled_height(img, contourss, max_value, display_image:bool=False):
    """
    Get all the countours present in a given img

    Parameters
    ----------
    img: np.ndarray
        RGB image as a np.ndarray
    contourss: countours
        Each contour is stored as a point vector.
    max_value: int
        value that will be used to scale the heights
    display_image: bool, default: False
        Wheter or not display the image with the rect found 
    Returns
    -------
    scaled_heights: list
        list with the scaled heights
    """
    if display_image:
        orig = img.copy()

    img_height = img.shape[0]
    scaled_heights = []
    for countour in contourss:
        if cv2.contourArea(countour) > 500:
            if display_image:
                x,y,w,h = cv2.boundingRect(countour)
                cv2.rectangle(orig,(x,y), (x+w,y+h,),(255, 0, 0), 3)
            else:
                _,_,_,h = cv2.boundingRect(countour)
            scaled_heights.append((h*max_value)//img_height)
    if display_image:
        cv2.imshow('image', orig)
        cv2.waitKey()
    return scaled_heights
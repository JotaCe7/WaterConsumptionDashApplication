import sys
import pytesseract
from pytesseract import Output
import settings


def set_tesseract_cmd():
     # Set tesseract_cmd in case running on Windows
    if sys.platform == 'win32':
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

def get_data_from_image(img):
    """
    Get data from all the texts in img as a dictionary

    Parameters
    ----------
    img: np.ndarray
        RGB image as a np.ndarray
    Returns
    -------
    data_dict: ndictionary
        Data from all the texts in img
    """
    # To speed up the process we are getiing only data from an upper
    # left regio of the image (We know in advamce that there is located
    # the known text -postal code-)
    data_dict = pytesseract.image_to_data(img[:600,:1800], output_type=Output.DICT)
    return data_dict

def image_to_string(img):
    """
    Get the thect in img as a string

    Parameters
    ----------
    img: np.ndarray
        RGB image as a np.ndarray
    Returns
    -------
    text: string
        Data from all the texts in img
    """
    return pytesseract.image_to_string(img, config='--psm 6').replace("\n\f", "").split("\n")
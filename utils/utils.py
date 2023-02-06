import os
import pandas as pd
import json
from utils.pytesseract_utils import get_data_from_image
from utils.cv2_utils import get_contours, get_scaled_height, get_image_from_filename
import settings

def get_pie_slice(text:str):
    """
    Gets a string ontaining pie chart slice description and returns a 
    substring from the beginning to stop charcter
    Eg. 'WATER BASE $80.60" -> "WATER BASE"

    Parameters
    ----------
    text: str
        string containing pie chart slice description

    Returns
    -------
    text:str
        pie chart slice description
    """
    # Possible stop characters
    stop_charcaters ='0123456789$'
    for i, c in enumerate(text):
        if c in stop_charcaters:
            return text[:i-1]
    return text

def get_invoice_images():
    """
    Returns all the files in settings.invoce_images_folder with valid extension

    Parameters
    ----------
    Nothing

    Returns
    -------
    list
        list with invoice file names in invoice folder     
    """
    return [file for file in os.listdir(settings.invoce_images_folder) if os.path.splitext(file)[1].lower() in settings.allowed_extensions ]

def get_shapes(filename:str):
    """
    Having a known string in an image file, returns the desphase in pixels between
    the bounding box from the shapes csv and the bounding box obtained by obtaining
    the data from the image

    Parameters
    ----------
    filename: str
        image file name
    Returns
    -------
    (shapes, img): tuple(pd.Dataframe, np.ndarray)
        shapes: Shapes dataframe with corrected bounding box wrt the img
        img: image as an np.ndarray from filename
    """

    # Get image from filename
    img = get_image_from_filename(filename)

    # Get data from image
    d = get_data_from_image(img)

    # Calculate coordinates of where in the image is located settings.postal_code 
    dfCoord=pd.DataFrame.from_dict(d)
    dfCoord = dfCoord[(dfCoord['text'] == settings.postal_code)]
    dfCoord=dfCoord.iloc[0]
    xCoor, yCoor = dfCoord['left'], dfCoord['top']

    # Read the settings.shapes_csv file and adjust bbox coordinates
    shapes=pd.read_csv(settings.shapes_csv)
    row_1=shapes.iloc[0]
    xCoor, yCoor = xCoor-row_1['x0'], yCoor-row_1['y0']
    
    shapes[['x0','x1']] = shapes[['x0','x1']] + xCoor
    shapes[['y0','y1']] = shapes[['y0','y1']] + yCoor
    # Convert shapes['line'] from str to dictionary
    shapes['line'] =  shapes['line'].apply( lambda s: json.loads(s.replace("'",'"')) )

    return shapes, img


def get_history_consumption(img_hc, max_consumption, display_image:bool = False):
    """
    Get the consumptions from image with History Consumption

    Parameters
    ----------
    img_hc: np.ndarray
        RGB image as a np.ndarray of the History Consumption
    contourss: countours
        Each contour is stored as a point vector.
    max_consumption: int
        value that will be used to scale the consumptions
    display_image: bool, default: False
        Wheter or not display the image with the rect found 
    Returns
    -------
    consumptions: list
        list with the scaled consumptions
    """

    # Get contours
    contourss = get_contours(img_hc)
    
    # Get consumptions
    consumptions = get_scaled_height(img_hc, contourss, max_consumption, display_image)
    
    return consumptions






    

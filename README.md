# WATER CONSUMPTION DASH APPLICATION

## Loading Invoice Image
This application allows you to choose an image of an invoice from a predefined folder.
It then will then display that image and show draw bounding boxes stored in a .csv file.

## Process Image
Clickink the Process button will get the information from the invoice image using cv2 and pytesseract libraries and it will plot a pie chart from the detail of the consumption and a barc chart from the History Consumption using plotly library. It will also infer the consumptions from previous month in the history applying computer vision techniques.


## Installation

### Buil Docker Image

You can use `Docker` to install all the needed packages and libraries easily.

```bash
$ docker build -t wattercosumpdashapp --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) -f ./Dockerfile .
```

### Run Docker Container


```bash
$ docker run --rm --net host -it \
    -v "$(pwd):/home/app/src" \
    --workdir /home/app/src \
    wattercosumpdashapp \
    bash
```

### Preparing data
In order for this project to run you need:

- Image of a City of Sugar Land TX 77487-5029 water consumption invoice
- Csv file with bounding boxed of all the region of interset from the invoicec images. It will have following structure:
```
editable,xref,yref,layer,opacity,line,fillcolor,fillrule,type,x0,y0,x1,y1

TRUE,x,y,above,1,"{'color': 'red', 'width': 1, 'dash': 'solid'}","rgba(0,0,0,0)",evenodd,rect,1289.236155,375.7984847,1657.318523,439.5050484
```
- setting.py file specifying the path of the images folder and csv file. Edit it as needed


## Running the project
In order to run the project simply run the Image_Create_Template.py file
```bash
python Image_Create_Template.py 
```
You will see the message:
```bash
Dash is running on http://127.0.0.1:8050/
```
Go to __http://127.0.0.1:8050/__ in your favourite browser and select the image you want to process

![Choose a file](/screenshots//1choosegile.png)

Load the image with the annotated bounding boxes by clicking the **Load image** button

![Load image](/screenshots/2loadimage.png)

CLick the **Process** button. A pie chart with the detaile invoice consumption will be displayed

![Process image](/screenshots/3.processimage.png)

It will also be shown a bar chart with the infered consumption from precious month in History Consumption

![Consumption History](/screenshots/4.historyconsumption.png)

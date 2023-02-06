import plotly.express as px
import json
from PIL import Image
import plotly.graph_objects as go
import pandas as pd
import pytesseract
import cv2
from pytesseract import Output as Output1
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import os
from dash_extensions.enrich import DashProxy, html, dcc, Input, Output, State, ServersideOutput, ServersideOutputTransform
import numpy as np

allowed_extensions = ['.png', '.jpg', '.jpeg']
files_list = [file for file in os.listdir('./resources/invoices') if os.path.splitext(file)[1].lower() in allowed_extensions ]

config = {
    "modeBarButtonsToAdd": [
        #"drawline",
        #"drawopenpath",
        #"drawclosedpath",
        #"drawcircle",
        "drawrect",
        "eraseshape",
    ]
}

fig = go.Figure()

fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                  yaxis = dict(showgrid=False, zeroline=False, tickfont = dict(color = 'rgba(0,0,0,0)')),
                  xaxis = dict(showgrid=False, zeroline=False, tickfont = dict(color = 'rgba(0,0,0,0)')))
figure = go.Figure()
figure.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    yaxis = dict(showgrid=False, zeroline=False, tickfont = dict(color = 'rgba(0,0,0,0)')),
                    xaxis = dict(showgrid=False, zeroline=False, tickfont = dict(color = 'rgba(0,0,0,0)')))

# Build App
# app = dash.Dash(__name__)
app = DashProxy(__name__, transforms=[ServersideOutputTransform()])
app.layout = html.Div(
    [
        dcc.Store(id='invoice-image'),
        html.Button('Load image', id='load-btn', n_clicks=0),
        dcc.Dropdown(files_list, files_list[0], id='files-list'),
        html.H4("Draw a shape, then modify it"),
        dcc.Graph(id="fig-image", figure=fig, config=config, style={'width': '150vh', 'height': '150vh',"border":"1px black solid"}),
        html.Button('Process', id='process-btn', n_clicks=0),
        dcc.Loading(id = "loading-icon",
                    type = 'graph',
                    children=[html.Div(dcc.Graph(id='graph', figure=figure))])
    ]
)

@app.callback(
    Output('fig-image', 'figure'),
    ServersideOutput('invoice-image', 'data'),
    Input('load-btn','n_clicks'),
    State('files-list', 'value'),
    prevent_initial_call=True,
)
def load_image(n_clicks, filename):
    print(filename)
    filename = './resources/invoices/' + filename
    print(n_clicks)
    # fileName="./ADMIN1.jpg"
    img = cv2.imread(filename)

    # On Windows
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Users\JIMMY\Desktop\Programming\Python_Libraries\Tesseract-OCR\tesseract'

    columns = ['type','left','top', 'width', 'height', 'scaleX', 'strokeWidth']

    d = pytesseract.image_to_data(img, output_type=Output1.DICT)
    dfCoord=pd.DataFrame.from_dict(d)
    dfCoord = dfCoord[(dfCoord['text'] == "77487-5029")]
    dfCoord=dfCoord.iloc[0]
    xCoor, yCoor = dfCoord['left'], dfCoord['top']

    fig = Image.open(filename)
    fig = px.imshow(fig)
    # shapes=pd.read_csv("C:\\Users\\JIMMY\\Desktop\\Programming\\RMS\\Sheets\\shapeSugarLand1.csv")
    shapes=pd.read_csv("./shapeSugarLand1.csv")
    row_1=shapes.iloc[0]
    xCoor, yCoor = xCoor-row_1['x0'], yCoor-row_1['y0']
    for index, row in shapes.iterrows():
        fig.add_shape(
            type='rect', xref='x', yref='y',
            x0=row['x0']+xCoor, x1=row['x1']+xCoor, y0=row['y0']+yCoor, y1=row['y1']+yCoor, line=dict(color="red", width=1)
        )
    return fig, json.dumps(img.tolist())





@app.callback(
    Output("graph", "figure"), 
    Input('process-btn', 'n_clicks'),
    State('invoice-image', 'data'),
    State('fig-image', 'figure'),
    prevent_initial_call=True,
)
def process_image(n_clicks, img, fig):
    print(n_clicks)
    img = np.array(json.loads(img)).astype(np.uint8)
    # print(img)
    def get_pie_slice(text):
        # Possible end characters
        end_label ='0123456789$'
        for i, c in enumerate(text):
            if c in end_label:
                return text[:i-1]
    def own(shape):
        global text_list
        ReadingSection = img[int(shape.y0):int(shape.y1), int(shape.x0):int(shape.x1)]
        text = pytesseract.image_to_string(ReadingSection, config='--psm 6').replace("\n\f", "").split("\n")
        print(text)
        text_list.extend(text)

    global text_list
    text_list = []
    fig = go.Figure(fig)
    fig.for_each_shape(own)
    result = json.dumps(text_list, indent=2)
    print(text_list)
    labels_list = [get_pie_slice(line) for line in text_list[-5:]]
    values_list = [line[line.find('$')+1:] for line in text_list[-5:]]
    names_list =  [line[line.find('$'):] for line in text_list[-5:]]
    pie_dict = {'Description':labels_list, 'values':values_list, 'names':names_list}
    figure = px.pie(pie_dict, values='values', names='Description', hole=.3, hover_data=['names'])
    figure.update_layout(
        margin=dict(b=0, l=0, r=0),
        font={'size': 15},
        title={'text': '<b>Water Consumption from ' + text_list[10].split()[4] + ' to ' + text_list[10].split()[5] + '</b>',
              'font': {'size': 35},
              'x':0.45},
    )
    figure.update_traces(textposition='inside', textinfo='percent+label')

    return figure

if __name__ == "__main__":
    app.run_server(debug=True)



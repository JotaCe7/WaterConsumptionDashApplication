import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from utils.utils import get_pie_slice, get_invoice_images, get_shapes, get_history_consumption
from utils.pytesseract_utils import  set_tesseract_cmd, image_to_string
from utils.cv2_utils import decode_image
import json

IS_DEBUGGING = False

# Set tesseract_cmd 
set_tesseract_cmd()

# Get file names from invoice folder
files_list = get_invoice_images()

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

# Create a dummy Figure
figure = go.Figure()
figure.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    yaxis = dict(showgrid=False, zeroline=False, tickfont = dict(color = 'rgba(0,0,0,0)')),
                    xaxis = dict(showgrid=False, zeroline=False, tickfont = dict(color = 'rgba(0,0,0,0)')))

# Build App
app = Dash(__name__)
app.layout = html.Div(
    [
        html.H1('Water Consumption Dashboard', style={'textAlign': 'center'}),
        html.Div(
            children=[
                html.H3("Select an invoice image and press the Load button, then press the Process button"),
                dcc.Dropdown(files_list, files_list[0], id='files-list'),
                html.Button('Load image', id='load-btn', n_clicks=0)
            ]
        ),
        dcc.Loading(id = "loading-image",
                    type = 'cube',
                    children = [html.Div(dcc.Graph(id="fig-image", figure=figure, config=config,
                                                   style={'width': '150vh', 'height': '150vh',
                                                          "border":"1px black solid"}))]),
        html.Button('Process', id='process-btn', n_clicks=0),
        dcc.Loading(id = "loading-icon",
                    type = 'graph',
                    children=[html.Div(dcc.Graph(id='piechart', figure=figure))]),
        dcc.Loading(id = "loading-icon2",
                    type = 'graph',
                    children=[html.Div(dcc.Graph(id='barchart', figure=figure))]),
  
        html.Pre(id="annotations-pre"),
    ]
)

@app.callback(
    Output('fig-image', 'figure'),
    Input('load-btn','n_clicks'),
    State('files-list', 'value'),
    prevent_initial_call=True,
)
def load_image(_, filename):
  
    shapes, img = get_shapes(filename)

    fig = px.imshow(img)

    for _, row in shapes.iterrows():
        fig.add_shape(
            **row
        )
    return fig

@app.callback(
    Output('piechart', 'figure'), 
    Output('barchart', 'figure'),
    Output('annotations-pre', 'children'),
    Input('process-btn', 'n_clicks'),
    State('fig-image', 'figure'),
    prevent_initial_call=True,
)
def process_image(_, fig):
    """
    This funtion gets called when Process button is clicked
    Get shapes from Figure on dcc.Graph with id="fig-image"
    and plots pie chart and bar chart
    """

    # Get image as np.ndarray from Figure in dcc.Graph with id="fig-image"
    img = decode_image(fig['data'][0]['source'])

    text_list = []
    def append_text_from_shape(shape):
        """
        Get the text from section of img defined by a Figure shape and appends it
        to a outter scopeed declared list
        Parameters
        ----------
        shape: plotly.graph_objects.layout.Shape 
            shape where boundinbox is obtained
        Returns
        -------
        Nothing        
        """
        if shape['line']['color'] == 'red':
            ReadingSection = img[int(shape.y0):int(shape.y1), int(shape.x0):int(shape.x1)]
            text = image_to_string(ReadingSection)
            text_list.extend(text)

    # Append texts in shapes to 'text_list'
    fig = go.Figure(fig)    
    fig.for_each_shape(append_text_from_shape)

    # Get months from Consumption Hystory shape.
    # Assumes that there is only one row in shapes csv with blue fillcolor
    for shape in fig.select_shapes({'fillcolor':'rgba(0,0,1,0)'}):
        ReadingSection = img[int(shape.y0):int(shape.y1), int(shape.x0):int(shape.x1)]
    text = image_to_string(ReadingSection)
    max_consumption = int(text[0])
    months = text[-1].split()
    
    # Get consumptions from Consumption Hystory shape.
    # Assumes that there is only one row in shapes csv with green fillcolor
    for shape in fig.select_shapes({'fillcolor':'rgba(0,1,0,0)'}):
        ReadingSection = img[int(shape.y0):int(shape.y1), int(shape.x0):int(shape.x1)]
    consumptions = get_history_consumption(ReadingSection, max_consumption)
    
    # Create bar chart
    history_data =  {'Month': months, 'Consumption': consumptions}
    barchart = px.bar(history_data, x='Month', y='Consumption',
            color='Consumption', height=800)
    barchart.update_layout(
      font={'size':15},
      title = {'text': '<b>History Consumption from ' + months[0]+'-'+str(int(text_list[10].split()[5][-4:])-1) + ' to ' + months[-1]+'-'+text_list[10].split()[5][-4:] + '</b>',
                                                                                                                                      # this might faile in January  ^
              'font': {'size': 35},
              'x':0.45},
    )

    # Create pie chart
    labels_list = [get_pie_slice(line) for line in text_list[-5:]]
    values_list = [line[line.find('$')+1:] for line in text_list[-5:]]
    names_list =  [line[line.find('$'):] for line in text_list[-5:]]
    pie_dict = {'Description':labels_list, 'values':values_list, 'names':names_list}
    piechart = px.pie(pie_dict, values='values', names='Description', hole=.3, hover_data=['names'])
    piechart.update_layout(
        margin=dict(b=0, l=0, r=0),
        font={'size': 15},
        title={'text': '<b>Water Consumption from ' + text_list[10].split()[4] + ' to ' + text_list[10].split()[5] + '</b>',
              'font': {'size': 35},
              'x':0.45},
    )
    piechart.update_traces(textposition='inside', textinfo='percent+label')

    text_list_debug = ""
    if IS_DEBUGGING:
        text_list_debug = json.dumps(text_list, indent=2)

    return piechart, barchart, text_list_debug

if __name__ == "__main__":
    app.run_server(debug=True)



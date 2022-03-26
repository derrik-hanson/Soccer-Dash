

from dash import Dash, dash_table

import pandas as pd
import numpy as np

from statsbombpy import sb
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

import sbutilities as sbut
import soccerplotly as socly

# ------------------
# -- Data 
# ------------------

all_comps = sb.competitions()

comps_360 = all_comps[all_comps['match_available_360'].apply(lambda x: isinstance(x, str))]

df = comps_360
#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

# ------------------
# -- Dash App 
# ------------------

app = Dash(__name__)

app.layout = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])

if __name__ == '__main__':
    app.run_server(debug=True)
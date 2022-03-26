

from dash import Dash, dash_table, html, dcc

import pandas as pd
import numpy as np

from statsbombpy import sb
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

import sbutilities as sbut
import soccerplotly as socly


# ------------------
# -- Utility Functions 
# ------------------

def get_player_events(df_act, active_player, event_type):
    df_act = df_act[event_type]
    df_player_events = df_act[df_act['player']==active_player]
    return df_player_events

def get_team_events(df_act, active_team, event_type):
	df_act = df_act[event_type]
	df_team_events = df_act[df_act['possession_team']==active_team]
	return df_team_events


# ------------------
# -- Data 
# ------------------

all_comps = sb.competitions()
comps_360 = all_comps[all_comps['match_available_360'].apply(lambda x: isinstance(x, str))]
df = comps_360

euro_final_mid = 3795506
euro_final_frames = sbut.get_local_360_file(euro_final_mid)
euro_final_events = sb.events(match_id=3795506, split=True, flatten_attrs=True)

euro_combo_df = sbut.join_events_split_to_frames(euro_final_frames, euro_final_events)
test_row = euro_combo_df['shots'].iloc[4]
fig_frame = socly.plot_frame(test_row)

# player event graphs
selected_player = 'Ciro Immobile'
selected_events = 'shots'
df_pl_shot = get_player_events(euro_combo_df, selected_player, selected_events)
fig_player_shots = socly.plot_shots_xg(df_pl_shot, title=f"Shots - {selected_player}")


# Team Shots 
selected_team_1 = 'Italy'
selected_team_ev_typ = 'shots'
df_tm_shot = get_team_events(euro_combo_df, selected_team_1, selected_team_ev_typ)
fig_team_shots = socly.plot_shots_xg(df_tm_shot, title=f"Shots - {selected_team_1}")



# ------------------
# -- Dash App 
# ------------------

app = Dash(__name__)

app.layout = html.Div(children=[

	html.Div(children='''
        A Single Frame from the Euro Fianl 2020
    '''),

    dcc.Graph(
        id='fz-graph',
        figure=fig_frame
    ),

    dcc.Graph(
        id='player-shot-graph',
        figure=fig_player_shots
    ),

    dcc.Graph(
        id='team-shot-graph',
        figure=fig_team_shots
    )

	#dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])

])


if __name__ == '__main__':
    app.run_server(debug=True)
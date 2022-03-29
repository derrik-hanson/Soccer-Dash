

from dash import Dash, dash_table, html, dcc, Input, Output

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


# team utility functions
def get_team_events(df_act, active_team, event_type):
    df_act = df_act[event_type]
    df_team_events = df_act[df_act['possession_team']==active_team]
    return df_team_events

# player utility functions
def get_player_events(df_act, active_player, event_type):
    df_act = df_act[event_type]
    df_player_events = df_act[df_act['player']==active_player]
    return df_player_events

def plot_player_shots(df_e, selected_player):
    df_pl_ev = get_player_events(df_e, selected_player, 'shots')
    fig_player_ev = socly.plot_shots_xg(df_pl_ev, title=f"Shots - {selected_player}")
    return fig_player_ev


def plot_player_passes(df_e, selected_player):
    df_pl_ev = get_player_events(df_e, selected_player, 'passes')
    fig_pass_arrows = socly.plot_passes(df_pl_ev)

    return fig_pass_arrows


def plot_player_heat(df, selected_player, selected_events=None, title=None):
    df_heats = df[df['player']==selected_player]

    if selected_events is not None:
        # selected_events must be a list
        df_heats = df_heats[df_heats['type'].isin(selected_events)]

    fig_heat = socly.plot_event_heat_rect(df_heats, title=title)
    return fig_heat

# Player selection utility functions


# ------------------
# -- Data 
# ------------------


all_comps = sb.competitions()
comps_360 = all_comps[all_comps['match_available_360'].apply(lambda x: isinstance(x, str))]
df = comps_360

# initital data fetch 
euro_final_mid = 3795506
euro_final_frames = sbut.get_local_360_file(euro_final_mid)
euro_final_events = sb.events(match_id=3795506, split=True, flatten_attrs=True)
df_all_evs = sb.events(match_id=3795506, split=False, flatten_attrs=True)

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
# -- UI Preprocessing
# ------------------
italy_all_players = sbut.get_all_team_players_match(euro_final_events,'Italy')
italy_player_opts = [{'label': p, 'value': p} for p in italy_all_players['player_name'].unique().tolist()]
df_t = italy_all_players

eng_all_players = sbut.get_all_team_players_match(euro_final_events,'England')
eng_player_opts = eng_all_players['player_name'].unique().tolist()

# ------------------
# -- Dash App 
# ------------------

app = Dash(__name__)

app.layout = html.Div(children=[

    html.H1(children='A Single Frame from the Euro Final 2020'),

    dcc.Graph(
        id='fz-graph',
        figure=fig_frame
    ),

    # -------------------------------
    html.H1(children='Team Analysis'),
    dcc.Graph(
        id='team-shot-graph',
        figure=fig_team_shots
    ),

    # -------------------------------
    html.H1(children='Player Analysis'),

    dash_table.DataTable(
        id='player-table',
        columns=[{"name": i, "id": i} 
                 for i in df_t.columns],
        data=df_t.to_dict('records'),
        style_cell=dict(textAlign='left')
    ),

    html.P(id='table-out'),

    # dcc.Dropdown(
    #     options = italy_player_opts,
    #     value = 'Marco Verratti', 
    #     placeholder = 'select a player',
    #     id='player-dropdown'
    # ),

    html.Div(id='player_name_output'),

    dcc.Graph(
        id='player-shot-plot',
        figure=fig_player_shots
    ),

    dcc.Graph(
        id='player-pass-plot'
    ),

    dcc.Graph(
        id='player-heat-plot'
    )

])

# ------------------
# Callbacks 
# ------------------

@app.callback(
    Output(component_id='player_name_output', component_property='children'),
    Output(component_id='player-shot-plot', component_property='figure'),
    Output('player-heat-plot', 'figure'),
    Output('player-pass-plot', 'figure'),
    # Input(component_id='player-dropdown', component_property='value')
    Input('player-table', 'active_cell')
)
def update_output_div(active_cell):
    if active_cell:
        selected_player = df_t.iloc[active_cell['row']][active_cell['column']]
    else:
        selected_player = 'Lorenzo Insigne'

    name_string = f'Selected Player: {selected_player}'
    
    print(selected_player)
    # source data
    df_e = euro_combo_df

    # shot plot
    shot_plot = plot_player_shots(df_e, selected_player)

    pass_plot = plot_player_passes(df_e, selected_player)

    heat_plot = plot_player_heat(df_all_evs, selected_player, title='All Player Events')

    return name_string, shot_plot, pass_plot, heat_plot



# ------------------
# Run App
# ------------------

if __name__ == '__main__':
    app.run_server(debug=True)






import dash
import dash_bootstrap_components as dbc
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

def make_pass_table_basic(df_e, selected_player):
    df_pl_ev = get_player_events(df_e, selected_player, 'passes')
    pass_table_basic =  sbut.get_pass_stats_basics(df_pl_ev)
    return pass_table_basic

def make_pass_length_bars(df_e, selected_player):
    df_pl_ev = get_player_events(df_e, selected_player, 'passes')
    fig_pass_lengths = socly.pass_length_bar_plot(df_pl_ev)
    return fig_pass_lengths

def make_player_dribble_plot(df_e, selected_player):
    df_pl_ev = get_player_events(df_e, selected_player, 'dribbles')
    fig_dribble_locs = socly.plot_event_scatter_generic(df_pl_ev, title='Dribble Locations')
    return fig_dribble_locs

def make_dribble_table_basic(df_e, selected_player):
    df_pl_ev = get_player_events(df_e, selected_player, 'dribbles')
    dribble_table_basic = sbut.make_dribble_stats_table(df_pl_ev)
    return dribble_table_basic

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
df_t = df_t.rename({'player_name': 'Player', 'position_name': 'Position'}, axis=1)

eng_all_players = sbut.get_all_team_players_match(euro_final_events,'England')
eng_player_opts = eng_all_players['player_name'].unique().tolist()

pass_table_basic = make_pass_table_basic(euro_combo_df, selected_player)

dribble_table_basic = make_dribble_table_basic(euro_combo_df, selected_player)
# ------------------
# -- Dash App 
# ------------------

app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])

navbar = dbc.NavbarSimple(
            children=[
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Player Study", href="/player-page", active="exact"),
                dbc.NavLink("Team Study", href='/team-page', active="exact"),
                dbc.NavLink("Frame ", href='/frame-page', active="exact"),
            ],
            brand="Socly Insight Engine",
            color="primary",
            dark=True,
        )

content = dbc.Container(id="page-content", className="pt-4")

app.layout = html.Div([dcc.Location(id="url"), navbar, content])

# -------------------------------
# Team and Frame placeholder
layout_frame_page = html.Div(children=[
    html.H1(children='A Single Frame from the Euro Final 2020'),

    dbc.Row([
            dbc.Col(html.Div(dcc.Graph(id='fz-graph',figure=fig_frame)), width=6),
            dbc.Col(html.Div(dcc.Graph(id='fz-graph',figure=fig_frame)), width=6)
        ]),

    dcc.Graph(
        id='fz-graph',
        figure=fig_frame
    ),
])
# -------------------------------
# Team and Frame placeholder
layout_team_page = html.Div(children=[
    html.H1(children='Team Analysis'),

    dcc.Graph(
        id='team-shot-graph',
        figure=fig_team_shots
    ),
])

# -------------------------------
# player analysis page
# -------------------------------

# Player UI Elements 
player_events_defense = ['Pressure', 'Duel', 'Ball Recovery', 'Block', 'Interception', 'Clearance']
player_events_ball = ['Shot','Pass', 'Ball Receipt*', 'Carry', 'Dribble']
player_events_other = ['Dispossessed', 'Miscontrol', 'Dribbled Past', 'Foul Won','Goal Keeper']

heat_checklist = html.Div(
    [
        html.H3("Select Events"),
        dbc.Label("Offense"),
        dbc.Checklist(
            id="heat-select-ball",
            options=[{"label": i, "value": i} for i in player_events_ball],
            value=[],
            inline=False,
        ),
        dbc.Label("Defense"),
        dbc.Checklist(
            id="heat-select-defense",
            options=[{"label": i, "value": i} for i in player_events_defense],
            value=[player_events_defense[0]],
            inline=False,
        ),
        dbc.Label("Other"),
        dbc.Checklist(
            id="heat-select-other",
            options=[{"label": i, "value": i} for i in player_events_other],
            value=[],
            inline=False,
        ),
    ],
    className="mb-4",
)

heat_controls = dbc.Card([heat_checklist], body=True,)

# ------------------------
# Player Layout
layout_player_page = html.Div(children=[
    html.H1(children='Player Analysis'),

    dbc.Card(html.Div([
        dash_table.DataTable(
        id='player-table',
        columns=[{"name": i, "id": i} 
                 for i in df_t.columns],
        data=df_t.to_dict('records'),
        style_cell={'textAlign':'left',
            'minWidth': '100px', 'width': '150px', 'maxWidth': '150px',
            'fontSize' : 16, 
            'font-family': 'sans-serif',
            'border': '1px solid darkgrey'
            },
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white'
        },
        style_data={
            'backgroundColor': 'rgb(50, 50, 50)', 
            'color': 'white'
        },
        style_as_list_view=True,
    )], 
    className="mb-4"
    ),
    body=True
    ),

    html.P(id='table-out'),

    # dcc.Dropdown(
    #     options = italy_player_opts,
    #     value = 'Marco Verratti', 
    #     placeholder = 'select a player',
    #     id='player-dropdown'
    # ),

    html.Div(id='player_name_output'),

    # --------------------------------
    # Player Passing
    html.Hr(),
    html.H1(children="Shooting Tendencies"),

    dcc.Graph(
        id='player-shot-plot',
        figure=fig_player_shots
    ),

    # --------------------------------
    # Player Passing
    html.Hr(),
    html.H1(children="Passing Tendencies"),

    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(id='player-pass-plot')), width=6),
        dbc.Col(dbc.Card(html.Div([
            html.H3(children='Pass Stats'),
            dash_table.DataTable(
                id='pass-basics',
                columns = [{"name": i, "id": i} 
                         for i in pass_table_basic.columns],
                data=pass_table_basic.to_dict('records'),
                style_cell={'textAlign':'left',
                    'minWidth': '30px', 'width': '100px', 'maxWidth': '150px',
                    'fontSize' : 14, 
                    'font-family': 'sans-serif',
                    'border': '1px solid darkgrey'
                    },
                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)',
                    'color': 'white'
                },
                style_data={
                    'backgroundColor': 'rgb(50, 50, 50)', 
                    'color': 'white'
                },
                style_as_list_view=True,
            )],
            style={'color':'white','padding-top': 15, },
            #className='mb-4'
            ),        
            body=True
            ),
            width = {'size':5, 'offset':1}),

    ]),

    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(id='pass-length-plot')), width=6)
    ]),

    # --------------------------------
    # Player Dribbles
    html.Hr(),
    html.H1(children="Dribbles"),

    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(id='player-dribble-plot')), width=6),
        dbc.Col(dbc.Card(html.Div([
            html.H3(children='Dribble Stats'),
            dash_table.DataTable(
                id='dribble-basics',
                columns = [{"name": i, "id": i} 
                         for i in dribble_table_basic.columns],
                data=dribble_table_basic.to_dict('records'),
                style_cell={'textAlign':'center',
                    'minWidth': '100px', 'width': '150px', 'maxWidth': '150px',
                    'fontSize' : 14, 
                    'font-family': 'sans-serif',
                    'border': '1px solid darkgrey'
                    },
                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)',
                    'color': 'white'
                },
                style_data={
                    'backgroundColor': 'rgb(50, 50, 50)', 
                    'color': 'white'
                },
                style_as_list_view=True,
            )],
            style={'color':'white','padding-top': 15, },
            #className='mb-4'
            ),        
            body=True
            ),
            width = {'size':5, 'offset':1}),
    ]),    
    

    # --------------------------------
    # Player Events
    html.Hr(),
    html.H1(children="Activity Heatmap"),
    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(id='player-heat-plot')), width = 8),
        dbc.Col(html.Div(heat_controls),width=4),

    ])
])

# ------------------
# Callbacks 
# ------------------

# Page Control Callouts 
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.P("This is the content of the home page!")
    elif pathname == "/player-page":
        return layout_player_page
    elif pathname == "/team-page":
        return layout_team_page
    elif pathname == "/frame-page":
        return layout_frame_page
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


# Player Callbacks
@app.callback(
    Output(component_id='player_name_output', component_property='children'),
    Output(component_id='player-shot-plot', component_property='figure'),
    Output('player-heat-plot', 'figure'),
    Output('player-pass-plot', 'figure'),
    Output('pass-basics', 'data'),
    Output('pass-length-plot', 'figure'),
    Output('dribble-basics', 'data'),
    Output('player-dribble-plot', 'figure'),
    # ------
    Input('player-table', 'active_cell'),
    Input('heat-select-ball', 'value'),
    Input('heat-select-defense', 'value'),
    Input('heat-select-other', 'value')
)
def update_output_div(active_cell, ball_evs, def_evs, other_evs):
    if active_cell:
        selected_player = df_t.iloc[active_cell['row']][active_cell['column']]
    else:
        selected_player = 'Lorenzo Insigne'

    name_string = f'Selected Player: {selected_player}'
    
    print(selected_player)
    # source data
    df_e = euro_combo_df

    # player shots
    shot_plot = plot_player_shots(df_e, selected_player)

    # player passes
    pass_plot = plot_player_passes(df_e, selected_player)
    pass_basics_data = make_pass_table_basic(df_e, selected_player).to_dict('records')
    pass_length_plot = make_pass_length_bars(df_e, selected_player)

    # player dribbles
    dribble_plot = make_player_dribble_plot(df_e, selected_player)
    dribble_basics_data = make_dribble_table_basic(df_e, selected_player).to_dict('records')

    # player event heatmap
    #heat_plot = plot_player_heat(df_all_evs, selected_player, title='All Player Events')
    selected_events = ball_evs + def_evs + other_evs
    df_sel_evs = df_all_evs[df_all_evs['type'].isin(selected_events)]
    heat_plot = plot_player_heat(df_sel_evs, selected_player, title='Selected Player Events')
    return name_string, shot_plot, heat_plot, pass_plot, pass_basics_data, pass_length_plot, dribble_basics_data, dribble_plot

# @app.callback(
#         Output('player-heat-plot', 'figure'),
#         # ------
#         Input('heat-select-ball', 'value'),
#         Input('heat-select-defense', 'value'),
#         Input('heat-select-other', 'value')
# )
# def update_player_heatmap(ball_evs, def_evs, other_evs):
#     selected_events = ball_evs + def_evs + other_evs
#     df_sel_evs = df_all_evs[df_all_evs['type'].isin(selected_events)]
#     heat_plot = plot_player_heat(df_sel_evs, selected_player, title='Selected Player Events')
#     return heat_plot_update

# ------------------
# Run App
# ------------------

if __name__ == '__main__':
    app.run_server(debug=True)






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


# ---------------------
# -- Utility Functions 
# ---------------------


# team utility functions
def get_team_events(df_act, active_team, event_type):
    df_act = df_act[event_type]
    df_team_events = df_act[df_act['possession_team']==active_team]
    return df_team_events

#-------------------------
# player utility functions
def get_player_events(df_act, active_player, event_type):
    df_act = df_act[event_type]
    df_player_events = df_act[df_act['player']==active_player]
    return df_player_events

def plot_player_shots(df_e, selected_player):
    df_pl_ev = get_player_events(df_e, selected_player, 'shots')
    fig_player_ev = socly.plot_shots_xg(df_pl_ev, title=f"Shots - {selected_player}")
    return fig_player_ev

def make_shot_stats_table(df_e, selected_player):
    df_pl_ev = get_player_events(df_e, selected_player, 'shots')
    shot_stat_summary = sbut.get_shot_stats(df_pl_ev)
    shot_stat_summary.columns = [s.replace('_',' ') for s in shot_stat_summary.columns]
    return shot_stat_summary

def make_shot_details_table(df_e, selected_player):
    df_pl_ev = get_player_events(df_e, selected_player, 'shots')
    shot_details = sbut.get_shot_details_table(df_pl_ev)
    shot_details.columns = [s.replace('_',' ') for s in shot_details.columns]
    return shot_details

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

def make_player_match_summary(df, selected_player):
    df_msum = sbut.get_player_match_summary(df, selected_player)
    df_msum = df_msum[['goals', 'total_xg','shots','assists', 'pass_completion_percent', 'carrys', 'dribbles_complete','playing_time']]
    df_msum.columns = [s.replace('_', ' ') for s in df_msum.columns]
    return df_msum

# Player selection utility functions


# ------------------
# -- Data 
# ------------------

#--------------------
# data selection 
comp_opts = sbut.get_comp_opts()


#-----------------
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
                dbc.NavLink("Player Match Report", href="/player-page", active="exact"),
                dbc.NavLink("Team Analysis", href='/team-page', active="exact"),
                dbc.NavLink("Frame ", href='/frame-page', active="exact"),
                dbc.NavLink("Barca Managers", href='/barca-manager-page', active="exact"),
            ],
            brand="Socly Insight Engine",
            color="primary",
            dark=True,
        )

content = dbc.Container(id="page-content", className="pt-4")

app.layout = html.Div([dcc.Location(id="url"), 
                      navbar,
                      content,
                      # data storage 
                       dcc.Store(id='selected-comp-id'),
                       dcc.Store(id='selected-season-id'),
                       dcc.Store(id='selected-match-id'),
                       dcc.Store(id='selected-player-id'),
                       dcc.Store(id='selected-team-name'),
                       ])

# -------------------------------
# Barca Managers Page
mgr_path = '/Users/Spade5/DSA/Projects/Soccer-Dash/df_barca_manager_tenures.pkl'
manager_opts = pd.read_pickle(mgr_path)


barca_manager_page_layout = html.Div(children=[
    html.H1(children='Barcelona Manager Analysis'),
    html.H2(children='Shot Assists'),
    html.Hr(),

    html.H3(children='Minimum xG Shot Value'),
    dcc.Dropdown(
       id='xg-min-select',
       options=[{'label': round(i,2), 'value': round(i,2)} for i in np.arange(0.05,1.0, 0.05)],
       value='0.10'
    ),
    
    html.H3(children='Managers to Compare'),
    dbc.Row([
        dbc.Col(html.Div(dcc.Dropdown(
           id='barca-manager-select1',
           options=[{'label': i, 'value': i} for i in manager_opts['manager_name'].to_list()],
           value='Pep Guardiola'
        ))),
        dbc.Col(html.Div(dcc.Dropdown(
           id='barca-manager-select2',
           options=[{'label': i, 'value': i} for i in manager_opts['manager_name'].to_list()],
           value='Pep Guardiola'
        ))),
    ]),



    html.Hr(),
    html.H2(children='Clusters Summary'),
    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(id='centers-fig1',figure=fig_frame)), width=6),
        dbc.Col(html.Div(dcc.Graph(id='centers-fig2',figure=fig_frame)), width=6),
    ]),

    html.Hr(),
    html.H2(children='Clusters in Detail'),
    dbc.Row([
        dbc.Col(html.Div(id='clusters-fig1'), width=6),
        dbc.Col(html.Div(id='clusters-fig2'), width=6),
    ]),
])


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

    html.Hr(),
    html.H1(children="Regaining Possession"),

    html.Hr(),
    html.H1(children="Goal Plot / All Shots Plot - w/ xG slider"),

    html.Hr(),
    html.H1(children="Assist Heatmap"),
    html.H1(children="Pass to shot Heatmap - w/ xG slider"),

    html.Hr(),
    html.H1(children="Passing Matrx / Passing Network Plot"),

    html.Hr(),
    html.H1(children="Possession Regained Heatmap"),

    html.Hr(),
    html.H1(children="Possession Termination Radar Plot"),
])

# -------------------------------
# player analysis page
# -------------------------------

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

# Player Selection Elements
select_table_comp = dbc.Row([
        dbc.Col(
            dbc.Card(html.Div([
                dash_table.DataTable(
                id='select-comp',
                columns=[{"name": i, "id": i} 
                         for i in comp_opts.columns],
                data=comp_opts.to_dict('records'),
                style_cell={'textAlign':'left',
                    'minWidth': '100px', 'width': '150px', 'maxWidth': '220px',
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
        width=7),
    ])

select_table_season = dbc.Row([
        dbc.Col(
            dbc.Card(html.Div([
                dash_table.DataTable(
                id='select-season',
                style_cell={'textAlign':'left',
                    'minWidth': '100px', 'width': '150px', 'maxWidth': '220px',
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
        width=7),
    ])

select_table_match = dbc.Row([
        dbc.Col(
            dbc.Card(html.Div([
                dash_table.DataTable(
                id='select-match',
                style_cell={'textAlign':'left',
                    'minWidth': '100px', 'width': '150px', 'maxWidth': '220px',
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
        width=7),
    ])

select_table_player = dbc.Row([
        dbc.Col(
            dbc.Card(html.Div([
                dash_table.DataTable(
                id='select-player',
                style_cell={'textAlign':'left',
                    'minWidth': '100px', 'width': '150px', 'maxWidth': '270px',
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
        width=12),
    ])

player_select_layout = html.Div(children=[
            html.H1(children='Player Analysis'),
            html.Hr(),

            html.H3(children='Select competition'),
            select_table_comp,

            html.H3(children='Select Season'),
            select_table_season,

            html.H3(children='Select Match'), 
            select_table_match,

            html.H3(children='Select Player'),
            select_table_player,

            #html.H3(children='Select Team'),
        ])

player_analysis_layout = html.Div(children=[
    dbc.Row([
        dbc.Col(html.Div([
            html.H3(children='selected player:'),
            html.H1(id='player_name_output'),
            ]),
            width=7),
        ]),

    html.Hr(),
    html.Hr(),

    html.H2(children="Player Match Summary "),
    dbc.Row([
        dbc.Col(dbc.Card(html.Div([
            html.H3(children='Stats'),
            dash_table.DataTable(
                id='player-match-sumr-table',

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
            width = {'size':11, 'offset':0}),

    ]),


    # --------------------------------
    # Player Passing
    html.Hr(),
    html.H1(children="Shooting Tendencies"),

    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(id='player-shot-plot',figure=fig_player_shots)),
            width=6),
        dbc.Col(html.Div([
            dbc.Card(html.Div([
            html.H3(children='Shot Stats'),
            dash_table.DataTable(
                id='shot-stats-table',
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
            
            dbc.Card(html.Div([
            html.H3(children='Shot Details'),
            dash_table.DataTable(
                id='shot-dets-table',
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
            style={'color':'white','padding-top': 15,},
            #className='mb-4'
            ),        
            body=True,
            style={'margin-top': 25},
            ), 
            ]),
            width = {'size':5, 'offset':1}),
        
    ]),

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

    # --------------
    # Player Events
    html.Hr(),
    html.H1(children="Activity Heatmap"),
    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(id='player-heat-plot')), width = 8),
        dbc.Col(html.Div(heat_controls),width=4),

    ])
])

# ------------------------
# Player Page Layout
player_tabs = html.Div([
                dcc.Tabs(id="player-tab", value='tab-player-select', children=[
                    dcc.Tab(label='Select', value='tab-player-select',
                            children=[player_select_layout]),
                    dcc.Tab(label='Player Match Report', value='tab-player-analysis',
                            children=[player_analysis_layout]),
                ], colors={
                    "border": "white",
                    "primary": "white",
                    "background": "black"
                }),
                html.Div(id='tabs-content-props')
            ])

layout_player_page = html.Div(children=[
    player_tabs,
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
    elif pathname == "/barca-manager-page":
        return barca_manager_page_layout
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

# --------------------
# Player Callbacks

# User Selections
@app.callback(
    Output('selected-comp-id', 'value'),
    Output('select-season','data'),
    Output('select-season','columns'),
    # ---
    Input('select-comp','active_cell')
    )
def handle_comp_selection(selected_comp_cell):
    if selected_comp_cell:
        comp_row = comp_opts.iloc[selected_comp_cell['row']][selected_comp_cell['column']]
        selected_comp_id = comp_row

        print(f"selected_comp_id: {selected_comp_id}")
        season_opts = sbut.get_seasons_from_comp(selected_comp_id)
        season_opt_data = season_opts.to_dict('records')
        season_opt_cols = [{"name": i, "id": i} for i in season_opts.columns]

        return selected_comp_id, season_opt_data, season_opt_cols

@app.callback(
    Output('selected-season-id', 'value'),
    Output('select-match','data'),
    Output('select-match','columns'),
    # ---
    Input('select-season','active_cell'),
    Input('selected-comp-id', 'value')
    )
def handle_season_selection(selected_season_cell, selected_comp_id):
    print(f"data-check comp_id: {selected_comp_id}")
    if selected_season_cell:
        season_df = sbut.get_seasons_from_comp(int(selected_comp_id))
        print(f"lenght of seasondf {len(season_df)}")
        print(f"selected season row: {selected_season_cell['row']}")
        print(f"selected season col: {selected_season_cell['column']}")

        season_row = season_df.iloc[selected_season_cell['row']][selected_season_cell['column']]
        selected_season_id = season_row

        print(f"selected_season_id: {selected_season_id}")
        match_opts = sbut.get_matches_from_season(selected_season_id, selected_comp_id)
        match_opt_data = match_opts.to_dict('records')
        match_opt_cols = [{"name": i, "id": i} for i in match_opts.columns]
        return selected_season_id, match_opt_data, match_opt_cols

@app.callback(
    Output('selected-match-id', 'value'),  
    Output('select-player','data'),
    Output('select-player', 'columns'),
    #--
    Input('selected-season-id', 'value'),
    Input('selected-comp-id', 'value'),
    Input('select-match', 'active_cell'),
    )
def handle_match_selection(selected_season_id, selected_comp_id, selected_match_cell):
    if selected_match_cell:  
        print(f"match-selected_season: {selected_season_id}")
        print(f"match-selected_comp: {selected_comp_id}")
        matches_df = sbut.get_matches_from_season(selected_season_id, selected_comp_id)
        selected_match_id = matches_df.iloc[selected_match_cell['row']][selected_match_cell['column']]
        # could check if match id hasn't changed- to avoid refetching data
        player_opts = sbut.get_lineups_from_match(selected_match_id)

        player_opts_data = player_opts.to_dict('records')
        player_opts_cols = [{"name": i, "id": i} for i in player_opts.columns]
    
        return selected_match_id, player_opts_data, player_opts_cols

# Analysis 
@app.callback(
    Output(component_id='player_name_output', component_property='children'),
    Output(component_id='player-shot-plot', component_property='figure'),
    Output('player-heat-plot', 'figure'),
    Output('player-pass-plot', 'figure'),
    Output('pass-basics', 'data'),
    Output('pass-length-plot', 'figure'),
    Output('dribble-basics', 'data'),
    Output('player-dribble-plot', 'figure'),
    Output('player-match-sumr-table', 'columns'),
    Output('player-match-sumr-table', 'data'),
    Output('shot-stats-table','columns'),
    Output('shot-stats-table','data'),
    Output('shot-dets-table','columns'),
    Output('shot-dets-table','data'),
    # ------
    Input('selected-match-id', 'value'),
    Input('select-player', 'active_cell'),
    Input('heat-select-ball', 'value'),
    Input('heat-select-defense', 'value'),
    Input('heat-select-other', 'value')
)
def update_player_analysis_div(selected_match_id, active_cell, ball_evs, def_evs, other_evs):
    if active_cell:
        #selected_player = df_t.iloc[active_cell['row']][active_cell['column']]
        
        players_df = sbut.get_lineups_from_match(selected_match_id)
        selected_player = players_df.iloc[active_cell['row']][active_cell['column']]
        print(f"final selected player {selected_player}")
        
        name_string = f'{selected_player}'
        
        print(selected_player)
        # source data
        #df_e = euro_combo_df
        df_e = sb.events(match_id=selected_match_id, split=True, flatten_attrs=True)

        # player shots
        shot_plot = plot_player_shots(df_e, selected_player)
        shot_stats = make_shot_stats_table(df_e, selected_player)
        shot_details = make_shot_details_table(df_e, selected_player)

        shot_sum_cols = [{"name": i, "id": i} for i in shot_stats.columns]
        shot_sum_data = shot_stats.to_dict('records')
        shot_dets_cols = [{"name": i, "id": i} for i in shot_details.columns]
        shot_dets_data = shot_details.to_dict('records')

        # player passes
        pass_plot = plot_player_passes(df_e, selected_player)
        pass_basics_data = make_pass_table_basic(df_e, selected_player).to_dict('records')
        pass_length_plot = make_pass_length_bars(df_e, selected_player)

        # player dribbles
        dribble_plot = make_player_dribble_plot(df_e, selected_player)
        dribble_basics_data = make_dribble_table_basic(df_e, selected_player).to_dict('records')

        # -------------
        # Viz using all events dataframe
        df_all_evs = sb.events(match_id=selected_match_id, split=False, flatten_attrs=True)
        
        player_match_summary = make_player_match_summary(df_all_evs, selected_player)
        psum_data = player_match_summary.to_dict('records')
        psum_cols = [{"name": i, "id": i} for i in player_match_summary.columns]

        # player event heatmap
        selected_events = ball_evs + def_evs + other_evs
        df_sel_evs = df_all_evs[df_all_evs['type'].isin(selected_events)]
        heat_plot = plot_player_heat(df_sel_evs, selected_player, title='Selected Player Events')
        return name_string, shot_plot, heat_plot, pass_plot, pass_basics_data, pass_length_plot, dribble_basics_data, dribble_plot, psum_cols, psum_data, shot_sum_cols, shot_sum_data, shot_dets_cols, shot_dets_data

@app.callback(
    Output('centers-fig1', 'figure'),
    Output('clusters-fig1', 'children'),
    Output('centers-fig2', 'figure'),
    Output('clusters-fig2', 'children'),
    #---
    Input('barca-manager-select1', 'value'),
    Input('barca-manager-select2', 'value'),
    Input('xg-min-select', 'value')
)
def update_manager_clusters(selected_manager1, selected_manager2, selected_xg_min):
    df_freq, cl_figs, center_fig, df_centers = sbut.make_barca_manager_clusters(selected_manager1, float(selected_xg_min))
    df_freq2, cl_figs2, center_fig2, df_centers2 = sbut.make_barca_manager_clusters(selected_manager2, float(selected_xg_min))

    cl_dcc_graphs = []
    for i, fig_i in enumerate(cl_figs):
        cl_dcc_graphs.append(dcc.Graph(
            id='graph-{}'.format(i),
            figure=fig_i
        ))

    cl_dcc_graphs2 = []
    for i, fig_i in enumerate(cl_figs2):
        cl_dcc_graphs2.append(dcc.Graph(
            id='graph-{}'.format(i),
            figure=fig_i
        ))

    return center_fig, cl_dcc_graphs, center_fig2, cl_dcc_graphs2

# ------------------
# Run App
# ------------------

if __name__ == '__main__':
    app.run_server(debug=True)





import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

import pandas as pd
import numpy as np

import sbutilities as sbut

def draw_pitch_lines(fig, length=120, width=80, line_color="LightGrey", below=True):
    
    lay_arg = 'below' if below else 'above'
        
    
    fig.update_layout(
    width = 700, 
    height = 600)
        
    fig.update_xaxes(range=(0, 120),
                    showgrid=False,
                    visible=False,
                    showticklabels=False)
    
    #fig.update_yaxes(range=(0, 80))
    #fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(
        range=(0, width),
        scaleanchor = "x",
        scaleratio = 1,
        showgrid=False,
        visible=False,
        showticklabels=False
      )
    # change background color outside plot area
    # ... and inside plot area
    fig.update_layout(paper_bgcolor="#1A1A1A",
                     plot_bgcolor="#1A1A1A")

    # left penalty box
    fig.add_shape(type="rect",
        xref="x", yref="y",
        x0=0, y0=60,
        x1=18, y1=20,
        line=dict(
            color=line_color,
            width=3,
        ),
        layer=lay_arg
    )

    # left 6 yard box
    fig.add_shape(type="rect",
        xref="x", yref="y",
        x0=0, y0=48,
        x1=6, y1=32,
        line=dict(
            color=line_color,
            width=3,
        ),
        layer=lay_arg
    )

    # right penalty box
    fig.add_shape(type="rect",
        xref="x", yref="y",
        x0=102, y0=60,
        x1=120, y1=20,
        line=dict(
            color=line_color,
            width=3,
        ),
        layer=lay_arg
    )

    # right 6 yard box
    fig.add_shape(type="rect",
        xref="x", yref="y",
        x0=114, y0=48,
        x1=120, y1=32,
        line=dict(
            color=line_color,
            width=3,
        ),
        layer=lay_arg
    )

    # halfway line
    fig.add_shape(type="line",
        xref="x", yref="y",
        x0=60, y0=80,
        x1=60, y1=0,
        line=dict(
            color=line_color,
            width=3,
        ),
        layer=lay_arg
    )
    # left endline
    fig.add_shape(type="line",
        xref="x", yref="y",
        x0=0, y0=80,
        x1=0, y1=0,
        line=dict(
            color=line_color,
            width=3,
        ),
        layer=lay_arg
    )
    # right endline
    fig.add_shape(type="line",
        xref="x", yref="y",
        x0=120, y0=80,
        x1=120, y1=0,
        line=dict(
            color=line_color,
            width=3,
        ),
        layer=lay_arg
    )
    # upper sideline
    fig.add_shape(type="line",
        xref="x", yref="y",
        x0=0, y0=80,
        x1=120, y1=80,
        line=dict(
            color=line_color,
            width=3,
        ),
        layer=lay_arg
    )
    # lower sideline
    fig.add_shape(
        type="line",
        xref="x", yref="y",
        x0=0, y0=0,
        x1=120, y1=0,
        line=dict(
            color=line_color,
            width=3,
        ),
        layer=lay_arg
    )
    # center circle
    fig.add_shape(type="circle",
        xref="x", yref="y",
        x0=50, y0=50,
        x1=70, y1=30,
        line=dict(
            color=line_color,
            width=3,
        ),
        layer=lay_arg
    )

    return fig

def plot_frame(row, table=False, viz_ar=False):
    
    # check for missing frame 
    if row['freeze_frame'] is np.nan:
        fig = px.scatter()
        fig = draw_pitch_lines(fig)
        fig.add_annotation(x=30, y=10,
            text="No Frame Data Available",
            showarrow=False,
            yshift=0, 
            font=dict(
                size=18,
                color='Grey')
            )
        return fig
    
    frame = pd.DataFrame(row['freeze_frame'])
    frame['x'] = frame.apply(lambda row: row['location'][0], axis=1)
    frame['y'] = frame.apply(lambda row: row['location'][1], axis=1)
    if table:
        display(frame)
    
    fig = px.scatter(frame, x="x", y="y", color='teammate', symbol='actor')
    
    if viz_ar:
        pass
    
    fig = draw_pitch_lines(fig)
    return fig

def plot_shots_xg(df, pens=False, title=None):
    
    if not pens: 
        df = df[df['shot_type']!= 'Penalty']
        
    if title:
        title_string=title
    else: 
        title_string="Shots - xG"
        
    # check for no shot data 
    if len(df) == 0:
        fig = px.scatter()
        fig = draw_pitch_lines(fig)
        fig.add_annotation(x=30, y=10,
            text="No Shots to Display",
            showarrow=False,
            yshift=0, 
            font=dict(
                size=18,
                color='Grey')
            )
        return fig
    
    # proceeding with shot processing
    x = [loc[0] for loc in df['location'].values]
    y = [loc[1] for loc in df['location'].values]
    
    s_size = 30*df['shot_statsbomb_xg'].values
    s_color = [1 if i == 'Goal' else 0 for i in df['shot_outcome']]
    s_symbol = list(df['shot_outcome'].values)
    
    fig = px.scatter(x=x, y=y,
                     size=s_size, 
                     color=s_color, color_continuous_scale='redor',
                     symbol=s_symbol,
                     title=title_string
                     )
    fig.update_coloraxes(showscale=False)
    fig.update_layout(
        font_color="LightBlue",
        title_font_color="white",
        legend_title_font_color="lightGrey"
    )
    fig = draw_pitch_lines(fig)
    
    return fig

def plot_event_heat_rect(df, title=None):
    """
    rectangle
    """
    # check for no event data
    if len(df) == 0:
        fig = px.scatter()
        fig = draw_pitch_lines(fig)
        fig.add_annotation(x=30, y=10,
            text="No Events to Display",
            showarrow=False,
            yshift=0, 
            font=dict(
                size=18,
                color='Grey')
            )
        return fig
    
    if title:
        title_string=title
    else: 
        title_string='All Events'
    
    x = [loc[0] for loc in df['location'].dropna()]
    y = [loc[1] for loc in df['location'].dropna()]
    
    fig = go.Figure(go.Histogram2d(x=x, y=y, 
        autobinx=False,
        xbins=dict(start=0, end=120, size=10),
        autobiny=False,
        ybins=dict(start=0, end=80, size=10),
        #colorscale=[[0, 'rgb(12,51,131)'], [0.25, 'rgb(10,136,186)'], [0.5, 'rgb(242,211,56)'], [0.75, 'rgb(242,143,56)'], [1, 'rgb(217,30,30)']]
    ))
    
    fig.update_layout(
        title={
            'text': title_string,
            'font' :{'color' : 'white'}
        })
    # add pitch lines
    fig = draw_pitch_lines(fig, below=False)
    
    return fig

def plot_pass_arrow(fig, event, pass_color='LightSeaGreen', verbose=False):
    
    start_loc = event['location']
    end_loc = event['pass_end_location']
    height = event['pass_height']

    
    if verbose:
        print(f"start: {start_loc}")    
        print(f"start: {start_loc}")
        print(f"end: {end_loc}")
        print(f"height: {height}")

    fig.add_annotation(
        ax=start_loc[0],  # arrows' head
        ay=start_loc[1],  # arrows' head
        x=end_loc[0],  # arrows' tail
        y=end_loc[1],  # arrows' tail
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        text='',  # if you want only the arrow
        showarrow=True,
        arrowhead=3,
        arrowsize=1,
        arrowwidth=1,
        arrowcolor=pass_color
    )
    
    return fig

def plot_passes(df, title=None):
    """
    df: expects flattened sb event dataframe
    """
    # check for no event data
    if len(df) == 0:
        fig = px.scatter()
        fig = draw_pitch_lines(fig)
        fig.add_annotation(x=30, y=10,
            text="No Events to Display",
            showarrow=False,
            yshift=0, 
            font=dict(
                size=18,
                color='Grey')
            )
        return fig
    
    df['pass_outcome'] = df['pass_outcome'].fillna('Complete')
    
    req_cols = ['location', 'pass_outcome', 'pass_height']
    df = df.loc[df[req_cols].dropna(how='any').index]

    x = [loc[0] for loc in df['location'].values]
    y = [loc[1] for loc in df['location'].values]
    p_color = [oc for oc in df['pass_outcome']]
    p_ht  = [ht for ht in df['pass_height']]
    
    
    color_dict = {'Complete': 'LightSeaGreen',
              'Incomplete': 'Yellow',
              'Unknown': 'Gray',
              'Out' : 'Yellow',
              'Pass Offside': 'Gray'}

    # plot pass starting points    
    fig = px.scatter(x=x, y=y, color=p_color, color_discrete_map=color_dict)
    
    fig.update_traces(marker=dict(size=3),
                  selector=dict(mode='markers'))
    
    for index, row in df.iterrows():
        arrow_color = color_dict[row['pass_outcome']]
        #line_type = line_dict[row['pass_height']]
        fig = plot_pass_arrow(fig, row, pass_color=arrow_color)
    
    # display adjustments 
    if title:
        title_string=title
    else: 
        title_string='All Passes'
           
    fig.update_layout(
        title={
            'text': title_string,
            'font' :{'color' : 'white'}
        })
    
    fig = draw_pitch_lines(fig)
    return fig


def pass_length_bar_plot(df, title=None):
    df['pass_outcome'] = df['pass_outcome'].fillna('Complete')

    counts, bins = np.histogram(df['pass_length'], bins=range(0,100,5))
    bins = 0.5 * (bins[:-1] + bins[1:])


    fig = px.bar(df, x=bins, y=counts, labels={'x':'Pass Length (m)', 'y':'No. Passes'}, title="Pass Lengths")
    fig.update_layout(paper_bgcolor="#1A1A1A",
                 plot_bgcolor="#1A1A1A") #'#112'

    if title:
        title_string=title
    else: 
        title_string='Pass Lengths'
    
    # layout Updates
    fig.update_layout(
        title={
            'text': title_string,
            'font' :{'color' : 'white'}
        })

    fig.update_layout(
    width = 700, 
    height = 600)

    return fig

def plot_event_scatter_generic(df, title=None):
    
    # check for no event data
    if len(df) == 0:
        fig = px.scatter()
        fig = draw_pitch_lines(fig)
        fig.add_annotation(x=30, y=10,
            text="No Events to Display",
            showarrow=False,
            yshift=0, 
            font=dict(
                size=18,
                color='Grey')
            )
        return fig
    
    df = sbut.expand_sb_location_col(df)
    
    fig = px.scatter(df, x='loc_x', y='loc_y', color='dribble_outcome')
    fig = draw_pitch_lines(fig)
    
    
    # display adjustments 
    if title:
        title_string=title
    else: 
        title_string='Event Locations'
           
    fig.update_layout(
        title={
            'text': title_string,
            'font' :{'color' : 'white'}
        })
    
    return fig
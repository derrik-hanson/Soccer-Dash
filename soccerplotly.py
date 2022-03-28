import plotly.express as px

import pandas as pd
import numpy as np


def draw_pitch_lines(fig, length=120, width=100, line_color="LightGrey", below=True):
    
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
    fig.update_layout(paper_bgcolor="#112",
                     plot_bgcolor="#112")

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

def plot_pass_arrow(fig, event, pass_color='LightSeaGreen'):
    print("-- pass info --")
    start_loc = event['location']
    print(f"start: {start_loc}")
    end_loc = event['pass']['end_location']
    print(f"end: {end_loc}")
    height = event['pass']['height']
    print(f"height: {height}")

    fig.add_annotation(
        x=start_loc[0],  # arrows' head
        y=start_loc[1],  # arrows' head
        ax=end_loc[0],  # arrows' tail
        ay=end_loc[1],  # arrows' tail
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

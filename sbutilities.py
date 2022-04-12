import json
import pandas as pd
import numpy as np
from statsbombpy import sb

#--------------------
# Data Loading and Preprocessing
#--------------------

def get_local_360_file(mid):
    base_path = "/Users/Spade5/Downloads/three_sixty_data/"
    full_path = base_path + str(mid) + ".json"
    
    with open(full_path) as f:
        t6 = json.load(f)
    
    all_frames = pd.DataFrame(t6)
    return all_frames


def join_events_split_to_frames(df_frames, events_split_dict):
    """
    events_split_dict: expects values returned by 
    -- sb.events(match_id=<int>, split=True, flatten_attrs=False)
    df_frames: expects values returned by
    -- sbut.get_local_360_file(euro_final_mid)
    -- sbut is from statsbombutilities.py
    """
    out_dict = dict()
    for e in events_split_dict:
        out_dict[e] = events_split_dict[str(e)].join(df_frames.set_index('event_uuid'),on='id')
        
    return out_dict

# UI selection 
def get_comp_opts():
    data_path = '/Users/Spade5/DSA/Projects/Soccer-Dash/comp_opts.csv'
    return pd.read_csv(data_path)

def get_seasons_from_comp(selected_comp_id):
    all_comps = sb.competitions()
    season_opts = all_comps[all_comps['competition_id']==selected_comp_id]
    season_opts = season_opts[['competition_name','season_name','competition_gender','competition_youth','season_id']]
    season_opts = season_opts.sort_values('season_name')
    return season_opts

def get_matches_from_season(selected_season_id, selected_comp_id):
    match_opts = sb.matches(competition_id=selected_comp_id, season_id=selected_season_id)
    match_opts = match_opts[['match_date','home_team','away_team', 'home_score', 'away_score','match_id']]
    return match_opts

def get_lineups_from_match(selected_match_id):
    lineups = sb.lineups(match_id=selected_match_id)
    teams = list(lineups.keys())
    lineup_team_0 = lineups[teams[0]]
    lineup_team_0['team'] = teams[0]
    lineup_team_1 = lineups[teams[1]]
    lineup_team_1['team'] = teams[1]
    lineups = pd.concat([lineups[teams[0]],lineups[teams[1]]])
    lineups = lineups[['team','player_name','player_nickname','jersey_number','country','player_id']]
    return lineups

def get_teams_from_match(m_id):
    lineups = sb.lineups(match_id=selected_match_id)
    teams = list(lineups.keys())
    return teams

# --------------
# player tools
# --------------
def get_starting_players(df, team):
    """
    expects dataframe input of type returned by: 
    df = sb.events(match_id=3795506, split=True, flatten_attrs=True)
    ---
    team: str
    """
    df_xis = df['starting_xis']
    lineup = df_xis[df_xis['team']==team]['tactics'].iloc[0]['lineup']

    p_hold = []
    for idx, _ in enumerate(lineup):
        p1 = pd.DataFrame([lineup[idx]['player']])
        p2 = pd.DataFrame([lineup[idx]['position']])
        p3 = pd.DataFrame([lineup[idx]['jersey_number']])

        df_players = pd.concat([p1, p2, p3], axis=1)
        df_players.columns = ['player_id', 'player_name', 'position_id', 'position_name', 'jersey_number']

        p_hold.append(df_players)

    return pd.concat(p_hold).reset_index(drop=True)

def get_substitution_players(df, team):
    """
    expects dataframe input of type returned by: 
    df = sb.events(match_id=3795506, split=True, flatten_attrs=True)
    ---
    team: str
    """
    
    subs = df['substitutions']
    out = subs[subs['team']==team][['substitution_replacement','position']].reset_index(drop=True)
    out.columns = ['player_name', 'position_name']
    return out

def get_starting_players(df, team):
    """
    expects dataframe input of type returned by: 
    df = sb.events(match_id=3795506, split=True, flatten_attrs=True)
    ---
    team: str
    """
    df_xis = df['starting_xis']
    lineup = df_xis[df_xis['team']==team]['tactics'].iloc[0]['lineup']

    p_hold = []
    for idx, _ in enumerate(lineup):
        p1 = pd.DataFrame([lineup[idx]['player']])
        p2 = pd.DataFrame([lineup[idx]['position']])
        p3 = pd.DataFrame([lineup[idx]['jersey_number']])

        df_players = pd.concat([p1, p2, p3], axis=1)
        df_players.columns = ['player_id', 'player_name', 'position_id', 'position_name', 'jersey_number']

        p_hold.append(df_players)

    return pd.concat(p_hold).reset_index(drop=True)

def get_all_team_players_match(df, team):
    """
    expects dataframe input of type returned by: 
    df = sb.events(match_id=3795506, split=True, flatten_attrs=True)
    ---
    team: str
    """
    starts = get_starting_players(df, team)
    subs = get_substitution_players(df, team)
    
    common_cols = ['player_name', 'position_name']
    return pd.concat([starts[common_cols], subs[common_cols]]).reset_index(drop=True)


# basic version to be improved with team names
def get_player_names_from_events(df_split):
    lineups = df_split['starting_xis']['tactics'].values
    team1 = [p['player']['name'] for p in lineups[0]['lineup']]
    team2 = [p['player']['name'] for p in lineups[1]['lineup']]
    starters = team1 + team2
    #print(f"--- starters --- \n {starters}")
    
    subs = euro_final_events['substitutions']['substitution_replacement'].tolist()
    #print(f"--- subs --- \n {subs}")
    
    return starters + subs

def playingtime_from_match(df):
    """
    df: pandas DataFrame of kind
    - df_sb = sb.events(match_id=match_id, split=False, flatten_attrs=True)
    """
    #--
    match_id = df.iloc[0]['match_id']
    #-- Starting lineups
    team1 = df.loc[0]['team']
    team1_lineup = [p['player']['name'] for p in df.loc[0]['tactics']['lineup']]

    team2 = df.loc[1]['team']
    team2_lineup = [p['player']['name'] for p in df.loc[1]['tactics']['lineup']]

    team_dat = {
        team1: team1_lineup,
        team2: team2_lineup
    }

    player_times = dict()

    for key, val in team_dat.items():
        for p in val:
            player_times[p] = {
                'team': key,
                'on':[0,0], 
                'off': [np.nan,np.nan]
            }

    #-- Handle Sub Events
    sub_events = df[df['type']=='Substitution']

    sub_events = sub_events[['team','player','substitution_replacement','period','timestamp','minute','second']]
    sub_events

    for index,s in sub_events.iterrows():
        off_player = s['player']
        on_player = s['substitution_replacement']

        player_times[off_player]['off'] = [s['minute'],s['second']] 
        player_times[on_player] = {
                'team': s['team'],
                'on':[s['minute'],s['second']],
                'off': [np.nan,np.nan]
            }
    
    #-- End of Match 
    half_ends = df[df['type']=='Half End']

    # half_ends = half_ends[['period','timestamp','minute','second']]
    end_match = half_ends.loc[half_ends['period']==2]
    end_match = end_match.iloc[0]

    for d in player_times.values():
        if np.isnan(d['off'][0]) == True:
            d['off'] = [end_match['minute'],end_match['second']]

    #-- Calculate total time
    for d in player_times.values():
        d['total_time_sec'] = (d['off'][0]*60 + d['off'][1]) - (d['on'][0]*60 + d['on'][1]) 
        # convert to decimal time 
        d['total_time_dec'] = round(d['total_time_sec']/60,2)

    # prepare dataframe
    pre_df = []
    for p in player_times.keys(): 
        pre_df.append({'player_name':p, 'time_played_mins':player_times[p]['total_time_dec'],
                       'team': player_times[p]['team'], 'match_id':match_id})
        
    return pd.DataFrame(pre_df)

def get_player_match_summary(df, player_name, m_id=None, pretty=True):
    
    # if m_id != None):
    #     df = sb.events(match_id=m_id)

    all_events = df
    
    # get match playing time dataframe
    pt_df = playingtime_from_match(all_events)
    
    player_evs = all_events.loc[all_events['player']==player_name]
    
    #- All False mask, for error handling
    all_false_mask = np.repeat(False, len(player_evs.index))
    
    #- shots
    shots_mask = player_evs['type']=='Shot'
    goal_mask = player_evs['shot_outcome'] == 'Goal'
    #- passes
    pass_mask = player_evs['type'] == 'Pass'
    pass_comp_mask = np.logical_not(player_evs['pass_outcome'].notna())
    pass_incomp_mask = player_evs['pass_outcome']=='Incomplete'
    
    try:
        assist_mask = player_evs['pass_goal_assist']==True
    except:
        assist_mask = all_false_mask
        
    #- dribbles
    carry_mask = player_evs['type']=='Carry'
    dribble_mask = player_evs['type']=='Dribble'
    dribble_comp_mask = player_evs['dribble_outcome']=='Complete'
    
    shot_cols = ['shot_body_part',
                'shot_end_location',
                'shot_first_time',
                'shot_freeze_frame',
                'shot_key_pass_id',
                'shot_one_on_one',
                'shot_outcome',
                'shot_redirect',
                'shot_statsbomb_xg',
                'shot_technique',
                'shot_type']
    #- Shots 
    goal_evs = player_evs[np.logical_and(shots_mask,goal_mask)]#[shot_cols]
    shot_evs = player_evs[shots_mask]
    # xG
    total_xg = shot_evs['shot_statsbomb_xg'].sum()
    non_goal_xg = player_evs[np.logical_and(shots_mask,np.logical_not(goal_mask))]['shot_statsbomb_xg'].sum()
     

    #- Passes
    pass_evs = player_evs[pass_mask]
    pass_comp_evs = player_evs[np.logical_and(pass_mask, pass_comp_mask)]
    pass_incomp_evs = player_evs[pass_incomp_mask]
    assist_evs = player_evs.loc[assist_mask]

    
    #- Dribbles
    carry_evs = player_evs[carry_mask]
    dribble_evs = player_evs[dribble_mask]
    dribble_comp_evs = player_evs[dribble_comp_mask]

    #---- Create Summary dict
    metric_dfs = {'goals': goal_evs,
                  'assists': assist_evs,
                  'shots': shot_evs,
                  'passes_attempted':pass_evs ,
                  'passes_complete': pass_comp_evs,
                  'passes_incomplete': pass_incomp_evs,
                  'carrys': carry_evs,
                  'dribbles': dribble_evs,
                  'dribbles_complete': dribble_comp_evs
                 }
    
    metrics = {k:len(v.index) for k,v in metric_dfs.items()}
    

    #----- Calculating Derived Metrics
    metrics['pass_completion_percent'] = 0 if metrics['passes_attempted'] == 0 else \
                                            metrics['passes_complete'] / metrics['passes_attempted']
    metrics['goals_minus_xg'] = metrics['goals']- total_xg
    metrics['goals_over_xg'] = metrics['goals']/total_xg if total_xg > 0 else 0
    metrics['total_xg'] = total_xg
    metrics['non-goal_xg'] = non_goal_xg
    
    
    #----- Incorporate Playing Time 
    t_played = metrics['playing_time'] = pt_df.loc[pt_df['player_name']==player_name]['time_played_mins'].item()
    
    metrics_90 = {str(f"{k}/90"):round(v/(t_played/90),2) for k,v in metrics.items()}
    
    #- Add player name
    metrics['player_name'] = player_name
    metrics_90['player_name'] = player_name
    
    metrics['match_id'] = m_id
    metrics_90['match_id'] = m_id
    
    
    #- Create final player summary dataframe
    metrics_df = pd.DataFrame([metrics]).set_index('player_name')
    metrics_90_df = pd.DataFrame([metrics_90]).set_index('player_name')
    
    plyr_sum_df = pd.concat([metrics_df, metrics_90_df], axis=1)

    if pretty:
        plyr_sum_df['total_xg'] = plyr_sum_df['total_xg'].apply(lambda x: round(x,3))
        plyr_sum_df['pass_completion_percent'] = plyr_sum_df['pass_completion_percent'].apply(lambda x: round(x,3))

    return plyr_sum_df
    

def make_team_match_summary(match_id, player_list=None, team_name=None, pretty_d=False):
    """
    match_id : int
    player_list= None : list (optional)
    team_name= None : str (optional. required if player list also provided)
    pretty_d=False : bool (optional) round derived metrics for display
    """
    if player_list is None:
        all_players = sbut.playingtime_from_match(df_L)
        team_mask = all_players['team']==team_name
        team_players = all_players[team_mask]
        player_list = team_players['player_name'].values.tolist()

    group_sum = []
    for player in player_list:

        use_cols = ['goals', 'total_xg','shots','assists', 'pass_completion_percent', 'carrys', 'dribbles_complete','playing_time']

        player_sum = get_player_match_summary(player, match_id)[use_cols]
        group_sum.append(player_sum)
        df_team = pd.concat(group_sum)
        
        if pretty_d:
            #-- 
            # clean up display 
            df_team['total_xg'] = round(df_team['total_xg'],3)
            df_team['pass_completion_percent'] = round(df_team['pass_completion_percent'],2)
    
    return df_team

def expand_sb_location_col(df, split_col='location'):
    """
    df: pandas dataframe with column 'location' and location values as list of form [int, int]
    split_col - str : the column in df to split
    """
    sb_pitch_y_dim = 80
    if len(df)>0:
        if split_col == 'location':
            locs_temp = df['location'].copy()
            locs_temp = locs_temp.apply(pd.Series)
            locs_temp.columns = ['loc_x', 'loc_y_raw']
            locs_temp['loc_y'] = sb_pitch_y_dim - locs_temp['loc_y_raw']
            return pd.concat([df, locs_temp], axis=1)
        else: 
            # can add validation later
            # try: 
            locs_temp = df[split_col].copy()
            locs_temp = locs_temp.apply(pd.Series)
            locs_temp.columns = [split_col + '_loc_x', split_col + '_loc_y_raw']
            locs_temp[split_col + '_loc_y'] = sb_pitch_y_dim - locs_temp[split_col + '_loc_y_raw']
            return pd.concat([df, locs_temp], axis=1)

    else: 
        df[:,'loc_x'] = None
        df[:,'loc_y'] = None
        df[:, 'loc_y_raw'] = None
        return df

# mostly unnecessary now
def extract_shot_details(df_a):
    """
    handles df returned by
    sb.events(match_id=3795506, split=True, flatten_attrs=False)['shots']
    ---
    obviated by changing flatten_attrs in above to True:
    sb.events(match_id=<int>, split=True, flatten_attrs=True)['shots']
    --
    --
    returns: new data frame which is a copy of the original and details columns added
    ---
    usage: 
    df = extract_shot_details(df)
    """
    
    df = df_a.copy()
    df['xg'] = df.apply(lambda x: x['shot'].get('statsbomb_xg'), axis=1)
    df['type'] = df.apply(lambda x: x['shot'].get('type')['name'], axis=1)
    df['end_location'] = df.apply(lambda x: x['shot'].get('end_location'), axis=1)
    df['body_part'] = df.apply(lambda x: x['shot'].get('body_part'), axis=1)
    df['shot_frame'] = df.apply(lambda x: x['shot'].get('freeze_frame'), axis=1)
    df['technique'] = df.apply(lambda x: x['shot'].get('technique'), axis=1)
    df['outcome_name'] = df.apply(lambda x: x['shot'].get('outcome')['name'], axis=1)
    return df

def get_shot_stats(df, split=True, pretty=True):
    """
    df : pandas Dataframe like sb.events(match_id=<>, split=True, flatten_attrs=True)['shots']
    """
    # Masks 
    goal_mask = df['shot_outcome'] == 'Goal'
    non_penalty_mask = df['shot_type'] != 'Penalty'
    # add no pens mask 
    
    # ---- 
    avg_xg = df['shot_statsbomb_xg'].mean()
    num_goals = len(df[np.logical_and(goal_mask, non_penalty_mask)])
    num_shots = len(df['index'])
    
    df_out = pd.DataFrame([[num_goals, avg_xg,  num_shots]])
    df_out.columns = ['goals', 'average_xg', 'shots_taken']

    # clean up for display
    if pretty:
        df_out['average_xg'] = df_out['average_xg'].apply(lambda x: round(x,3))
    
    return df_out

def get_shot_details_table(df):
    """
    df : pandas Dataframe like sb.events(match_id=<>, split=True, flatten_attrs=True)['shots']
    """
    
    shot_details_cols = ['shot_outcome','play_pattern','minute','period']
    df_out = df[shot_details_cols]
    return df_out

def get_pass_stats_basics(df_p):
    """
    expects df input returned by: 
    sb.events(<matchid>, Flat=True, Split=True)
    """

    df_p['pass_outcome'].fillna('Complete', inplace=True)
    pvt_player_pass = pd.pivot_table(df_p, values='index', index=['pass_height'],
                        columns=['pass_outcome'], aggfunc='count')
    
    pvt_player_pass.fillna(0, inplace=True)
    pvt_player_pass = pvt_player_pass.astype('int')

    def get_percent(a, b):
        return round((a / (a+b)),2)

    if set(['Complete','Incomplete']).issubset(pvt_player_pass.columns.tolist()):
        pvt_player_pass['Completion_Percent'] = get_percent(pvt_player_pass['Complete'],pvt_player_pass['Incomplete'])
    elif 'Incomplete' not in pvt_player_pass.columns.tolist():
        pvt_player_pass['Completion_Percent'] = 1.00
    elif 'Complete' not in pvt_player_pass.columns.tolist():
        pvt_player_pass['Completion_Percent'] = 0.00
    else:
        pvt_player_pass['Completion_Percent'] = 0.00

    pvt_player_pass = pvt_player_pass.reset_index()

    pvt_player_pass = pvt_player_pass.rename(
    {'pass_height': 'Pass Height','Completion_Percent': 'Completion Percent'}, axis=1)

    #pvt_player_pass['Success Rate'] = round(100*pvt_player_pass['Success Rate'],0)

    return pvt_player_pass



#-----
def make_dribble_stats_table(df):
    """
    df : pandas dataframe sb(split=True, flat=True)['dribbles']
    """

    def get_percent(a, b, disp=1):
        """
        a : number
        b : number
        disp : number. display results relateive to 1 or 100
        decs : number. number of decimals to display
        """
        if (a+b) ==0: 
            out = 0
        else:
            out = a / (a+b)
            
        if disp ==100:
            out = out*100

        return round(out, 2)
    
    # get df data 
    dr_disp = df[['dribble_outcome','id', 'under_pressure']]
    df_in = pd.pivot_table(dr_disp, values='id', index='under_pressure',
                  columns=['dribble_outcome'], aggfunc='count')
    
    
    # dribble_data_baseline
    data_baseline = [[True, 0, 0, 0, 0],[False,0,0, 0, 0]]
    dr_stats = pd.DataFrame(data_baseline)
    dr_stats.columns = ['Under Pressure','Complete', 'Incomplete', 'Total', 'Success Rate']
    dr_stats = dr_stats.set_index('Under Pressure', drop=True)

    # add stats to table
    if len(df_in)>0: 
        if True in df_in.index:
            if 'Complete' in list(df_in.columns):
                dr_stats.at[True, 'Complete'] = df_in.loc[True, 'Complete']
            if 'Incomplete' in list(df_in.columns):
                dr_stats.at[True, 'Incomplete'] = df_in.loc[True, 'Incomplete']

        if False in df_in.index:
            if 'Complete' in list(df_in.columns):
                dr_stats.at[False, 'Complete'] = df_in.loc[False, 'Complete']
            if 'Incomplete' in list(df_in.columns):
                dr_stats.at[False, 'Incomplete'] = df_in.loc[False, 'Incomplete']

    # update success rate column
    dr_stats['Total'] = dr_stats['Complete'] + dr_stats['Incomplete']
    
    # add totals row
    totals = pd.DataFrame([[dr_stats['Complete'].sum(), dr_stats['Incomplete'].sum(), dr_stats['Total'].sum(), 0]])
    totals.columns = ['Complete','Incomplete','Total', 'Success Rate']
    dr_stats = pd.concat([dr_stats, totals])
    
    dr_stats['Success Rate'] = dr_stats.apply(lambda row: get_percent(row['Complete'], row['Incomplete'], disp=100), axis=1)
    
    # update with 'totals' index name
    dr_stats.index = dr_stats.index.astype('str')
    dr_stats = dr_stats.rename({'0':'Totals'}, axis='index')
    
    # reorder columns
    dr_stats = dr_stats[['Total','Success Rate', 'Complete', 'Incomplete']]

    dr_stats = dr_stats.reset_index()
    dr_stats = dr_stats.rename({'index':'Under Pressure'}, axis=1)
    
    return dr_stats


#-------------------
# Team Functions 
#-------------------


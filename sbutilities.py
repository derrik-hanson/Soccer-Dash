import json
import pandas as pd
import numpy as np
import statsbombpy as sb

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

    pvt_player_pass['Completion_Percent'] = get_percent(pvt_player_pass['Complete'],pvt_player_pass['Incomplete'])
    pvt_player_pass = pvt_player_pass.reset_index()

    return pvt_player_pass

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

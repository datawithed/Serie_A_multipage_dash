# -*- coding: utf-8 -*-
"""
Created on Sun Jul  3 08:53:43 2022

@author: Ed.Morris
"""

# pass maps page

# Import modules
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import numpy as np
import pandas as pd
import json
import os
from mplsoccer import Pitch, VerticalPitch

# Configure page
st.set_page_config(page_title = 'Pass maps', page_icon = Image.open('arrow.jpg'))

st.sidebar.success('Select an analysis above.')

# Set font
font1 = font_manager.FontProperties(family = 'Tahoma')
font = {'fontname':'Tahoma'}

# Load data
def load_data():
    # Set wd path
    #rfp_path = r"C:\Users\ed.morris\Documents\Python Scripts\Wyscout"
    #os.chdir(rfp_path)

    # Read in json to variable 'data'
    with open('Sample event data.txt') as json_file:
        data = json.load(json_file)
    
    # Convert dictionary to df
    df = pd.DataFrame.from_dict(data['events'], orient = 'columns')
    
    return df

# Create shot_data df
def load_shot_data():
    df = load_data()
    # Filter all data for appropriate cols
    shot_df = df[['minute','second','type','location','player','team','shot','possession']]
    # Unnest the type col
    action = [a.get('primary') for a in shot_df.type]
    shot_df['action'] = action
    # Filter for shots
    shot_data = shot_df.loc[shot_df.action == 'shot']
    # Extract all data from dictionaries
    x_location = [x.get('x') for x in shot_data.location]
    y_location = [y.get('y') for y in shot_data.location]
    player_name = [player.get('name') for player in shot_data.player]
    desc = [d.get('secondary') for d in shot_data.type]
    body_part = [bd.get('bodyPart') for bd in shot_data.shot]
    is_goal = [g.get('isGoal') for g in shot_data.shot]
    on_target = [ot.get('bodyPart') for ot in shot_data.shot]
    xg = [xg.get('xg') for xg in shot_data.shot]
    psxg = [psxg.get('postShotXg') for psxg in shot_data.shot]
    team = [team.get('name') for team in shot_data.team]
    # Assign extracted data to columns 
    shot_data['start_x'] = x_location
    shot_data['start_y'] = y_location
    shot_data['player'] = player_name
    shot_data['team'] = team
    shot_data['description'] = desc
    shot_data['body_part'] = body_part
    shot_data['is_goal'] = is_goal
    shot_data['on_target'] = on_target
    shot_data['xG'] = xg
    shot_data['PSxG'] = psxg
    # Drop redundant cols
    shot_data = shot_data.drop(columns = ['type','shot','location','possession']).reset_index(drop=True)
    
    return shot_data

shot_data = load_shot_data()

xG_vs_mins = shot_data[['minute','second','team','xG']]
xG_vs_mins['actual_minute'] = xG_vs_mins.minute + 1

# Create passes df
df = load_data()
pass_df = df[['minute','second','type','location','player','team','pass']]
pass_df = pass_df.rename(columns = {'minute':'minute','second':'second','type':'type','location':'location','player':'player','team':'team','pass':'pass_info'})

# Pull out all relevant data from various columns containing dictionaries
team = [t.get('name') for t in pass_df.team]
x_location = [x.get('x') for x in pass_df.location]
y_location = [y.get('y') for y in pass_df.location]
player = [p.get('name') for p in pass_df.player]
player_pos = [pos.get('position') for pos in pass_df.player]
action = [a.get('primary') for a in pass_df.type]
desc = [d.get('secondary') for d in pass_df.type]

# Add these coords as new cols
pass_df['team'] = team
pass_df['start_x'] = x_location
pass_df['start_y'] = y_location
pass_df['player_name'] = player
pass_df['player_position'] = player_pos
pass_df['action'] = action
pass_df['description'] = desc

# Filter action col for appropriate dataset
passes = pass_df.loc[pass_df.action == 'pass'].reset_index(drop=True)

# Pull out pass info now 'None' have been removed from pass_info['accurate']
acc_pass = [e.get('accurate') for e in passes.pass_info]
recipient = [r.get('recipient') for r in passes.pass_info]
end = [end.get('endLocation') for end in passes.pass_info]

# Add pass info as columns
passes['accurate_pass'] = acc_pass
passes['recipient_data'] = recipient
passes['end_coords'] = end

# Pull recipients and coords from dictionaries
recipients = [r.get('name') for r in passes.recipient_data]
x_end = [x.get('x') for x in passes.end_coords]
y_end = [y.get('y') for y in passes.end_coords]

# Add recipient and end coordinates to df
passes['recipient'] = recipients
passes['end_x'] = x_end
passes['end_y'] = y_end

# Drop redundant columns
passes = passes.drop(columns = ['type','location','player','pass_info','end_coords','recipient_data']).reset_index(drop=True)

# Filter for completed passes
completed = passes.loc[passes.accurate_pass == True].reset_index(drop=True)

# Draw passmap using mplsoccer library
def passmap_plot(team,player):
    pitch = Pitch(pitch_type='wyscout', orientation = 'horizontal', pitch_color = '#1E4966', line_color = '#c7d5cc', figsize = (16,11))
    fig, axs = pitch.grid(endnote_height = 0.03, 
                          endnote_space = 0, 
                          figheight = 16, 
                          title_height = 0.06, 
                          title_space = 0, 
                          grid_height = 0.86, 
                          axis = False)
    fig.set_facecolor('#1E4966')
    
    plt.gca().invert_yaxis()
    
    if player == 'All':
        passes_filtered = passes.loc[passes.team == team].reset_index(drop=True)
    else:
        passes_filtered = passes.loc[(passes.team == team) & (passes.player_name == player)].reset_index(drop=True)
    
    pitch.arrows(passes_filtered.loc[passes_filtered.accurate_pass == True].start_x, passes_filtered.loc[passes_filtered.accurate_pass == True].start_y, passes_filtered.loc[passes_filtered.accurate_pass == True].end_x, passes_filtered.loc[passes_filtered.accurate_pass == True].end_y, 
                 width = 2, 
                 headwidth = 10, 
                 headlength = 10, 
                 color = 'aquamarine', 
                 ax = axs['pitch'],
                 label = 'Completed')

    pitch.arrows(passes_filtered.loc[passes_filtered.accurate_pass == False].start_x, passes_filtered.loc[passes_filtered.accurate_pass == False].start_y, passes_filtered.loc[passes_filtered.accurate_pass == False].end_x, passes_filtered.loc[passes_filtered.accurate_pass == False].end_y, 
                 width = 2, 
                 headwidth = 6, 
                 headlength = 5, 
                 headaxislength = 12, 
                 color = 'tomato', 
                 ax = axs['pitch'],
                 label = 'Failed')
                
    if player == 'All':
        #plt.title(f'Juventus vs Sampdoria 20/09/2020: {team} pass map', color = 'white', size = 30)
        axs['title'].text(0.5, 0.5, f'Juventus vs Sampdoria 20/09/2020: \n {team} passes', color='#dee6ea',
                  va='center', ha='center', fontsize=25)
    else:
        #plt.title(f'Juventus vs Sampdoria 20/09/2020: {player} pass map', color = 'white', size = 30)
        axs['title'].text(0.5, 0.5, f'Juventus vs Sampdoria 20/09/2020: \n {player} passes', color='#dee6ea',
                  va='center', ha='center', fontsize=25)
    
    legend = axs['pitch'].legend(facecolor = '#01153E', handlelength = 5, edgecolor = 'None', loc = 'upper left', prop = {'size':25})
    frame = legend.get_frame()
    frame.set_facecolor('white')
    frame.set_edgecolor('white')
    
    axs['endnote'].text(1,0.25,'@datawithed',color='white',alpha=0.5,va='center',ha='right',fontsize=20,)
    
    st.pyplot(fig)


st.title('Pass map plots (by player/team)')
teams1 = tuple(xG_vs_mins.team.unique())
teams1_select = st.selectbox('Select a team', (teams1))

if teams1_select == 'Juventus':
    players1 = tuple(np.append('All', passes.loc[passes.team == 'Juventus']['player_name'].unique()))
    players1_select = st.selectbox('Select a player', (players1))
    passmap_plot(teams1_select, players1_select)
    st.markdown("""
                These pass maps can be used to highlight passing patterns on a individual or team basis.
                \nFurther developments upon this interactive passing page could be:
                \n- Segment the pitch into channels or dangerous sectors, collating pass data to these areas of the pitch to draw insights regarding dangerous passes
                \n- Create passing networks to understand passing patterns across the team between players
- This can demonstrate relationships between players on the pitch and where these can be improved to implement coaching tactics more effectively
                \n- Highlight progressive passes (based on varying defintions by data provider or "in-club" definition of progressive pass)
                
                """)

if teams1_select == 'Sampdoria':
    players2 = tuple(np.append('All', passes.loc[passes.team == 'Sampdoria']['player_name'].unique()))
    players2_select = st.selectbox('Select a player', (players2))
    passmap_plot(teams1_select, players2_select)

# -*- coding: utf-8 -*-
"""
Created on Sun Jul  3 08:42:55 2022

@author: Ed.Morris
"""

import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import numpy as np
import pandas as pd
import json
import os
from mplsoccer import Pitch, VerticalPitch


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

# Filter goal vs non-goal shots
goals = shot_data.loc[shot_data.is_goal == True]
non_goals = shot_data.loc[shot_data.is_goal == False]

xG_vs_mins = shot_data[['minute','second','team','xG']]
xG_vs_mins['actual_minute'] = xG_vs_mins.minute + 1
juve_xg = xG_vs_mins.loc[xG_vs_mins['team'] == 'Juventus'].reset_index(drop=True)
sampd_xg = xG_vs_mins.loc[xG_vs_mins['team'] == 'Sampdoria'].reset_index(drop=True)

xg_to_plot1 = [0]
j = 0
for min in range(1,91):
    if min == juve_xg['actual_minute'][j]:
        if j == len(juve_xg.actual_minute) - 1:
            xg_to_plot1.append(juve_xg['xG'][j] + xg_to_plot1[min-1])
        elif j < len(juve_xg) - 1:
            if juve_xg['actual_minute'][j] == juve_xg['actual_minute'][j+1]:
                xg_to_plot1.append(juve_xg['xG'][j] + juve_xg['xG'][j+1] + xg_to_plot1[min-1])
                j += 2
            else:
                xg_to_plot1.append(juve_xg['xG'][j] + xg_to_plot1[min-1])
                j += 1
    else:
        xg_to_plot1.append(xg_to_plot1[min-1])
        
print(xg_to_plot1)
print(len(xg_to_plot1))

# Create xG per minute for Sampdoria
xg_to_plot2 = [0]
j = 0
for min in range(1,91):
    if min == sampd_xg['actual_minute'][j]:
        if j == len(sampd_xg.actual_minute) - 1:
            xg_to_plot2.append(sampd_xg['xG'][j] + xg_to_plot2[min-1])
        elif j < len(sampd_xg) - 1:
            if sampd_xg['actual_minute'][j] == sampd_xg['actual_minute'][j+1]:
                xg_to_plot2.append(sampd_xg['xG'][j] + sampd_xg['xG'][j+1] + xg_to_plot2[min-1])
                j += 2
            else:
                xg_to_plot2.append(sampd_xg['xG'][j] + xg_to_plot2[min-1])
                j += 1
    else:
        xg_to_plot2.append(xg_to_plot2[min-1])

print(xg_to_plot2)
print(len(xg_to_plot2))

x = 0
for i in range(0,14):
    x += juve_xg.xG[i]

print(x) # 2.2507932

team1, team2 = shot_data.team.unique()


# Draw shotmap using mplsoccer library
def shotmap_plot(team,player):
    pitch = VerticalPitch(pad_bottom = 0.5,  # pitch extends slightly below halfway line
                      half = True,  # half of a pitch
                      goal_type = 'box',
                      goal_alpha = 0.8,
                      pitch_type = 'wyscout',
                      pitch_color = '#1E4966',
                      line_color = '#c7d5cc')  # control the goal transparency
    fig, ax = pitch.draw(figsize = (12,10))
    
    if team == team1:
        if player == 'All':
            non_goals_filtered = non_goals.loc[non_goals.team == team1]
            goals_filtered = goals.loc[goals.team == team1]
        if player != 'All':
            non_goals_filtered = non_goals.loc[(non_goals.team == team1) & (non_goals.player == player)]
            goals_filtered = goals.loc[(goals.team == team1) & (goals.player == player)]
            
    if team == team2:
        if player == 'All':
            non_goals_filtered = non_goals.loc[non_goals.team == team2]
            goals_filtered = goals.loc[goals.team == team2]
        if player != 'All':
            non_goals_filtered = non_goals.loc[(non_goals.team == team2) & (non_goals.player == player)]
            goals_filtered = goals.loc[(goals.team == team2) & (goals.player == player)]
    
    # Plot non-goal shots with hatches
    scat_1 = pitch.scatter(non_goals_filtered.start_x,non_goals_filtered.start_y,
                           # Size varies based on xG
                           s = (non_goals_filtered.xG * 1900) + 100,
                           edgecolors = '#b94b75', # Give markers a charcoal border
                           c = 'None', # No facecolours for the markers
                           hatch = '///', # hatched pattern for the markers
                           marker = 'o',
                           ax = ax)
    
    scat_2 = pitch.scatter(goals_filtered.start_x,goals_filtered.start_y,
                           # Size varies based on xG
                           s = (goals_filtered.xG * 1900) + 100,
                           edgecolors = '#b94b75',
                           linewidth = 0.6,
                           c = 'white',
                           marker = 'football',
                           ax = ax)
    
    ax.text(45.8, 82.6, '@datawithed', color = 'white', alpha = 0.5)
    
    if player == 'All':
        txt = ax.text(x = 50, y = 65, s = f'Juventus vs Sampdoria 20/09/2020:\n {team} shot map', fontname = 'Tahoma', size = 20, va = 'center', ha = 'center', color = 'white')
    if player != 'All':
        txt = ax.text(x = 50, y = 65, s = f'Juventus vs Sampdoria 20/09/2020:\n {player} shot map', fontname = 'Tahoma', size = 20, va = 'center', ha = 'center', color = 'white')
    
    st.pyplot(fig)

st.title('Shot map plots (by team/player)')
teams = tuple(xG_vs_mins.team.unique())
teams_select = st.selectbox('Select a team', (teams))

if teams_select == 'Juventus':
    players = tuple(np.append('All', shot_data.loc[shot_data.team == 'Juventus']['player'].unique()))
    players_select = st.selectbox('Select a player', (players))
    shotmap_plot(teams_select, players_select)
    st.markdown("""
                The graphic above shows that Juventus created xG opportunities from 15 different shots, scoring 3 goals (shown by the football shapes on the diagram).
                \n 
                """)
    col13, col14, col15 = st.columns(3)
    col13.metric(label = '% shots in box', value = f"{11/15:.0%}")
    col14.metric(label = 'Total xG created', value = f"{round(xg_to_plot1[90],2)}")
    col15.metric(label = 'Largest xG created (1 event)', value = f"{round(juve_xg.xG.max(),2)}")

if teams_select == 'Sampdoria':
    players = tuple(np.append('All', shot_data.loc[shot_data.team == 'Sampdoria']['player'].unique()))
    players_select = st.selectbox('Select a player', (players))
    shotmap_plot(teams_select, players_select)
    st.markdown("""
                The graphic above shows that Sampdoria created xG opportunities from 13 different shots, scoring 0 goals (shown by no football shapes on the diagram).
                """)
    col10, col11, col12 = st.columns(3)
    col10.metric(label = '% shots in box', value = f"{7/13:.0%}")
    col11.metric(label = 'Total xG created', value = f"{round(xg_to_plot2[90],2)}")
    col12.metric(label = 'Largest xG created (1 event)', value = f"{round(sampd_xg.xG.max(),2)}")

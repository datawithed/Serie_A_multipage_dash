# -*- coding: utf-8 -*-
"""
Created on Sun Jul  3 08:41:31 2022

@author: Ed.Morris
"""

# Page 2

import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import numpy as np
import pandas as pd
import json
import os

font1 = font_manager.FontProperties(family = 'Tahoma')
font = {'fontname':'Tahoma'}

@st.cache
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
    

# Create new df for xG and mins, create actual minute col (minute + 1) and filter for each team
xG_vs_mins = shot_data[['minute','second','team','xG']]
xG_vs_mins['actual_minute'] = xG_vs_mins.minute + 1
juve_xg = xG_vs_mins.loc[xG_vs_mins['team'] == 'Juventus'].reset_index(drop=True)
sampd_xg = xG_vs_mins.loc[xG_vs_mins['team'] == 'Sampdoria'].reset_index(drop=True)
print(juve_xg)

# Create xG per minute for Juventus
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

# xG chart
def xg_chart():
    fig, ax = plt.subplots(1,1)
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    plt.plot(np.linspace(0,90,num=91),xg_to_plot1,label = 'Juventus xG', color = 'white')
    plt.plot(np.linspace(0,90,num=91),xg_to_plot2,label = 'Sampdoria xG', color = 'purple')
    ax = plt.gca()
    ax.set_facecolor('#1E4966')
    ax.spines['left'].set_color('white') 
    ax.spines['bottom'].set_color('white') 
    ax.spines['right'].set_color('white')
    ax.spines['top'].set_color('#1E4966')
    ax.tick_params(axis='x', colors='white')    #setting up X-axis tick color to red
    ax.tick_params(axis='y', colors='white', labelright = True)
    ax.text(40,2.5,'@datawithed', color = 'white', alpha = 0.5, size = 8)
    fig.patch.set_facecolor('#1E4966')
    plt.xticks(np.arange(0,90+1,5))
    plt.xlabel('Minute', color = 'white',**font)
    plt.ylabel('xG', color = 'white',**font)
    plt.title(f'Juventus [{round(juve_xg.xG.sum(),2)}] vs [{round(sampd_xg.xG.sum(),2)}] Sampdoria:\nxG generated over match', color = 'white',**font)
    plt.legend(prop = font1)
    plt.rcParams['figure.dpi'] = 800
    st.pyplot(fig)

st.set_page_config(page_title = 'xG Flow Chart', page_icon = Image.open('Serie_A_logo.jpg'))

st.title('xG Flow Chart')
xg_chart()
st.caption('xG flow chart showing xG generated across the course of the match. Commentary below.')
st.markdown("""
            - This xG flow chart shows how the shooting opportunities created by each team varied over the course of the match.
            \n- Juventus were the team on the offensive for the majority of the match, due to the continuously bumpy xG line showing they created shooting opportunities (even if only small) fairly frequently.
            \n- Also clear to see Sampdoria were the defensive/counter-attacking team for large periods of the match due to long periods of a stagnant xG line. 
- This shows that they were only creating shooting opportunities fairly infrequently, for example having 0 xG generated for the first 25 minutes of the match.
            \n- Can possibly infer from this chart a question over the fitness/concentration of the Sampdoria defence towards the end of the match. 
- Between the 75th and 80th minutes of the match, Juventus were able to generate over 1 xG in this 5 minute period, which could be due to a lack of fitness or concentration in the later stages of the match. 
- Alternatively, this could demonstrate the superior fitness of the Juventus attackers, or positive substitutions made to attack a tiring Sampdoria defence.
            \n- It is important to note however that a sample size of one match is not adequate to draw such large conclusions, we would need to see this pattern occurring over 10s of matches to be able to conclude any hard insights from this type of graphic.
            """)

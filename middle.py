from django.shortcuts import render
import requests
import json
import plotly.express as px
import pandas as pd
from plotly.offline import plot

def get_team_data(team_url):
    team_response = requests.get(team_url)
    return team_response.json()

def get_team_statistics_data(team_statistics_url):
    team_statistic_response = requests.get(team_statistics_url)
    return team_statistic_response.json()

def index(request):
    response = requests.get('https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams?limit=32')
    response_dict = response.json()

    conferences = {
        'AFC': {
            'North': [],
            'South': [],
            'East': [],
            'West': []
        },
        'NFC': {
            'North': [],
            'South': [],
            'East': [],
            'West': []
        }
    }

    for team in response_dict.get('items', []):
        team_url = team.get('$ref')
        if team_url:
            team_data = get_team_data(team_url)
            team_name = team_data.get('displayName')
            logo_url = team_data.get('logos', [{}])[0].get('href')
            team_id = team_data.get('id')
            conference_parts = team_data.get('group', {}).get('name')
            conference = conference_parts.split(' ')[0]
            division = conference_parts.split(' ')[1]

            if conference in conferences and division in conferences[conference]:
                conferences[conference][division].append({'name': team_name, 'logo': logo_url, 'id': team_id})

    return render(request, 'nfl_app/index.html', context={'conferences': conferences})

def team_detail(request, team_id):
    team_url = f'https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams/{team_id}'
    team_data = get_team_data(team_url)
    team_color = team_data.get('color')
    team_name = team_data.get('displayName')
    logo_url = team_data.get('logos', [{}])[0].get('href')
    team_statistics = team_data.get('statistics', {})
    team_statistics_url = team_statistics.get('$ref')
    team_statistics_data = get_team_statistics_data(team_statistics_url)
    splits_data = team_statistics_data.get('splits', [])
    score_type = []
    score_values = []

    categories_data = team_statistics_data.get('splits', []).get('categories', [])
    scoring_data = [category for category in categories_data if 'scoring' in category.get('displayName', '').lower()]
    for category in scoring_data:
        for stat in category.get('stats', []):
            score_type.append(stat.get('displayName'))
            if stat.get('displayName') == 'Field Goals':
                fg_points = stat.get('value') * 3
                score_values.append(fg_points)
            elif (stat.get('displayName') == 'Return Touchdowns' or stat.get('displayName') == 'Passing Touchdowns' or stat.get('displayName') == 'Rushing Touchdowns' or stat.get('displayName') == 'Receiving Touchdowns'):
                td_points = stat.get('value') * 6
                score_values.append(td_points)
            elif (stat.get('displayName') == 'Two Point Pass Conversions' or stat.get('displayName') == 'Two Point Rush Conversion' or stat.get('displayName') == 'Two Point Receiving Conversion'):
                two_point_conv_points = stat.get('value') * 2
                score_values.append(two_point_conv_points)
            else:
                score_values.append(stat.get('value'))

    team_graph_data = pd.DataFrame({
        'Score Type': score_type,
        'Points': score_values
    })

    fig = px.bar(team_graph_data, x='Score Type', y='Points')
    fig.update_traces(marker_color=f'#{team_color}', marker_line_color='rgba(255, 255, 255, 0.5)', marker_line_width=1)
    fig.update_layout(
        plot_bgcolor='rgba(30, 30, 30, 0.8)',  # Dark gray background for the graph
        paper_bgcolor='rgba(30, 30, 30, 0.8)',  # Dark gray background for the paper
        font=dict(color='white'),  # White font color for better contrast
        xaxis=dict(showgrid=False),  # Hide x-axis grid lines
        yaxis=dict(showgrid=False),  # Hide y-axis grid lines
        bargap=0.2,  # Gap between bars
        bargroupgap=0.1,  # Gap between bar groups
    )

    plot_div = plot(fig, output_type='div')

    return render(request, 'nfl_app/team_detail.html', context={'plot': plot_div, 'logo': logo_url, 'team_name': team_name})
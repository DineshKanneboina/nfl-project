from django.shortcuts import render
from django.core.cache import cache
import requests
import json
import plotly.express as px
import pandas as pd
from plotly.offline import plot
from django.http import JsonResponse

def fetch_athletes(request, team_id):
    team_url = f'https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams/{team_id}'
    team_data = get_team_data(team_url)
    athletes_list = []
    if 'athletes' in team_data:
        athletes_url = team_data['athletes'].get('$ref')
        if athletes_url:
            athletes_list = process_athletes_data(athletes_url)
    return JsonResponse({'athletes': athletes_list})

def fetch_depth_chart(request, team_id):
    team_url = f'https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams/{team_id}'
    team_data = get_team_data(team_url)
    depth_chart_list = []
    if 'depthCharts' in team_data:
        depth_chart_url = team_data['depthCharts'].get('$ref')
        if depth_chart_url:
            depth_chart_data = get_depth_chart_data(depth_chart_url)
            depth_chart_list = process_depth_chart_data(depth_chart_data)
    return JsonResponse({'depth_chart': depth_chart_list})

def get_team_data(team_url):
    cached_data = cache.get(team_url)
    if cached_data:
        return cached_data
    team_response = requests.get(team_url)
    team_data = team_response.json()
    cache.set(team_url, team_data, timeout=60*60)  # Cache for 1 hour
    return team_data

def get_group_data(group_url):
    cached_data = cache.get(group_url)
    if cached_data:
        return cached_data
    group_response = requests.get(group_url)
    group_data = group_response.json()
    cache.set(group_url, group_data, timeout=60*60)  # Cache for 1 hour
    return group_data

def get_team_statistics_data(team_statistics_url):
    cached_data = cache.get(team_statistics_url)
    if cached_data:
        return cached_data
    team_statistic_response = requests.get(team_statistics_url)
    team_statistics_data = team_statistic_response.json()
    cache.set(team_statistics_url, team_statistics_data, timeout=60*60)  # Cache for 1 hour
    return team_statistics_data

def get_venue_data(venue_url):
    cached_data = cache.get(venue_url)
    if cached_data:
        return cached_data
    venue_response = requests.get(venue_url)
    venue_data = venue_response.json()
    cache.set(venue_url, venue_data, timeout=60*60)  # Cache for 1 hour
    return venue_data

def get_athletes_data(athletes_url):
    cached_data = cache.get(athletes_url)
    if cached_data:
        return cached_data
    athletes_response = requests.get(athletes_url)
    athletes_data = athletes_response.json()
    cache.set(athletes_url, athletes_data, timeout=60*60)  # Cache for 1 hour
    return athletes_data

def get_player_data(player_url):
    cached_data = cache.get(player_url)
    if cached_data:
        return cached_data
    player_response = requests.get(player_url)
    player_data = player_response.json()
    cache.set(player_url, player_data, timeout=60*60)  # Cache for 1 hour
    return player_data

def get_position_data(position_url):
    cached_data = cache.get(position_url)
    if cached_data:
        return cached_data
    position_response = requests.get(position_url)
    position_data = position_response.json()
    cache.set(position_url, position_data, timeout=60*60)  # Cache for 1 hour
    return position_data

def get_depth_chart_data(depth_chart_url):
    cached_data = cache.get(depth_chart_url)
    if cached_data:
        return cached_data
    depth_chart_response = requests.get(depth_chart_url)
    depth_chart_data = depth_chart_response.json()
    cache.set(depth_chart_url, depth_chart_data, timeout=60*60)  # Cache for 1 hour
    return depth_chart_data

def process_team_data(team_data):
    group_url = team_data.get('groups', {}).get('$ref')
    group_data = get_group_data(group_url)
    venue_url = team_data['venue'].get('$ref')
    venue_data = get_venue_data(venue_url)
    cap_name = team_data.get('displayName', '').upper()
    team_info = {
        'abbreviation': team_data.get('abbreviation'),
        'location': team_data.get('location'),
        'nickname': team_data.get('nickname'),
        'color': team_data.get('color'),
        'id': team_data.get('id'),
        'slug': group_data.get('slug'),
        'division': group_data.get('name'),
        'venue': venue_data.get('fullName')
    }
    return team_info

def process_athletes_data(athletes_url):
    page_counter = 1
    current_page_url = f"{athletes_url}&page={page_counter}"
    athletes_data = get_athletes_data(current_page_url)
    total_athletes = athletes_data.get('count', 0)
    processed_athletes = 0
    athletes_list = []

    while processed_athletes < total_athletes:
        athletes_data = get_athletes_data(current_page_url)
        for athlete in athletes_data.get('items', []):
            player_url = athlete.get('$ref')
            if player_url:
                player_data = get_player_data(player_url)
                position_url = player_data['position'].get('$ref')
                if position_url:
                    position_data = get_position_data(position_url)
                athletes_list.append({
                    'name': player_data.get('fullName'),
                    'position': position_data.get('displayName'),
                    'jersey': player_data.get('jersey')
                })
            processed_athletes += 1

        # Check if there are more pages
        if (processed_athletes % 25 == 0):
            page_counter += 1
            current_page_url = f"{athletes_url}&page={page_counter}"
        else:
            break

    return athletes_list

def process_depth_chart_data(depth_chart_data):
    depth_chart_list = []
    for item in depth_chart_data.get('items', []):
        positions = []
        for position_key, position_value in item.get('positions', {}).items():
            athletes = []
            if position_key == "wr":
                # Sort athletes by rank
                sorted_athletes = sorted(position_value.get('athletes', []), key=lambda x: x.get('rank'))
                for athlete in sorted_athletes:
                    athlete_url = athlete.get('athlete', {}).get('$ref')
                    rank = athlete.get('rank')
                    if athlete_url:
                        player_data = get_player_data(athlete_url)
                        athletes.append({
                            'name': player_data.get('fullName'),
                            'rank': rank
                        })
            else:
                for athlete in position_value.get('athletes', []):
                    athlete_url = athlete.get('athlete', {}).get('$ref')
                    rank = athlete.get('rank')
                    if athlete_url:
                        player_data = get_player_data(athlete_url)
                        athletes.append({
                            'name': player_data.get('fullName'),
                            'rank': rank
                        })
            positions.append({
                'position_key': position_key,
                'position_name': position_value.get('position', {}).get('displayName'),
                'athletes': athletes
            })
        depth_chart_list.append({
            'id': item.get('id'),
            'name': item.get('name'),
            'positions': positions
        })
    return depth_chart_list

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
            group_url = team_data.get('groups', {}).get('$ref')
            group_data = get_group_data(group_url)
            conference_parts = group_data.get('name')
            conference = conference_parts.split(' ')[0]
            division = conference_parts.split(' ')[1]

            if conference in conferences and division in conferences[conference]:
                conferences[conference][division].append({'name': team_name, 'logo': logo_url, 'id': team_id})

    return render(request, 'nfl_app/index.html', context={'conferences': conferences})

def team_detail(request, team_id):
    team_url = f'https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams/{team_id}'
    team_data = get_team_data(team_url)
    team_info = process_team_data(team_data)
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

    athletes_list = []
    if 'athletes' in team_data:
        athletes_url = team_data['athletes'].get('$ref')
        if athletes_url:
            athletes_list = process_athletes_data(athletes_url)

    depth_chart_list = []
    if 'depthCharts' in team_data:
        depth_chart_url = team_data['depthCharts'].get('$ref')
        if depth_chart_url:
            depth_chart_data = get_depth_chart_data(depth_chart_url)
            depth_chart_list = process_depth_chart_data(depth_chart_data)

    return render(request, 'nfl_app/team_detail.html', context={
        'plot': plot_div, 
        'logo': logo_url, 
        'team_name': team_name, 
        'team_info': team_info, 
        'athletes': athletes_list, 
        'depth_chart': depth_chart_list, 
        'team_id': team_id
    })
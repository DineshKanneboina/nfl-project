# import requests module 
import requests
import json
import plotly.express as px
import pandas as pd

# Function to print a line of dashes
def print_dashes():
    print('-' * 80)  # Adjust the number of dashes as needed

# Function to get team data
def get_team_data(team_url):
    team_response = requests.get(team_url)
    return team_response.json()

def get_team_statistics_data(team_statistics_url):
    team_statistic_response = requests.get(team_statistics_url)
    return team_statistic_response.json()

# Function to get venue data
def get_venue_data(venue_url):
    venue_response = requests.get(venue_url)
    return venue_response.json()

# Function to get athletes data
def get_athletes_data(athletes_url):
    athletes_response = requests.get(athletes_url)
    return athletes_response.json()

# Function to get player data
def get_player_data(player_url):
    player_response = requests.get(player_url)
    return player_response.json()

# Function to get position data
def get_position_data(position_url):
    position_response = requests.get(position_url)
    return position_response.json()

# Function to get depth chart data
def get_depth_chart_data(depth_chart_url):
    depth_chart_response = requests.get(depth_chart_url)
    return depth_chart_response.json()

def get_group_data(group_url):
    group_response = requests.get(group_url)
    return group_response.json()

def get_scoring_data(scoring_url):
    scoring_response = requests.get(scoring_url)
    return scoring_response.json()

# Function to process team data
def process_team_data(team_data):
    group_url = team_data.get('groups', {}).get('$ref')
    group_data = get_group_data(group_url)
    cap_name = team_data.get('displayName', '').upper()
    print('-' * 30 + cap_name + '-' * 30)
    print("Team Abbreviation:".ljust(20), team_data.get('abbreviation'))
    print("Team Location:".ljust(20), team_data.get('location'))
    print("Team Nickname:".ljust(20), team_data.get('nickname'))
    print("Team Color:".ljust(20), team_data.get('color'))
    print("Team ID:".ljust(20), team_data.get('id'))
    print("Team Slug:".ljust(20), group_data.get('slug'))
    print("Team Division:".ljust(20), group_data.get('name'))


    venue_url = team_data['venue'].get('$ref')
    venue_data = get_venue_data(venue_url)
    print("Team Venue:".ljust(20), venue_data.get('fullName'), "\n")

    if 'athletes' in team_data:
        athletes_url = team_data['athletes'].get('$ref')
        if athletes_url:
            athletes_data = get_athletes_data(athletes_url)
            process_athletes_data(athletes_url)
    else:
        print("Athletes key does not exist")

    if 'depthCharts' in team_data:
        depth_chart_url = team_data['depthCharts'].get('$ref')
        if depth_chart_url:
            depth_chart_data = get_depth_chart_data(depth_chart_url)
            process_depth_chart_data(depth_chart_data)

# Function to process depth chart data
def process_depth_chart_data(depth_chart_data):
    print('-' * 20 + "DEPTH CHART DATA" + '-' * 20)
    for item in depth_chart_data.get('items', []):
        print("\nDepth Chart Id:".ljust(20), item.get('id'))
        print("Depth Chart Name:".ljust(20), item.get('name'))
        for position_key, position_value in item.get('positions', {}).items():
            print("\nPosition Key:", position_key)
            position_name = position_value.get('position', {}).get('displayName')
            print("Position Display Name:".ljust(20), position_name)

            if position_key == "wr":
                # Sort athletes by rank
                sorted_athletes = sorted(position_value.get('athletes', []), key=lambda x: x.get('rank'))
                for athlete in sorted_athletes:
                    athlete_url = athlete.get('athlete', {}).get('$ref')
                    rank = athlete.get('rank')
                    if athlete_url:
                        player_data = get_player_data(athlete_url)
                        print(f"Name: {player_data.get('fullName')}".ljust(40), f"Rank: {rank}")
            else:
                for athlete in position_value.get('athletes', []):
                    athlete_url = athlete.get('athlete', {}).get('$ref')
                    rank = athlete.get('rank')
                    if athlete_url:
                        player_data = get_player_data(athlete_url)
                        print(f"Name: {player_data.get('fullName')}".ljust(40), f"Rank: {rank}")

# Function to process athletes data
def process_athletes_data(athletes_url):
    page_counter = 1
    current_page_url = f"{athletes_url}&page={page_counter}"
    athletes_data = get_athletes_data(current_page_url)
    total_athletes = athletes_data.get('count', 0)
    processed_athletes = 0

    while processed_athletes < total_athletes:
        athletes_data = get_athletes_data(current_page_url)
        for athlete in athletes_data.get('items', []):
            print("Athlete #"+str(processed_athletes)+" data:")
            player_url = athlete.get('$ref')
            if player_url:
                player_data = get_player_data(player_url)

                position_url = player_data['position'].get('$ref')
                if position_url:
                    position_data = get_position_data(position_url)

                print("Name:".ljust(20), player_data.get('fullName'))
                print("Position:".ljust(20), position_data.get('displayName'))
                print("Jersey Number:".ljust(20), player_data.get('jersey'), "\n")

            processed_athletes += 1

        # Check if there are more pages
        if (processed_athletes % 25 == 0):
            page_counter += 1
            current_page_url = f"{athletes_url}&page={page_counter}"
            athletes_data = get_athletes_data(current_page_url)
        else:
            break

def process_statistics_data(team_statistics_data):
    print_dashes()
    splits_data = team_statistics_data.get('splits', [])
    categories_data = splits_data.get('categories', [])
    print('-' * 20 + "SPLIT DATA" + '-' * 20)
    for split in categories_data:
        if isinstance(split, dict):
            print("\nSplit Type:".ljust(20), split.get('displayName'))
            stat_data = split.get('stats', [])
            #print(stat_data.get('displayName')+": "+str(stat_data.get('value')))
            for stat in stat_data:
                print(f"{stat.get('displayName')}: ".ljust(35) + str(stat.get('value')))
            

        else:
            print("Unexpected split format:", split)




# Main function to get and process teams data
def main():
    # Making a get request 
    response = requests.get('https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams?limit=32') 

    # Convert json into dictionary 
    response_dict = response.json() 

    # Loop through each team and get data from the URL endpoint
    team_count = 0
    for team in response_dict.get('items', []):
        if team_count >= 3:
            break
        team_url = team.get('$ref')
        if team_url:
            #team general data
            team_data = get_team_data(team_url)
            process_team_data(team_data)
            #team statistics data
            logo_url = team_data.get('logos', [{}])[0].get('href')
            team_statistics = team_data.get('statistics', {})
            team_statistics_url = team_statistics.get('$ref')
            team_statistics_data = get_team_statistics_data(team_statistics_url)
            #process_statistics_data(team_statistics_data)
            x = 0
            #getting data into lists
            score_type = []
            score_values = []
            #gets category data from team stats (splits url to categories)
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
                    print(stat.get('displayName') + ": " + str(stat.get('value')))

            team_count += 1
            #plotting data

            team_graph_data = pd.DataFrame({
                'Score Type': score_type,
                'Points': score_values
            })

            fig = px.bar(team_graph_data, x='Score Type', y='Points')
            fig.update_layout(
                title=dict(text=team_data.get('displayName'), font=dict(size=50), automargin=True, yref='paper')
            )
            fig.show()

if __name__ == "__main__":
    main()
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
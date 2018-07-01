from flask import Flask, render_template
import requests
import json


def isnumeric(num):
    try:
        float(num)
        return True
    except:
        return False


def check_time(time_str):
    if len(time_str) <= 2:
        return True

    if isnumeric(time_str[2]):
        return False

    if float(time_str[:2]) <= 90:
        return True
    else:
        return False


def get_standings():
    res = requests.get('http://worldcup.sfg.io/matches')
    matches = filter(lambda x: x['stage_name'] == 'Round of 16' and x['status'] in ['in progress', 'completed'], res.json())
    matches = map(lambda x: [x['home_team_events'], x['away_team_events'], x['home_team_country'] + ' vs ' + x['away_team_country']], matches)

    out_list = []
    for team_event in matches:
        score = [0, 0]
        for xevent in team_event[0]:
            if check_time(xevent['time']):
                if 'goal-own' == xevent['type_of_event']:
                    score[1] += 1
                elif 'goal' in xevent['type_of_event']:
                    score[0] += 1

        for xevent in team_event[1]:
            if check_time(xevent['time']):
                if 'goal-own' == xevent['type_of_event']:
                    score[0] += 1
                elif 'goal' in xevent['type_of_event']:
                    score[1] += 1

        if score[0] == score[1]:
            str_score = 'X'
        elif score[0] > score[1]:
            str_score = '1'
        elif score[0] > score[1]:
            str_score = '0'

        out_list.append({'name': team_event[2], 'result': str_score})

    return out_list

#print get_standings()
app = Flask(__name__)

@app.route('/')
def present_scores():
    #stand_dict = get_standings()

    with open('./data/playoffs_data.json', 'r') as infile:
        bet_dict = json.load(infile)

    match_name = filter(lambda x: x != 'name', bet_dict[0].keys())
    return render_template('wc_rank.html', result=bet_dict, match_name=match_name)

@app.route('/end_point')
def endp():
    return requests.get('http://worldcup.sfg.io/matches').text

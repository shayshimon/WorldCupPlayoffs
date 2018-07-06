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


def check_extra_time(xtime):
    if len(xtime) < 3:
        return False
    elif isnumeric(xtime[2]):
        return True
    else:
        return int(xtime[:2]) > 90


def get_standings(round_name='Round of 16'):
    res = requests.get('http://worldcup.sfg.io/matches')
    matches = filter(lambda x: x['stage_name'] == round_name and x['status'] in ['in progress', 'completed'], res.json())
    matches = map(lambda x: [x['home_team_events'], x['away_team_events'], x['home_team_country'] + ' vs ' + x['away_team_country'], x['home_team']['goals'], x['away_team']['goals']], matches)

    out_list = {}
    for team_event in matches:
        if team_event[3] == team_event[4] or any(check_extra_time(ev['time']) for ev in team_event[0] + team_event[1]):
            str_score = 'X'
        elif team_event[3] > team_event[4]:
            str_score = '1'
        elif team_event[3] > team_event[4]:
            str_score = '0'

        out_list.update({team_event[2]: str_score})

    return out_list

#print get_standings()
app = Flask(__name__)

@app.route('/')
def present_scores():
    def score2name(score, name_list):
        if score == 'X':
            return 'Tie'
        else:
            return name_list[int(score) - 1]

    def get_ranks(bet_file_name, round_name):
        stand_dict = get_standings(round_name = round_name)

        with open(bet_file_name, 'r') as infile:
            bet_dict = json.load(infile)

        match_name = filter(lambda x: x != 'name', bet_dict[0].keys())
        for item in bet_dict:
            tmp_rank = 0
            for mname in match_name:
                if mname in stand_dict and stand_dict[mname] == str(item[mname]):
                    tmp_rank += 1

                item[mname] = score2name(item[mname], mname.split(' vs '))

            item['rank'] = tmp_rank

        return sorted(bet_dict, key=lambda x: x['rank'], reverse=True), match_name

    sorted_bet_dict, match_name = get_ranks('./data/playoffs_data.json', 'Round of 16')
    sorted_bet_dict2, match_name2 = get_ranks('./data/playoffs_data2.json', 'Quarter-finals')

    for item in sorted_bet_dict2:
        prev_item = filter(lambda x: x['name'] == item['name'], sorted_bet_dict)
        if prev_item:
            item['rank'] = prev_item[0]['rank'] + item['rank'] * 2

    sorted_bet_dict2 = sorted(sorted_bet_dict2, key=lambda x: x['rank'], reverse=True)

    return render_template('wc_rank.html', result=sorted_bet_dict, match_name=match_name, result2=sorted_bet_dict2, match_name2=match_name2)

@app.route('/end_point')
def endp():
    return requests.get('http://worldcup.sfg.io/matches').text

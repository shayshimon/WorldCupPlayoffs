from flask import Flask, render_template
from itertools import groupby
import requests
import json


def get_standings():
    res = requests.get("http://worldcup.sfg.io/teams/results")
    sorted_res = sorted(res.json(), key=lambda x: (x['group_letter'], x['points'], x['goal_differential'], x['country']), reverse=True)
    stand_groups = groupby(sorted_res, key=lambda x: x['group_letter'])
    house_dict = {}
    for i, g in stand_groups:
        house_dict[i] = sorted(list(g), key=lambda x: (x['points'], x['goal_differential'], x['country']), reverse=True)

    return house_dict

app = Flask(__name__)

@app.route("/")
def present_scores():
    stand_dict = get_standings()

    with open('./data/bet_poll.json', 'r') as infile:
        bet_dict = json.load(infile)

    for item in bet_dict:
        item_rank = 0
        for house in stand_dict:
            house_rank = 0
            if stand_dict[house][0]['country'] == item[house][0]:
                house_rank += 3
            elif item[house][0] == stand_dict[house][1]['country']:
                house_rank += 2

            if stand_dict[house][1]['country'] == item[house][1]:
                house_rank += 3
            elif item[house][1] == stand_dict[house][0]['country']:
                house_rank += 2

            item_rank += house_rank

        item['rank'] = item_rank

    sorted_bet_dict = sorted(bet_dict, key=lambda x: x['rank'], reverse=True)
    abc_list = [chr(i) for i in range(ord('A'), ord('I'))]
    return render_template("wc_rank.html", result=sorted_bet_dict, abc_list=abc_list, stand_dict=stand_dict)

@app.route("/end_point")
def endp():
    return requests.get("http://worldcup.sfg.io/teams/results").text

import pandas as pd
import json


df = pd.read_csv('./data/playoffs_data.csv')
cols = filter(lambda x: '[' in x, df.columns)
cols = map(lambda x: x[x.find('[') + 1:x.find(']')], cols)

out_list = []
for i, row in df.iterrows():
    tmp_dict = {i[0]: i[1] for i in zip(cols, row[2:])}
    tmp_dict['name'] = row[1]
    out_list.append(tmp_dict)

with open('./data/playoffs_data.json', 'w') as outfile:
    json.dump(out_list, outfile)

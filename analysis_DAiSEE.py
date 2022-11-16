import pandas as pd
import os

label_path = 'C:\\Users\\dlsxo\\OneDrive - GIST\\scilab\\과제\\220225_미프과제\\meeting\\dataset\\DAiSEE\\DAiSEE\\'
label_file = label_path + 'Labels\\AllLabels.csv'

dataset_path = os.path.join(label_path, 'DataSet')
dir_list = os.listdir(dataset_path)
id_list = []

for category_dir in dir_list:
    if 'txt' in category_dir:
        continue

    cat_dir_list = os.listdir(os.path.join(dataset_path, category_dir))
    cat_dir_list.sort()

    for id_dir in cat_dir_list:
        # print(id_dir)
        id_list.append(id_dir)

id_list.sort()
df = pd.read_csv(label_file)

def splitId(row):
    id = row[:6]

    return id

df['id'] = df['ClipID']
df.id = df.id.apply(splitId)
grouped = df['Engagement'].groupby(df['id'])


index = df.index.to_list()

df['index'] = index


print(df)
print('****************************')
print(grouped.mean())


# grouped.plot(x = 'index',
#              y = 'mean',
#              figsize = (10, 5))



# df.groupby('ClipID')
# print(df)


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec



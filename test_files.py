""" Testing file sorting and handling """

import csv
import os
import time

path = '/mnt/stuff/Joseph/Production/Labels'
posts = {}

def GetCSVData(filename):
    this_label = []
    try:
        f = open(filename, newline='')
    except:
        print('Unable to open ', filename)
    with f:
        this_file = csv.reader(f, delimiter=',', quoting=csv.QUOTE_NONE)
        for row in this_file:
            this_label.append(row)
    this_post = this_label[13]
    this_post = [i.replace("'","") for i in this_post]
    return this_post

for filename in os.listdir(path):
    #print(filename)
    if os.path.isfile(os.path.join(path,filename)):
        timestamp = filename.split('_')[-1].split('.')[0]
        posts[timestamp] = GetCSVData(os.path.join(path,filename))

for i in sorted(posts):
    print(i)
    print('Order Number: ', posts[i][0])
    print('Post Number: ', posts[i][4])


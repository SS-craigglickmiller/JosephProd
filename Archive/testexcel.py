import csv

spammy = [['a','b','c'],['1','2','3']]
with open('eggs.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
            quotechar="'",quoting=csv.QUOTE_MINIMAL
            )
    spamwriter.writerows(spammy)

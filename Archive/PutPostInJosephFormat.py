""" Take information from OfficeDot and put into Joseph format. """

def PrepOrdersForProduction(orders):
    today_Joseph_posts = []
    for post in range(1,len(orders)):
        this_post = StripQuotes(orders[post])
        row = ['DEFAULT', 'DEFAULT','2x2', 'DEFAULT', 'DEFAULT']
        print('Processing: ', str(this_post[ORD[Order_Number]]), 
                '-', str(this_post[ORD['PieceNumber']])
        row.append(this_post[16])
        if this_post[17]:
            for i in range(this_post[18]):
                
            return today_Joseph_posts

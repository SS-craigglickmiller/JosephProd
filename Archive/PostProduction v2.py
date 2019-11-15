""" Script to create Joseph ops from post production list in Office Dot.

Inputs = Query OfficeDot for production schedule
Process = Match post to spec, includes Joseph instruction set
Outputs = CSV file to send to Joseph

THIS SCRIPT RUNS ON DAY OF PRODUCTION! 
"""

import xlrd
import datetime
import csv
import math
import logging

##### LOGGING #####
#logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger(__name__)
#file = str(datetime.date.today()) + '-log.log'
#handler = logging.FileHandler(file)
#handler.setLevel(logging.INFO)
#logger.addHandler(handler)

##### CONSTANTS #####

ANGLE_KERF = 0.140 # cutoff blade
CUT_OFFSET = 1.112 # cutoff setop offset

ORD = {
        'OrderNumber':0,
        'MetalProduction':1,
        'DueDate':2,
        'OrderItemBaseName':3,
        'PieceNumber':4,
        'BarcodeValue':5,
        'InfillType':6,
        'PostConfiguration':7,
        'MountingStyle':8,
        'TopStyle2Name':9,
        'FootStyle':10,
        'QuantityOrdered':11,
        'PostAngle':12,
        'CutLength':13,
        'FinishOptionTitle':14,
        'PartNumber':15,
        }
SPEC = {
        'PN':0,
        'Post Name':1,
        'Routing Instructions':2,
        'Cut Length':3,
        'First Hole':4,
        'Steps':5,
        'Pattern':6,
        'Top Type':7,
        'Joseph Instructions':8,
        }
JOSEPH_COLUMNS = {
        'Model':0,
        'PART':1,
        'MATERIAL':2,
        'ID NUMBER':3,
        'BIN NUMBER':4,
        'CUT LENGTH':5,
        'CRC':6,
        'ADDITIONAL STEPS':7,
        'STEPS':8,
        'EXTRA':9,
        }
# NOTE: This angled foot part number is used for regular foot and narrow
#       Even though they technically have different part numbers.
ANGLED_PARTNO = {
        'B Up':182534,
        'B Down':182642,
        'B-5':150194,
        }

##### PRIMARY FUNCTIONS ####

def GetOrders():
    # Reading in from a prepped file.
    #logger.info('Fetching orders for today...')
    print('Fetching orders for today...')
    today_orders = []
    order_book = xlrd.open_workbook('orders.xlsx')
    order_sheet = order_book.sheet_by_index(0)
    for r in range(order_sheet.nrows):
        today_orders.append(order_sheet.row_values(r))
    return today_orders

def PrepOrdersForProduction(orders):
    """ ------ """
    # Open the spec sheet
    spec_book = xlrd.open_workbook('JosephInstructions.xlsx')
    spec_sheet = spec_book.sheet_by_index(0)
    spec_partno = spec_sheet.col_values(0) #part number index list
    today_Joseph_posts = []
    for post in range(1,len(orders)):
        # loop over posts for the day.
        this_post = StripQuotes(orders[post])
        #logger.info('Processing: ', this_post[ORD['OrderNumber']],
        #        '-', this_post[ORD['PieceNumber']])
        print('Prcoessing: ', str(this_post[ORD['OrderNumber']]),
                '-', str(this_post[ORD['PieceNumber']]))
        if this_post[ORD['PartNumber']] > 300000:
            this_post = UpdatePost(this_post)
        try:
            # match this_post partnumber to a spec row number
            r = 0
            while this_post[ORD['PartNumber']] != spec_partno[r]:
                r += 1
            spec_row = r
        except:
            #TORDO create an alert if spec doesn't match! Write to file.
            #logger.info('The part number is not in the spec list!')
            print('The part number is not in the spec list!')
            continue
        # add this post to the production list.
        this_spec = spec_sheet.row_values(r)
        today_Joseph_posts.append(PutPostInJosephFormat(this_post, 
                                                        this_spec))
    #logger.info(len(orders), ' processed...\n')
    print(len(orders), ' posts processed... \n')
    return today_Joseph_posts
    
def ProductionToCSV(prod_list):
    filename = str(datetime.date.today()) + '-cutlist.csv'
    #logger.info('Writing orders to ', filename)
    print('Writing orders to ', filename)
    with open(filename, 'w', newline='\n') as f:
        cutlist = csv.writer(f, delimiter=',', 
                    quotechar='"', quoting=csv.QUOTE_NONNUMERIC
                    )
        cutlist.writerow(list(JOSEPH_COLUMNS)) #Header
        cutlist.writerows(prod_list)
        cutlist.writerow([]) # this writes an empty row at the end.
    return '\nSUCCESS!'
     
##### ADDITIONAL FUNCTIONS #####
     
def UpdatePost(post):
    """ Update part number and dimensions for ramp/angle """
    #logger.info('Custom order - matching to actual part number...')
    print('Custom order - matching to actual part number...')
    item = post[ORD['OrderItemBaseName']].lower()
    if ('angled' in item) or ('ramp' in item):
        matching = ANGLED_PARTNO[post[ORD['PostConfiguration']]]
        post[ORD['PartNumber']] = matching
        #logger.info('Match found.')
        print('Match found')
    else:
        #TODO get cut length, mill on huerco.
        #logger.info('Not an angled post. Need special instructions!')
        print('Not an angled post. Need special instructions!')
    return post
    
def PutPostInJosephFormat(post, spec):
    """ Put a post into the Joseph format. """
    post_row = ['DEFAULT','DEFAULT','2X2','DEFAULT','DEFAULT']
    post_row.append(GetCutLength(post,spec)) # Cut length
    post_row.append(1) # number of posts, always 1
    post_row.append(GetAdditionalSteps(spec)) # Count of steps
    post_row.append(GetJosephInstructions(post, spec))  # Actual steps
    post_row.append(post) # all order information appended to instructions
    #logger.info('Post complete\n')
    print('Post complete')
    return post_row

def StripQuotes(post):
    """ take all quotes out of the list """
    for i in range(len(post)):
        if type(post[i]) == str:
            post[i] = post[i].replace('"', '')
    return post
    
def GetCutLength(post, spec):
    """ Cut length for angled and ramp post, otherwise spec. """
    need_offset = post[ORD['OrderItemBaseName']].lower()
    if ('angled' in need_offset) or ('ramp' in need_offset): 
        #logger.info('Calculating angled cut length...')
        print('Calculating angled cut length...')
        cut_length = round(post[ORD['CutLength']] 
                            + ANGLE_KERF 
                            + CUT_OFFSET
                            - math.tan(math.radians(post[ORD['PostAngle']])),4)
    else:
        cut_length = spec[SPEC['Cut Length']]
    return cut_length
    
def GetAdditionalSteps(spec):
    """ Return zero if the spec is cut only post """
    steps = spec[SPEC['Steps']]
    if steps:
        return steps 
    else:
        return int()

def GetJosephInstructions(post, spec):
    """ Calculate offset for angles and return the instructions. """
    joseph_instructions = spec[SPEC['Joseph Instructions']]
    angle = post[ORD['PostAngle']]
    if angle:
        #logger.info('Calculating offset for front holes...')
        print('Calculating offset for front holes...')
        # Convert to a list of numbers
        spec_split = [float(x) for x in joseph_instructions.split(',')]
        start = spec_split.index(0) #first hole that needs offset
        j, k = 0, 2
        while spec_split[j] < spec_split[k]:
            j = k
            k += 2
        first_hole = spec_split[k] #first hole dimension
        end = j #last hole that needs offset
        for i in range(start,end+1,2):
            spec_split[i] += first_hole + round(2*math.tan(math.radians(angle)),4)
        joseph_instructions = ','.join(str(x) for x in spec_split)
        return joseph_instructions
    else:
        return joseph_instructions

##### MAIN #####

order_list = GetOrders()
production_list = PrepOrdersForProduction(order_list)
file_status = ProductionToCSV(production_list)
#logger.info(file_status)
print(file_status)

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

##### CONSTANTS #####

POST_ADJUST_CUTLENGTH = ['182534', '182642', '150194']
POST_OFFSET_FRONT = []
POST_ON_ANGLE = ['"B-5"','"B-5"','"B" Down','"B" Down','"B" Up','"B" Up','"J" Down','"J" Down','"J" Up','"J" Up','"S"','"S"']
ANGLE_POST_PARTNO = ['150194','214440','182642','214438','182534','214439','150195','214441','150197','214442','157332','214443']
RAMP_POST_PARTNO = ['264558','264559','264560','264561','264562','264563','264564','264565','264566','264567','264568','264569','264570','264571','264572','264573','264574','264575']

ORDER_COLUMNS = {
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

SPEC_COLUMNS = {
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

##### FUNCTIONS #####

def GetOrders():
    """ Query Office Dot for orders ready for production. """
    today_orders = []
    
    ###### TODO needs to be replaced with query

    order_book = xlrd.open_workbook('20190918production.xlsx')
    order_sheet = order_book.sheet_by_index(0)
    for r in range(1,order_sheet.nrows):
        today_orders.append(order_sheet.row_values(r))

    #####

    return today_orders

def MatchOrdersToSpecs(orders):
    """ Take today's orders and match to the part number spec row"""
    spec_book = xlrd.open_workbook('JosephInstructions.xlsx')
    spec_sheet = spec_book.sheet_by_index(0)
    # spec_partno is a list of all the part numbers in the spec sheet
    spec_partno = spec_sheet.col_values(0)

    post_quantity = len(orders)
    today_specs = []

    for post in range(post_quantity):
        this_post = orders[post]
        this_post_partno = this_post[ORDER_COLUMNS['PartNumber']]
        
        if this_post_partno  > 300000:
            # Deal with Special Order Posts = set the actual partno 
            this_post_configuration = this_post[ORDER_COLUMNS['PostConfiguration']]
            for i in range(len(POST_ON_ANGLE)):
                if this_post_configuration == POST_ON_ANGLE[i]:
                    this_post_partno = ANGLE_POST_PARTNO[i]

        print('this_post_partno: ', this_post_partno)
        # Iterate over spec sheet to find matching spec
        r = 0
        while this_post_partno != spec_partno[r]:
            r += 1
        today_specs.append(spec_sheet.row_values(r))

#            else:
#                #TODO need some way to notify if part number is not found.
#                print('Spec not found for ', 
#                        this_post[ORDER_COLUMNS['PartNumber']],
#                        ' ',
#                        this_post[ORDER_COLUMNS['PieceNumber']],
#                        )
    return today_specs

def PrepOrdersForProduction(orders, specs):
    """ Combine today's orders and specs into a cut list for Joseph """
    production_ready = []
    this_order = []
    this_spec = []
    post_quantity = len(orders)
    for r in range(post_quantity):
        this_order = orders[r]
        this_spec = specs[r]
        print('Production #', r)
        print(this_order)
        print(this_spec)
        this_post = ['DEFAULT','DEFAULT','2X2','DEFAULT','DEFAULT']
        if this_order[ORDER_COLUMNS['PartNumber']] in POST_ADJUST_CUTLENGTH:
            this_post.append(CalculateCutLength(this_order[ORDER_COLUMNS['Cut Length']], this_order[ORDER_COLUMNS['PostAngle']]))
        else:
            this_post.append(this_spec[SPEC_COLUMNS['Cut Length']])
        this_post.append(1)
        this_post.append(int(this_spec[SPEC_COLUMNS['Steps']]))
        if this_order[ORDER_COLUMNS['PartNumber']] in POST_OFFSET_FRONT:
            this_post.append(PostOffsetFront(this_spec[SPEC_COLUMNS['Joseph Instructions']]),this_order[ORDER_COLUMNS['PostAngle']])
        else:
            this_post.append(this_spec[SPEC_COLUMNS['Joseph Instructions']])
        this_post.append(this_order)
        production_ready.append(this_post)
    print(production_ready)
    return production_ready

def ProductionToCSV(production):
    #TODO 
    filename = str(datetime.date.today()) + '-cutlist.csv'
    with open(filename, 'w', newline='') as f:
        cutlist = csv.writer(f, delimiter=',', 
                quotechar='"', quoting=csv.QUOTE_MINIMAL
                )
        cutlist.writerows(production)
    print('File written!')
    return True

def CalculateOffset(angle):
    """ Calculate the offset of front holes for angle posts. """
    offset = 2 * math.tan(math.radians(angle))
    return offset

def CalculateCutLength(original, angle):
    """ Joseph will cut long and then angle saw will cut to right length at angle
    original length + kerf + offset
    """
    new = original + 0.140 + tan(radians(angle))
    return new

def PostOffsetFront(spec, angle):
    """  """
    spec_split = [int(x) for x in spec.split(",")]
    start = spec_split.index(0)
    while spec_split[j] < spec_split[j+2]:
        j = j+2
    end = j
    offset = 2 * tan(radians(angle))
    for i in range(start,end):
        spec_split[i] = spec_split[i] + offset
    new_spec = ','.join(spec_split)    
    return new_spec

# ---------- Main ----------

order_list = GetOrders()
production_with_specs = MatchOrdersToSpecs(order_list)
production_list = PrepOrdersForProduction(order_list, production_with_specs)
ProductionToCSV(production_list)
print('Production is set!')

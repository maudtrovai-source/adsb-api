import json,pymysql,time
from flask import Flask
from flask import request,redirect
import datetime
import yaml


app = Flask(__name__)

db_config = None
with open("config.yml", "r") as file:
    config = yaml.safe_load(file)
    db_config = config['mysql']     

def auth(token):
    if token is None:
        return False
    conn = pymysql.connect(**db_config) 
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = 'SELECT * FROM `rovaimt_auth` WHERE `token` = %s;'
    cur.execute(sql,(token,))
    results = cur.fetchall()
    conn.close()
    if len(results) == 1:
        return True
    else:
        return False

def log(token,endpoint,res):
    conn = pymysql.connect(**db_config)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = '''INSERT INTO `rovaimt_log` (`endpoint`,`token`,`code`,`msg`,`sqltime`,`dt`) VALUES (%s,%s,%s,%s,%s,%s)'''
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(sql,(endpoint,token,res.get('code'),res.get('msg'),res.get('sqltime'),dt))
    conn.close()

def clean(value):
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    return float(value)


@app.route("/", methods=['GET','POST'])
def root():
    res = {} 
    res['code'] = 2
    res['msg'] = 'No endpoint specified'
    res['req'] = '/'
    return json.dumps(res,indent=4)
    #return '<b>hello</b>'

@app.route("/getData", methods=['GET','POST'])
def getData():
    res = {}
    res['req'] = 'getData'
    res['sqltime'] = 0

    if not auth(request.args.get('key')):
        res['code'] = 0
        res['msg'] = 'auth error'
        log(request.args.get('key'),res['req'],res)
        return json.dumps(res,indent=4)

    start = request.args.get('start')
    end = request.args.get('end')
    if start is None or end is None:
        res['code'] = 0
        res['msg'] = 'start and end must be provided.'
        log(request.args.get('key'),res['req'],res)
        return json.dumps(res,indent=4)

    conn = pymysql.connect(**db_config)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = 'SELECT * FROM `class_datapoints` WHERE `date_time` BETWEEN %s AND %s ORDER BY `date_time` LIMIT 500;'
    t1 = time.time()
    cur.execute(sql,(start,end))
    rows = cur.fetchall()
    res['sqltime'] = time.time() - t1
    conn.close()

    items = []
    for row in rows:
        item = {}
        item['dpid'] = row['dpid']
        item['date_time'] = clean(row['date_time'])
        item['hex'] = row['hex']
        item['flight_num'] = row['flight_num']
        item['squawk'] = row['squawk']
        item['lat'] = clean(row['lat'])
        item['lon'] = clean(row['lon'])
        item['fid'] = row['fid']
        item['gs'] = clean(row['gs'])
        item['alt_gps'] = row['alt_gps']
        item['alt_baro'] = row['alt_baro']
        item['cat'] = row['cat']
        item['track'] = clean(row['track'])
        item['nav_heading'] = clean(row['nav_heading'])
        items.append(item)

    res['code'] = 1
    res['msg'] = 'ok'
    res['results'] = items
    res['num_results'] = len(items)
    log(request.args.get('key'),res['req'],res)
    return json.dumps(res,indent=4)

@app.route("/countInPolygon", methods=['GET','POST'])
def countInPolygon():
    res = {} 
    res['req'] = 'countInPolygon'
    res['sqltime'] = 0
    if not auth(request.args.get('key')):
        res['code'] = 0
        res['msg'] = 'auth error'
        log(request.args.get('key'),res['req'],res)
        return json.dumps(res,indent=4)

    polygon = request.args.get('polygon')
    points = []
    try:
        for pair in polygon.split(','):
            x,y = pair.split()
            points.append(f'{float(x)} {float(y)}')
    except Exception as e:
        points = []
    if len(points) < 4 or points[0] != points[-1]:
        res['code'] = 0
        res['msg'] = 'polygon needs to be provided as closed points, e.g. -74 42,-75 39,-74 41,-74 42'
        log(request.args.get('key'),res['req'],res)
        return json.dumps(res,indent=4)

    conn = pymysql.connect(**db_config) 
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = 'SELECT COUNT(*) AS `count` FROM `class_datapoints` WHERE ST_Within(`geo_point`, ST_GeomFromText(%s,0));'
    shape = 'Polygon((' + ','.join(points) + '))'
    t1 = time.time()
    cur.execute(sql,(shape,))
    res['sqltime'] = time.time() - t1
    row = cur.fetchone()
    conn.close()

    res['code'] = 1
    res['msg'] = 'ok'
    res['polygon'] = shape
    res['count'] = row['count']
    log(request.args.get('key'),res['req'],res)
    return json.dumps(res,indent=4)

@app.route("/getAvgSpeedByFlight", methods=['GET','POST'])
def getAvgSpeedByFlight():
    res = {} 
    res['req'] = 'getAvgSpeedByFlight'
    res['sqltime'] = 0
    if not auth(request.args.get('key')):
        res['code'] = 0
        res['msg'] = 'auth error'
        log(request.args.get('key'),res['req'],res)
        return json.dumps(res,indent=4)

    start = request.args.get('start')
    end = request.args.get('end')
    where = ''
    vals = []
    if start is not None and end is not None:
        where = 'WHERE `date_time` BETWEEN %s AND %s'
        vals = [start,end]
    elif start is not None:
        where = 'WHERE `date_time` >= %s'
        vals = [start]
    elif end is not None:
        where = 'WHERE `date_time` <= %s'
        vals = [end]

    conn = pymysql.connect(**db_config) 
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = f'SELECT `flight_num`, AVG(`gs`) AS `avg_speed` FROM `class_datapoints` {where} GROUP BY `flight_num` ORDER BY `flight_num` LIMIT 0,500;'
    t1 = time.time()
    cur.execute(sql,vals)
    res['sqltime'] = time.time() - t1
    res['code'] = 1
    res['msg'] = 'ok'
    items = []
    for row in cur:
        item = {}
        item['flight_num'] = row['flight_num']
        item['avg_speed'] = clean(row['avg_speed'])
        items.append(item)
    conn.close()

    res['results'] = items
    res['num_results'] = len(items)
    log(request.args.get('key'),res['req'],res)
    return json.dumps(res,indent=4)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
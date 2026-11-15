import requests, json

base = 'http://127.0.0.1:5000'

urls = [
    # getData
    base + '/getData?key=123&start=2022-11-23 05:28:10&end=2022-11-23 05:28:15',   
    base + '/getData?key=999&start=2022-11-23 05:28:10&end=2022-11-23 05:28:15',   
    base + '/getData?key=123&start=2022-11-23 05:28:10',                           

    # countInPolygon
    base + '/countInPolygon?key=123&polygon=-74 42,-75 39,-74 41,-74 42',          
    base + '/countInPolygon?key=123',                                              
    base + '/countInPolygon?key=123&polygon=abc',                                  
    base + '/countInPolygon?key=123&polygon=-74 42,-75 39,-74 41',                 

    # getAvgSpeedByFlight
    base + '/getAvgSpeedByFlight?key=123&start=2022-11-23 05:00:00&end=2022-11-23 08:00:00',  
    base + '/getAvgSpeedByFlight?key=123&start=2022-11-23 07:00:00',                           
    base + '/getAvgSpeedByFlight?key=999',                                                     
]

for url in urls:
    r = requests.get(url)
    resp = json.loads(r.text)
    print(url.replace(base, ''))
    print('   code:', resp['code'], '| msg:', resp['msg'], '| sqltime:', resp['sqltime'])
    if 'num_results' in resp:
        print('   ', resp['num_results'], 'records')
    if 'count' in resp:
        print('    count:', resp['count'])
    print()
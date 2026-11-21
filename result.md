## detail page SSR
status 200 bytes 195006
episode links: 40
lastEpis: ['lastEpis:aG', 'lastEpis:af', 'lastEpis:p']
allEpis: ['allEpis:aG', 'allEpis:af', 'allEpis:p']
payEpisFrom: ['payEpisFrom:B', 'payEpisFrom:Y', 'payEpisFrom:Z']
episodes-text: ['78', '78', '78', '78', '78']

## api variants
h5/series/detail?seriesId=72945322 -> 200 46 bytes | {"code":404,"message":"请求地址不存在"}
h5/series/detail?id=72945322 -> 200 46 bytes | {"code":404,"message":"请求地址不存在"}
series/detail?seriesId=72945322 -> 200 46 bytes | {"code":404,"message":"请求地址不存在"}
h5/series/72945322 -> 200 46 bytes | {"code":404,"message":"请求地址不存在"}
h5/series/episodes?seriesId=72945322 -> 200 46 bytes | {"code":404,"message":"请求地址不存在"}
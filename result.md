## detail page SSR
status 200 bytes 196587
episode links: 40
lastEpis: ['lastEpis:aL', 'lastEpis:ao', 'lastEpis:p']
allEpis: ['allEpis:aL', 'allEpis:ao', 'allEpis:p']
payEpisFrom: ['payEpisFrom:G', 'payEpisFrom:R', 'payEpisFrom:Z']
episodes-text: ['78', '78', '78', '78', '78']

## api variants
h5/series/detail?seriesId=72945322 -> 200 46 bytes | {"code":404,"message":"请求地址不存在"}
h5/series/detail?id=72945322 -> 200 46 bytes | {"code":404,"message":"请求地址不存在"}
series/detail?seriesId=72945322 -> 200 46 bytes | {"code":404,"message":"请求地址不存在"}
h5/series/72945322 -> 200 46 bytes | {"code":404,"message":"请求地址不存在"}
h5/series/episodes?seriesId=72945322 -> 200 46 bytes | {"code":404,"message":"请求地址不存在"}
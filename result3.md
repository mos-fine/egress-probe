home cards=40 slugs=39
scripts: 5
api strings: 0

## paging tests
/search?keyword=love&page=2 -> bytes=109364 slugs=20
/dramas?page=2 -> bytes=190683 slugs=30
/dramas/romance?page=2 -> bytes=185837 slugs=28
/dramas/romance/2 -> ERR <HTTPError 404: 'Not Found'>
/dramas/all -> bytes=190775 slugs=30
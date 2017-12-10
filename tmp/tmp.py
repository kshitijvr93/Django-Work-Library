import urllib.parse
username='robertvphillips@gmail.com'
password='Rys08nat!'
f={'pid': 'robertvphillips@gmail.com:Rys08nat!'}
f={'usr': 'robertvphillips@gmail.com', 'password':'Rys08nat!'}
print(urllib.parse.urlencode(f))

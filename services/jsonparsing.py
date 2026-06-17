import urllib
from urllib.parse import urlencode, quote
from functools import partial


def quote_keep_plus(s, safe, encoding, errors):
    return quote(s, safe='+', encoding=encoding, errors=errors)

params = {"api_key": "abc+def", "q": "hello world"}
#quote_keep_plus = partial(quote, safe=safe+'+')
url=urlencode(params, quote_via=quote_keep_plus)
print(f"{url}")
# 'api_key=abc+def&q=hello%20world'

jsonparams = {"q": "97055+US", "api_key": "123456789"}
urlparams = urllib.parse.urlencode( jsonparams,quote_via=quote_keep_plus)
urlparams =  "https://geocode.maps.co/search?"+urlparams
print(f"{urlparams}")
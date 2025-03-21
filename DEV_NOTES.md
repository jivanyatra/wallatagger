## To Do

### ~~General Steps~~
1. ~~Authenticate via env vars~~
2. ~~Check for timestamp~~
3. ~~Get articles up to time frame~~
4. ~~Parse body for URL scheme (regex)~~
5. ~~Make call to add tag to article for each tag~~

### Improvements
1. break out formatting tags string work into new func
2. add flag to reprocess tags
3. before updating tags, check if tags exist
   1. if tags exist and reprocess == False, skip and log debug
   2. if tags exist and reprocess == True, check if the strings are the same.
      1. if they are the same, skip and log info
      2. if they are different, update and log info
4. if errors occur, set `new_ts` to before the earliest error
5. log the errors and time at warning level

## Authenticate

```
http POST http://localhost:8000/oauth/v2/token \
    grant_type=password \
    client_id=1_3o53gl30vhgk0c8ks4cocww08o84448osgo40wgw4gwkoo8skc \
    client_secret=636ocbqo978ckw0gsw4gcwwocg8044sco0w8w84cws48ggogs4 \
    username=wallabag \
    password=wallabag

You'll have this in return:

HTTP/1.1 200 OK
Cache-Control: no-store, private
Connection: close
Content-Type: application/json
Date: Tue, 05 Apr 2016 08:44:33 GMT
Host: localhost:8000
Pragma: no-cache
X-Debug-Token: 19c8e0
X-Debug-Token-Link: /_profiler/19c8e0
X-Powered-By: PHP/7.0.4

{
    "access_token": "ZGJmNTA2MDdmYTdmNWFiZjcxOWY3MWYyYzkyZDdlNWIzOTU4NWY3NTU1MDFjOTdhMTk2MGI3YjY1ZmI2NzM5MA",
    "expires_in": 3600,
    "refresh_token": "OTNlZGE5OTJjNWQwYzc2NDI5ZGE5MDg3ZTNjNmNkYTY0ZWZhZDVhNDBkZTc1ZTNiMmQ0MjQ0OThlNTFjNTQyMQ",
    "scope": null,
    "token_type": "bearer"
}
```

```
h = {"Authorization": "Bearer {access_token}"}
get /api/entries
https://domain.com/api/entries?archive=0&starred=0&sort=created&order=desc&page=1&perPage=1&public=0&detail=full
headers=h

for item in response["items"]:
    parse(item["content"])
    entry = item["id"]
    
    post /api/entries/{entry}/tags
    {"tags" : "tag1,tag2,tag3"}
    
regexpr = r"tags\.domain\.com\/(.+?)\/"
get group from each match
```

## Timestamps

API expects timestamps as integers, even if it returns a datetime like object.

For manual testing, you can login to:

```
https://domain.com/api/doc/
```

you want the `entries` endpoint. After authenticating, you can get an integer ts from [The Epoch Converter](https://www.epochconverter.com/)

Test data:

```
Date and time (GMT): Thursday, April 4, 2024 12:00:01 AM
Epoch timestamp: 1712188801
```

datetime should be able to convert timestamps to integers

we can load timestamps as human-readable when necessary, but we prefer integer timestamps

```
>>>datetime.datetime.fromtimestamp(1712188801)
datetime.datetime(2024, 4, 3, 20, 0, 1)
>>>datetime.datetime.utcfromtimestamp(1712188801)
datetime.datetime(2024, 4, 4, 0, 0, 1)

>>>datetime.datetime.fromisoformat("20240402")
datetime.datetime(2024, 4, 2, 0, 0)
>>>datetime.datetime.fromisoformat("20240402T12:12:12")
datetime.datetime(2024, 4, 2, 12, 12, 12)

>>>datetime.datetime.fromisoformat("20240402T12:12:12+0000")
datetime.datetime(2024, 4, 2, 12, 12, 12, tzinfo=datetime.timezone.utc)
>>>datetime.datetime.fromisoformat("20240402T12:12:12+0000").toordinal()
738978
>>>datetime.datetime.fromisoformat("20240402T12:12:12+0000").timestamp()
1712059932.0

need to use floor function there ^
```


## Adding entries

yields:

```

```

## Pagination

```
resp.json()["_links"] -> {
    "self": {
        "href": "http://127.0.0.1:8080/api/entries?archive=0&starred=0&public=0&sort=created&order=desc&tags=&since=0&detail=full&page=1&perPage=100"
    },
    "first": {
        "href": "http://127.0.0.1:8080/api/entries?archive=0&starred=0&public=0&sort=created&order=desc&tags=&since=0&detail=full&page=1&perPage=100"
    },
    "last": {
        "href": "http://127.0.0.1:8080/api/entries?archive=0&starred=0&public=0&sort=created&order=desc&tags=&since=0&detail=full&page=48&perPage=100"
    },
    "previous": {
        "href": "http://127.0.0.1:8080/api/entries?archive=0&starred=0&public=0&sort=created&order=desc&tags=&since=0&detail=full&page=47&perPage=100"
    },
    ^^ previous only exists if there's a previous page! if not, it's not there. first page doesn't have a previous entry.
    "next": {
        "href": "http://127.0.0.1:8080/api/entries?archive=0&starred=0&public=0&sort=created&order=desc&tags=&since=0&detail=full&page=2&perPage=100"
    },
    ^^ next only exists if there's a next page! if not, it's not there. last page doesn't have a next entry.
}
```


## Newest version issues

Newest version in docker complains about "oauth required"

DO NOT pass "Bearer {token}" as the "Authorization" header!! This only works for the doc page

Instead, send "access_token" key, value in body:
* requests.post -> gets passed in the data dict
* requests.get -> gets passed in params dicts
* NO USING `headers`

## Tests

___NEED to inject site template for parsing pages!!___

1. run tests/docker_test_runner.sh
1. default user/pass = `wallabag/wallabag`
1. client_id = `1_4j4oh4xqini8ckkgwssso0s8kc4kscw88w0swkos88cw0skg0o`
1. client_secret = `3vpq4a624feogowwwocc04wswgggk80o8ccw0wcgossk0s4cc`
1. use api to load a page, run tests...
1. using `pytest` with a runner to the tests "script" in PyCharm
1. using runner for "script" to test as well

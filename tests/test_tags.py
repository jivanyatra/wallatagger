from pprint import pprint as pp
from src import wallatagger
import re, requests


def gen_auth_body():
    auth_body = {
        "grant_type": "password",
        "username": "wallabag",
        "password": "wallabag",
        "client_id": "1_65zthm9gtdkw4oo8swsg4848sowwwk8ck8s0wk4gs4kc0swwks",
        "client_secret": "4i3tykbjwf408g008ocg48koos8ckskc04sosw4go04ksgo4k0",
    }
    return auth_body


def gen_base_url():
    base_url = "http://localhost"
    return base_url


def check_docker():
    auth_body = gen_auth_body()
    base_url = gen_base_url()
    try:
        r = requests.get(base_url + "/api/info", headers=auth_body)
    except Exception as e:
        assert e == ""
    assert r.status_code == 200


def load_page(page, token):
    #auth_headers = {"Authentication": f"Bearer {token}"}
    base_url = gen_base_url()
    body = {
        "url": page,
        "access_token": token
    }
    r = requests.post(base_url + "/api/entries", data=body)  #headers=auth_headers, json=body)
    assert r.status_code == 200
    return r


def test_tags():
    auth_body = gen_auth_body()
    base_url = gen_base_url()
    token = wallatagger.authenticate(base_url, auth_body)
    page1 = "" #"http://example.com"
    page2 = ""
    r = load_page(page1, token)
    assert r.status_code == 200
    r = load_page(page2, token)
    assert r.status_code == 200
    old_ts = 0
    '''
    try:
        entries_list = wallatagger.get_entries_list(base_url, auth_headers, old_ts)
    except Exception as e:
        print(f"Exception occurred: {e}")
    '''
    params = {
        "sort": "created",
        "order": "asc",
        "page": "1",
        "perPage": "100",
        "access_token": token
    }
    r = requests.get(base_url + "/api/entries", params=params)
    items = r.json()["_embedded"]["items"]
    content1 = items[0]["content"]
    content2 = items[1]["content"]
    tags_string = wallatagger.parse_for_tags(content1, re.compile(r"regex"))
    assert tags_string == ''
    tags_string = wallatagger.parse_for_tags(content2, re.compile(r"regex"))
    assert tags_string == ''
    #r = requests.get()

    page = "url"
    r = load_page(page, token)
    assert r.status_code == 200
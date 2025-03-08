# from pprint import pprint as pp
# from src
import wallatagger
import re
import requests

print(dir(wallatagger))


# for docs page
# Bearer ZmFlOGZhYWM4ODhkZjhmZjczNzFiY2E5MGRkNzMzNjM5MTU3MGUyZGRkMzM1OTI3ZTgxZDI4MjAxY2Q5YzVmMw
def gen_auth_body():
    auth_body = {
        "grant_type": "password",
        "username": "wallabag",
        "password": "wallabag",
        "client_id": "1_65zthm9gtdkw4oo8swsg4848sowwwk8ck8s0wk4gs4kc0swwks",
        "client_secret": "4i3tykbjwf408g008ocg48koos8ckskc04sosw4go04ksgo4k0",
        # "client_id": "1_5dnifffgieckk4080gcs88og0g4gsgc84g4k0wcc44wsogg408",
        # "client_secret": "1boh10kal3nooc4ww8o4wgkg8oc88w4kw0soswcocgg4so4ws0",
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
    # auth_headers = {"Authentication": f"Bearer {token}"}
    base_url = gen_base_url()
    body = {"url": page, "access_token": token}
    r = requests.post(
        base_url + "/api/entries", data=body
    )  # headers=auth_headers, json=body)
    assert r.status_code == 200
    return r


def test_initial_page():
    auth_body = gen_auth_body()
    base_url = gen_base_url()
    token = wallatagger.authenticate(base_url, auth_body)

    params = {
        "sort": "created",
        "order": "asc",
        "page": "1",
        "perPage": "100",
        "access_token": token,
    }
    r = requests.get(base_url + "/api/entries", params=params)
    items = r.json()["_embedded"]["items"]
    content = items[0]["content"]
    tags_string = wallatagger.parse_for_tags(
        content, re.compile(r"wired\.com\/tag\/(.+?)[\"\/]")
    )
    assert tags_string == "automation,longreads,san-francisco,self-driving-cars,waymo"


def test_remove_article():
    auth_body = gen_auth_body()
    base_url = gen_base_url()
    token = wallatagger.authenticate(base_url, auth_body)

    params = {
        "sort": "created",
        "order": "asc",
        "page": "1",
        "perPage": "100",
        "access_token": token,
    }
    r = requests.get(base_url + "/api/entries", params=params)
    items = r.json()["_embedded"]["items"]
    item_id = items[0]["id"]
    url = items[0]["url"]
    hashed_url = items[0]["hashed_given_url"]

    exists_before_params = {
        "access_token": token,
        "hashed_url": hashed_url,  # "1ad5a6f95c0903d600c24451a5a396f3565b96b2",
        "url": url,  # "https://www.wired.com/story/waymo-robotaxi-driverless-future/",
    }
    exists_before = requests.get(
        base_url + "/api/entries/exists", params=exists_before_params
    )
    assert exists_before.json()["exists"] == True

    delete_item_params = {
        "access_token": token,
        "expect": "id",
        "entry": item_id,
    }
    delete_item = requests.delete(
        base_url + f"/api/entries/{item_id}", params=delete_item_params
    )
    assert delete_item.status_code == 200

    exists_after = requests.get(
        base_url + "/api/entries/exists", params=exists_before_params
    )
    assert exists_after.json()["exists"] == False


def test_tags():
    print(dir(wallatagger))
    auth_body = gen_auth_body()
    base_url = gen_base_url()
    token = wallatagger.authenticate(base_url, auth_body)
    page1 = "https://www.wired.com/story/nokia-4g-network-on-the-moon/"  # "http://example.com"
    page2 = "https://www.wired.com/story/the-ev-buyers-guide-to-an-uncertain-future/"
    r = load_page(page1, token)
    assert r.status_code == 200
    r = load_page(page2, token)
    assert r.status_code == 200
    old_ts = 0
    """
    try:
        entries_list = wallatagger.get_entries_list(base_url, auth_headers, old_ts)
    except Exception as e:
        print(f"Exception occurred: {e}")
    """
    params = {
        "sort": "created",
        "order": "asc",
        "page": "1",
        "perPage": "100",
        "access_token": token,
    }
    r = requests.get(base_url + "/api/entries", params=params)
    items = r.json()["_embedded"]["items"]
    content1 = items[0]["content"]
    content2 = items[1]["content"]
    # https://www.wired.com/tag/electric-vehicles/
    tags_string = wallatagger.parse_for_tags(
        content1, re.compile(r"wired\.com\/tag\/(.+?)[\"\/]")
    )
    assert (
        tags_string
        == "4g-lte,mobile-world-congress,moon,mwc,nasa,nokia,phones,space,spacecraft"
    )
    tags_string = wallatagger.parse_for_tags(
        content2, re.compile(r"wired\.com\/tag\/(.+?)[\"\/]")
    )
    assert (
        tags_string
        == "electric-vehicles,elon-musk,evs-and-hybrids,infrastructure,taxes,tesla"
    )
    # r = requests.get()

    page = "url"
    r = load_page(page, token)
    assert r.status_code == 200

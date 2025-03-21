import re
from datetime import datetime

# noinspection PyPackageRequirements
from dotenv import find_dotenv, load_dotenv, set_key
from loguru import logger
import os
import requests
import sys


log_level = "INFO"
log_path = "wallatagger.log"


def load_env_vars():
    dotenv_file = find_dotenv()
    load_dotenv(dotenv_file)
    auth_body = dict()
    auth_body["grant_type"] = os.getenv("GRANT_TYPE")
    auth_body["client_id"] = os.getenv("CLIENT_ID")
    auth_body["client_secret"] = os.getenv("CLIENT_SECRET")
    auth_body["username"] = os.getenv("USER")
    auth_body["password"] = os.getenv("PASS")
    base_url = os.getenv("BASE_URL")
    conf_log_level = os.getenv("LOG_LEVEL")
    if conf_log_level:
        global log_level
        log_level = conf_log_level
    conf_log_path = os.getenv("LOG_PATH")
    if conf_log_path:
        global log_path
        log_path = conf_log_path
    return auth_body, base_url


def authenticate(base_url, auth_body):
    resp = requests.post(base_url + "/oauth/v2/token", json=auth_body)
    if resp.status_code != 200:
        logger.error(f"Authentication failed...{resp.status_code = } ; {resp.content}")
        sys.exit("Authentication Failed")
    token = resp.json()["access_token"]
    logger.debug("Authenticated!")
    return token


def authenticate_only(server_base_url=None, credentials=None, load_env=True, doc=False):
    """Returns auth token/headers for CLI usage
    Optionally add a 'doc=True' flag for the string
    you can paste into the wallabag/api/doc page"""
    if load_env:
        credentials, server_base_url = load_env_vars()
    else:
        if not credentials:
            raise Exception("No credentials dict provided!")
        if not server_base_url:
            raise Exception("No base URL for server provided!")
    token = authenticate(server_base_url, credentials)
    if doc:
        return f"Bearer {token}"
    else:
        return token


def get_new_timestamp():
    now = datetime.now()
    return str(now.timestamp().__floor__())


def get_last_timestamp():
    sync_ts = os.getenv("LAST_SYNC_TS")
    logger.debug(f"Last timestamp loaded from env: {sync_ts = }")
    if not sync_ts:
        logger.warning("No last synced timestamp!")
        logger.warning("This will process the entire backlog. This may take a while...")
        return 0
    # check for iso-assumable format
    if "T" in sync_ts:
        ts = datetime.fromisoformat(sync_ts)
        secs = ts.timestamp()
        logger.debug(f"Inferring TimeZone Data: {ts} (Unix Epoch: {secs})")
        return secs
    else:  # assume Unix Epoch and convert to integer
        logger.debug("Assuming Unix Epoch, as required")
        return int(sync_ts)


def get_parsing_pattern():
    pattern_string = os.getenv("REGEX")
    logger.debug(f"{pattern_string = }")
    compiled_pattern = re.compile(pattern_string)
    return compiled_pattern


def get_reprocess_flag():
    reprocess = os.getenv("REPROCESS", "False").lower()
    logger.debug(f"{reprocess = }")
    if reprocess in ["true", "1", "t"]:
        return True
    elif reprocess not in ["false", "0", "f"]:
        logger.error(f"Could not parse {reprocess = } into a boolean; setting to False")
    return False


def set_new_timestamp(timestamp):
    dotenv_file = find_dotenv()
    os.environ["LAST_SYNC_TS"] = timestamp
    set_key(dotenv_file, "LAST_SYNC_TS", timestamp)


def get_entries_list_first_page(base_url, auth_dict, last_timestamp):
    """Deprecated, but left for testing the module"""
    params = {
        "sort": "created",
        "order": "asc",
        "page": "1",
        "perPage": "100",
        "since": last_timestamp,
    }
    params.update(auth_dict)
    resp = requests.get(base_url + "/api/entries", params=params)
    unprocessed_entries = None
    logger.debug(f"entries response: {resp.status_code}")
    if resp.status_code == 200:
        unprocessed_entries = resp.json()["_embedded"]["items"]
    return unprocessed_entries


def get_entries_generator(base_url, auth_dict, last_timestamp):
    params = {
        "sort": "created",
        "order": "asc",
        "page": "1",
        "perPage": "100",
        "since": last_timestamp,
    }
    params.update(auth_dict)
    next_page_url = f"{base_url}/api/entries"
    while next_page_url:
        logger.debug(f"fetching page_url: {next_page_url}")
        resp = requests.get(next_page_url, params=params)
        unprocessed_entries = None
        logger.debug(f"entries response: {resp.status_code}")
        if resp.status_code != 200:
            raise Exception(
                f"entries_generator request returned status code {resp.status_code} ; {resp.json()}"
            )
        resp_data = resp.json()
        unprocessed_entries = resp_data["_embedded"]["items"]
        current_page = resp_data["page"]
        total_pages = resp_data["pages"]
        logger.info(f"yielding page {current_page} of {total_pages}")
        next_item = resp_data["_links"].get("next", None)

        yield unprocessed_entries

        if next_item:
            next_page_url = next_item["href"]
            logger.debug(f"{next_page_url = }")
        else:
            next_page_url = None
            logger.debug("no next page")
    logger.debug(f"exhausted all {total_pages} pages")


def get_and_update_articles(server_url, auth_key, old_ts, reprocess_flag, pattern):
    successes = 0
    skips = 0
    failures = 0
    total_entries = 0

    for entries_list in get_entries_generator(server_url, auth_key, old_ts):
        # logger.debug(f"{entries_list = }")
        logger.info(f"{len(entries_list)} entries found")
        i_successes, i_skips, i_failures, i_total = process_entries(
            server_url, auth_key, entries_list, reprocess_flag, pattern
        )
        successes += i_successes
        skips += i_skips
        failures += i_failures
        total_entries += i_total

    logger.info(
        f"Finished processing {total_entries} entries; {successes = }, {failures = }, {skips = }"
    )


def get_entry_tags(entry_tags):
    if len(entry_tags) == 0:
        logger.debug("no existing tags")
        return ""
    tags_list = []
    for tag in entry_tags:
        tags_list.append(tag["label"])
    tags_list = set(tags_list)
    tags_list = sorted(tags_list)
    tags_string = ",".join(tags_list)
    logger.debug(f"found existing tags: {tags_string}")
    return tags_string


def parse_for_tags(entry_content, re_pattern):
    matches = re.findall(re_pattern, entry_content)
    logger.debug(f"{matches = }")
    matches = set(matches)
    matches = sorted(matches)
    tags_string = ",".join(matches)
    logger.debug(f"{tags_string = }")
    return tags_string


def update_entry_tags(base_url, auth_dict, entry, tags) -> bool:
    data = {"tags": tags}
    data.update(auth_dict)
    try:
        resp = requests.post(base_url + f"/api/entries/{entry}/tags", data=data)
    except Exception as update_error:
        logger.error(
            f"Failed to update {entry = } ; Exception occurred: {update_error}"
        )
        return False

    if resp.status_code == 200:
        logger.debug(f"Updated {entry = } ; {resp.status_code}")
        return True
    else:
        logger.error(
            f"Failed to update {entry = } ; {resp.status_code = }, {resp.content}"
        )
        return False


def process_entries(base_url, headers, unprocessed_entries, reprocess_flag, re_pattern):
    logger.debug(f"Using regex pattern: '{re_pattern}'")
    successes = 0
    skips = 0
    failures = 0
    total = 0
    for item in unprocessed_entries:
        total += 1
        entry_id = item["id"]
        page_content = item["content"]
        tags = get_entry_tags(item["tags"])

        # TODO: change this to check for more than 2 tags - category tags when adding can prevent processing!!
        # TODO: Add threshold variable in config!
        if not reprocess_flag and tags:
            # entry already has tags, and we're not reprocessing !
            logger.debug(f"{entry_id = } already has {tags = }; skipping")
            skips += 1
            continue
        tags_list = parse_for_tags(page_content, re_pattern)
        if reprocess_flag and tags == tags_list:
            logger.debug(
                f"Reprocessing but {entry_id = } doesn't have changes to {tags = }; skipping"
            )
            skips += 1
            continue

        logger.debug(f"For {entry_id = }; found {tags_list = }")
        outcome = update_entry_tags(base_url, headers, entry_id, tags_list)
        if outcome:
            successes += 1
        else:
            failures += 1
    logger.debug(
        f"processed {len(unprocessed_entries)} entries; {successes = }, {failures = }, {skips = } in iteration"
    )
    return (successes, skips, failures, total)


def main():
    creds, server_url = load_env_vars()
    # noinspection PyArgumentList
    # TODO: change how these settings are read - sensitive from .env vars, non sensitive from config file
    logger.add(log_path, level=log_level)
    logger.info(f"Added logger @ {log_path} - {log_level = }")
    logger.info(f"{server_url = }")
    new_ts = get_new_timestamp()
    logger.info(f"new timestamp {new_ts}")
    old_ts = get_last_timestamp()
    logger.info(f"old timestamp {old_ts}")
    auth_token = authenticate(server_url, creds)
    auth_key = {"access_token": auth_token}
    pattern = get_parsing_pattern()
    reprocess_flag = get_reprocess_flag()
    entries_list = []
    try:
        get_and_update_articles(
            server_url, auth_key, entries_list, reprocess_flag, pattern
        )
    except Exception as e:
        # TODO: change above Exception to custom Exception
        logger.error(f"Exception occurred: {e}")
    finally:
        # TODO: remove this in favor of raising new exception and catching above
        if not entries_list:
            logger.info("No entries found, exiting...")
        set_new_timestamp(new_ts)
        logger.info(f"Set new timestamp {new_ts} ; Exiting...")


if __name__ == "__main__":
    main()

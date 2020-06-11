import os
from typing import Dict, Iterable, Union

import requests
import click


APP_URL = os.environ.get("APP_URL", "redisinsight:8001")


def load_credentials():
    """
    Load the session token and CSRF token to make protected API calls.
    """
    resp = requests.get(APP_URL)
    try:
        csrftoken = resp.cookies['csrftoken']
        sessionid = resp.cookies['sessionid']
        return sessionid, csrftoken
    except Exception:
        # For debugging a KeyError for sessionid cookie being thrown on some builds.
        print("RESP CONTENT:", resp, resp.content)
        print("RESP COOKIES:", resp.cookies)
        raise


def make_add_db_api_call(name: str, host: str, port: int, session_token: str, csrf_token: str):
    """
    Make API call to add databases. Raises exception on error response.
    """
    url = f"{APP_URL}/api/add-instance/?check_connection=true"
    resp = requests.post(url=url,
                         cookies={'csrftoken': csrf_token,
                                  'sessionid': session_token},
                         headers={'X-CSRFToken': csrf_token},
                         data={'host': host,
                               'port': port,
                               'password': None,
                               "instance_name": host,
                               "is_ssl": "false"})
    if not resp.ok:
        raise Exception("Error response:\n" + resp.content.decode())


def add_dbs(db_urls: Iterable[str]):
    """
    Add databases.
    """
    sessionid, csrftoken = load_credentials()
    for db_url in db_urls:
        host, port = db_url.split(':')
        make_add_db_api_call(name=host, host=host, port=port, session_token=sessionid, csrf_token=csrftoken)


@click.command()
@click.option('--db_urls', required=True, help='list of db urls separated by `;`. E.g. localhost:6379;localhost:6380')
def main(db_urls: str):
    db_urls = db_urls.split(';')
    add_dbs(db_urls)


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    main()

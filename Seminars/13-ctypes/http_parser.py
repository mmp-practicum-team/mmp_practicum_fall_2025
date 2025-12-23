from typing import Optional
import requests
from bs4 import BeautifulSoup
import time
import random

import cProfile
import pstats


def download_page(base_url: str, page_id: int) -> dict:
    url = base_url.format(page_id)

    # Perform an HTTP GET request and return only the fields we care about.
    # Note: no timeout/retries are set here—this is intentionally minimal for a profiling demo.
    req = requests.get(url)

    return {
        'status': req.status_code,
        'text': req.text
    }


def get_page_title(base_url: str, page_id: int) -> Optional[str]:
    """
    Download the page and extract the <title> using BeautifulSoup.
    """

    down_res = download_page(base_url, page_id)

    if down_res['status'] != 200:
        return None
    
    text = down_res['text']
    soup = BeautifulSoup(text, "lxml")
    title: str = soup.title

    return title


def complex_habraparser(base_url: str, page_id: int):
    """ 
    A heavier “toy” parser: simulates expensive processing and returns a random token.
    """

    down_res = download_page(base_url, page_id)

    if down_res['status'] != 200:
        return None
    
    # Artificial delay to emulate a slow parsing pipeline
    time.sleep(0.5)

    res = random.choice(down_res['text'].split())
    return res


def main():
    base_url = "https://habr.com/ru/articles/{0}/"

    with cProfile.Profile() as pr:
        for page_id in range(15):
            # Alternate workload (commented out): heavier parsing path.
            # res = complex_habraparser(base_url, page_id)
            # print(f"{page_id=}\t{res=}")

            # Main workload being profiled: download + HTML parse + title extraction.
            title = get_page_title(base_url, page_id)
            if title:
                print(f"{page_id=}\t{title}\n")

    # Convert raw profiling data into pstats and sort by time spent in functions.
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)

    # Optional: print profiling report to stdout.
    # stats.print_stats()

    # Persist profiling results for later inspection (e.g., snakeviz).
    stats.dump_stats('./http_parser.stats')


if __name__ == '__main__':
    main()

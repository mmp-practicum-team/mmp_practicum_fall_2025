import time
import requests
from bs4 import BeautifulSoup
import argparse
from typing import Optional

import threading
import multiprocessing
import multiprocessing.dummy

def get_page(url, n_attempts=5, t_sleep=1, headers={}, **kwargs):
    # This function is I/O-bound: most time is typically spent waiting for the network/server.
    for _ in range(n_attempts):
        page = requests.get(url, headers=headers)
        if page.status_code == 200:
            return page
        time.sleep(t_sleep)

    return None

def get_habr_article(article_number) -> Optional[str]:
    base_url = "https://habr.com/ru/articles/{0}"
    page = get_page(base_url.format(article_number))

    if page:
        return page.text
    return None


def get_article_title(article_number):
    article = get_habr_article(article_number)
    if article is None:
        return "NOT FOUND"
    
    soup = BeautifulSoup(article, features="lxml")
    title = soup.title

    return title


def get_article_title_ths(article_number):
    global titles
    global mutex

    title = get_article_title(article_number)

    with mutex:
        titles[article_number - 1] = title


def single(n_tasks: int):
    # Sequential baseline: fetch and parse titles one by one.
    titles = [get_article_title(i) for i in range(1, n_tasks)]

    for i, title in enumerate(titles, start=1):
        print(f"Article {i:2} title: {title}")


def threads(n_tasks: int):
    # Threading implementation
    # - Creates one Thread per task.
    # - Uses a shared `titles` list and a `Lock` to store results safely.

    global titles
    global mutex
    titles = [""] * n_tasks
    mutex = threading.Lock()

    threads = [
        threading.Thread(target=get_article_title, args=(i, ))
        for i in range(1, n_tasks+1)
    ]

    for th in threads:
        th.start()
    
    for th in threads:
        th.join()

    for i, title in enumerate(titles, start=1):
        print(f"Article {i:2} title: {title}")


def thread_pool(n_tasks: int, pool_size: int = 10):
    # Thread-pool implementation (I/O-bound concurrency):
    # - Uses `multiprocessing.dummy.Pool`, which provides the same API as `multiprocessing.Pool`
    #   but is backed by threads rather than processes.
    # - Runs up to `pool_size` worker threads concurrently, overlapping HTTP requests while other threads
    #   are blocked on network I/O, which typically yields speedups despite the GIL.

    with multiprocessing.dummy.Pool(pool_size) as pool:
        titles = pool.map(get_article_title, range(1, n_tasks))
    
    for i, title in enumerate(titles, start=1):
        print(f"Article {i:2} title: {title}")


def process_pool(n_tasks: int, pool_size: int = 10):
    # Process-pool implementation (I/O-bound concurrency with separate interpreters):
    # - Uses `multiprocessing.Pool`, which spawns multiple OS processes. Each worker runs in its
    #   own Python interpreter with its own GIL, so this approach is suitable for both I/O-bound
    #   and CPU-bound workloads.
    # - For THIS example (HTTP fetching + HTML parsing), a process pool often performs worse than
    #   a thread pool due to higher overhead: process startup, IPC, and pickling arguments/results.
    # - It can still be useful when tasks include significant CPU-bound post-processing, or when
    #   you want stronger isolation between workers.

    with multiprocessing.Pool(pool_size) as pool:
        titles = pool.map(get_article_title, range(1, n_tasks))
    
    for i, title in enumerate(titles, start=1):
        print(f"Article {i:2} title: {title}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("single", "threads", "pool", "process_pool"),
        default="pool",
        help=(
            "Execution mode: "
            "single (sequential), "
            "threads (one thread per task), "
            "pool (thread pool), "
            "process_pool (process pool)."
        ),
    )
    parser.add_argument(
        "--n_tasks",
        type=int,
        default=20,
        help="Number of articles to fetch (default: 20).",
    )
    parser.add_argument(
        "--pool_size",
        type=int,
        default=10,
        help="Number of workers for pool/process_pool modes (default: 10).",
    )
    args = parser.parse_args()

    if args.mode == "single":
        single(args.n_tasks)
    elif args.mode == "threads":
        threads(args.n_tasks)
    elif args.mode == "pool":
        thread_pool(args.n_tasks, pool_size=args.pool_size)
    else:
        process_pool(args.n_tasks, pool_size=args.pool_size)


if __name__ == "__main__":
    main()

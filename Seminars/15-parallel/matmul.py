import random
import time
import threading
import multiprocessing
import argparse


def matmul(A: list[list[float]], B: list[list[float]]):
    # Naive O(m * l * n) matrix multiplication implemented in pure Python.
    # This is intentionally slow to make the difference between threads and processes observable.

    m, l = len(A), len(A[0])
    _, n = len(B), len(B[0])

    C = [[0.0] * n for _ in range(m)]

    # Triple nested loop: CPU-heavy Python bytecode -> constrained by the GIL under threads.
    for i in range(m):
        for j in range(n):
            for k in range(l):
                C[i][j] += A[i][k] * B[k][j]
    
    # Print a marker so you can see when each job completes (flush=True avoids buffering issues).
    print(f"Finished", flush=True)
    return C


def single_thread():
    # Baseline: execute a single matrix multiplication in the main thread.
    # Matrices are created once and the multiplication is run once.

    m = 1_000
    l = 100
    n = 1_000

    A = [
        [random.random() for _ in range(l)] 
        for _ in range(m)
    ]
    B = [
        [random.random() for _ in range(n)] 
        for _ in range(l)
    ]

    C = matmul(A, B)
    return C


def multy_thread(njobs: int):
    # Run `njobs` matrix multiplications concurrently using threads.
    #
    # Key point: for this pure-Python CPU-bound workload, threads usually do not provide
    # linear speedup in CPython due to the GIL. You may see interleaving, but not true
    # multi-core parallelism.

    m = 1_000
    l = 100
    n = 1_000

    A = [
        [random.random() for _ in range(l)] 
        for _ in range(m)
    ]
    B = [
        [random.random() for _ in range(n)] 
        for _ in range(l)
    ]

    # Create threads that all execute the same CPU-bound function.
    tasks = [
        threading.Thread(target=matmul, args=(A, B))
        for _ in range(njobs)
    ]
    for t in tasks:
        t.start()
    
    # Wait for all threads to complete.
    for t in tasks:
        t.join()


def multy_process(njobs: int):
    # Run `njobs` matrix multiplications concurrently using processes.
    #
    # Key point: processes bypass the GIL limitation for CPU-bound Python code because each
    # process has its own interpreter and GIL, enabling true parallelism across CPU cores.
    # Trade-offs include higher startup overhead and the need to pickle/transfer arguments.

    m = 1_000
    l = 100
    n = 1_000

    A = [
        [random.random() for _ in range(l)] 
        for _ in range(m)
    ]
    B = [
        [random.random() for _ in range(n)] 
        for _ in range(l)
    ]

    # Create processes; each will execute `matmul` independently.
    tasks = [
        multiprocessing.Process(target=matmul, args=(A, B))
        for _ in range(njobs)
    ]
    for t in tasks:
        t.start()
    
    # Wait for all processes to complete.
    for t in tasks:
        t.join()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--njobs", type=int, required=False, help="Number of concurrent jobs to run.")
    parser.add_argument(
        "--mode",
        choices=("thread", "process"),
        default="process",
        help="Parallelization mode to use when --njobs is provided (default: process).",
    )
    args = parser.parse_args()

    if args.njobs is None:
        single_thread()
        return
    
    if args.njobs <= 0:
        raise SystemExit("--njobs must be a positive integer.")

    if args.mode == "thread":
        multy_thread(njobs=args.njobs)    # typically limited by GIL for this workload
    else:
        multy_process(njobs=args.njobs)   # typically achieves multi-core parallelism


if __name__ == "__main__":
    main()

import multiprocessing

daemon = True
workers = 2 * multiprocessing.cpu_count() + 1
worker_class = "sync"

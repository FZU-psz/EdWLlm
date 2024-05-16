import json

def file_lines(file_path):
    from itertools import (takewhile, repeat)
    buffer = 1024 * 1024
    with open(file_path) as f:
        buf_gen = takewhile(lambda x: x, (f.read(buffer) for _ in repeat(None)))
        return sum(buf.count('\n') for buf in buf_gen)
import os
from collections import namedtuple

def directory_crawl(path):
    targets = []
    for (path, dirs, files) in os.walk(path):
        targets.extend([os.path.join(path, f) for f in files])
    return targets

# Options for Joosc.
JooscOptions = namedtuple('JooscOptions',
    ['stage', 'include_stdlib', 'print_stdlib', 'directory_crawl'])

stdlib_files = directory_crawl('stdlib/5.0/java')


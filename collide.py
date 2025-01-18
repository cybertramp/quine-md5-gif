#
# Copyheart Rogdham, 2017
# See http://copyheart.org/ for more details.
#
# This program is free software. It comes without any warranty, to the extent
# permitted by applicable law. You can redistribute it and/or modify it under
# the terms of the CC0 1.0 Universal Licence (French).
# See https://creativecommons.org/publicdomain/zero/1.0/deed.fr for more
# details.
#

"""
Wrapper around the fastcoll binary used to create a MD5 collision

Download and compile it from http://www.win.tue.nl/hashclash/
"""

import os
import subprocess
import tempfile
from hashlib import md5


COLLISION_LEN = 128  # fastcoll generate two MD5 blocks
COLLISION_LAST_DIFF = 123

FASTCOLL_PATH = 'fastcoll_linux_amd64'

def collide(prefix):
    """
    Generate a collision with the chosen prefix

    Prefix must be aligned to a MD5 block (64 bytes)

    Returns two strings; append either one to the prefix and the result will
    have the same MD5 hash

    At position COLLISION_LAST_DIFF, the first string returned has a byte value
    smaller than the second one
    """
    assert len(prefix) % 64 == 0
    tmp_path = 'tmp'

    prefix_filename = os.path.join(tmp_path, 'prefix')
    # directory create
    with open(prefix_filename, 'wb') as prefix_fd:
        prefix_fd.write(prefix)
    
    # get current working directory
    cwd = os.getcwd()
    subprocess.check_call([
        f'{cwd}/{FASTCOLL_PATH}',
        prefix_filename
    ], stdout=subprocess.PIPE)
    
    coll_a_filename = f'{cwd}/md5_data1'
    coll_b_filename = f'{cwd}/md5_data2'
    with open(coll_a_filename, 'rb') as coll_a_fd:
        coll_a = coll_a_fd.read()[len(prefix):]
    with open(coll_b_filename, 'rb') as coll_b_fd:
        coll_b = coll_b_fd.read()[len(prefix):]
        
        
    assert coll_a != coll_b
    assert md5(prefix + coll_a).digest() == md5(prefix + coll_b).digest()
    assert len(coll_a) == len(coll_b) == COLLISION_LEN
    assert coll_a[COLLISION_LAST_DIFF] != coll_b[COLLISION_LAST_DIFF]
    if coll_a[COLLISION_LAST_DIFF] < coll_b[COLLISION_LAST_DIFF]:
        return (coll_a, coll_b)
    return (coll_b, coll_a)

#!/usr/bin/env python3

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
# edited by 2025 cybertramp
#

"""
Hashquine generator
"""

import os
import struct
from hashlib import md5
import time

import collide


class Hashquine():
    """
    Create a hashquine

    Specify a template directory for background and character images
    """

    def __init__(self, template_dir, out_filename):
        self.start_time = time.time()
        self.template_dir = template_dir
        self.out_filename = out_filename
        self.hash_img_coordinates = (102, 143)
        self.md5_mask = '           d5    dead           '  # already in bg
        
        self.tmp_path = 'tmp'
        print(f"Create {self.tmp_path} directory")
        os.makedirs(self.tmp_path, exist_ok=True)
        
        # read images
        self.background_blocks = self.read_gif('bg.gif')
        self.chars_img_data = {}
        for char in '0123456789abcdef':
            blocks = self.read_gif('char_{}.gif'.format(char))
            self.chars_img_data[int(char, 16)] = blocks['img_data']
            width, height = struct.unpack('<HH', blocks['img_descriptor'][5:9])
            if char == '0':
                self.char_width, self.char_height = width, height
            assert (self.char_width, self.char_height) == (width, height)

    def read_gif(self, filename):
        """
        Read the data from the GIF image

        Images must have a specific format: 16-colours pallete, etc.
        """
        blocks = {}
        with open(os.path.join(self.template_dir, filename), 'rb') as gif_fd:
            blocks['header'] = gif_fd.read(6)
            assert blocks['header'] in (b'GIF87a', b'GIF89a')
            blocks['lcd'] = gif_fd.read(7)  # logical screen descriptor
            assert blocks['lcd'].endswith(b'\xe3\x10\x00')  # gct of 16 colours
            blocks['gct'] = gif_fd.read(16 * 3)  # global colour table
            blocks['img_descriptor'] = gif_fd.read(10)  # image descriptor
            assert blocks['img_descriptor'][0] == 0x2c
            assert blocks['img_descriptor'][9] == 0
            # img data
            blocks['img_data'] = gif_fd.read(1)  # LZW min code size
            while True:  # img data sub-blocks
                blocks['img_data'] += gif_fd.read(1)  # sub-block data size
                if blocks['img_data'][-1] == 0:
                    break  # final sub-block (size 0)
                blocks['img_data'] += gif_fd.read(blocks['img_data'][-1])
            assert gif_fd.read(1) == b'\x3b'  # trailer
        return blocks

    def generate(self):
        """
        Generate the hashquine
        """
        graphic_control_extension = b'\x21\xf9\x04\x04\x02\x00\x00\x00'
        alternatives = {}  # (char_pos, char): (coll_pos, coll)
        
        # header
        generated_gif = self.background_blocks['header']
        generated_gif += self.background_blocks['lcd']
        generated_gif += self.background_blocks['gct']
        
        # place comment
        comment = b'cybertramp 2025\n' \
                  b'https://github.com/cybertramp\n' \
                  b'Original: https://github.com/rogdham/gif-md5-hashquine\n\n'

        generated_gif += b'\x21\xfe%s%s\x00' % (bytes([len(comment)]), comment)
        # place background
        generated_gif += graphic_control_extension
        generated_gif += self.background_blocks['img_descriptor']
        generated_gif += self.background_blocks['img_data']
        # start comment
        generated_gif += b'\x21\xfe'
        
        # generate all possible md5 characters frames
        top, left = self.hash_img_coordinates
        for char_pos in range(32):
            left += self.char_width
            if self.md5_mask[char_pos] != ' ':
                continue
            for char in range(16):
                char_img = graphic_control_extension
                char_img += b'\x2c%s\x00' % struct.pack(  # img descriptor
                    '<HHHH', left, top, self.char_width, self.char_height)
                char_img += self.chars_img_data[char]
                # add comment to align to a md5 block
                coll_diff = collide.COLLISION_LAST_DIFF
                align = 64 - (len(generated_gif) % 64)
                generated_gif += bytes([align - 1 + coll_diff])
                generated_gif += b'\x00' * (align - 1)  # any char would do
                # generate collision
                while True:
                    current_time = time.time()
                    print(f'Generating collision {char_pos * 16 + char + 1} | Data len: {len(generated_gif)}')
                    print(f"Elapsed time: {current_time - self.start_time:.2f} seconds")
                    coll_img, coll_nop = collide.collide(generated_gif)
                    assert coll_img[coll_diff] < coll_nop[coll_diff]
                    offset = collide.COLLISION_LEN - coll_diff - 1
                    coll_p_img = coll_img[coll_diff] - offset
                    coll_p_nop = coll_nop[coll_diff] - offset
                    pad_len = coll_p_nop - coll_p_img - len(char_img) - 4
                    if coll_p_img >= 0 and pad_len >= 0:
                        break
                    print('Unsatisfying collision, trying again')
                # push collision
                alternatives[char_pos, char] = (len(generated_gif), coll_img)
                generated_gif += coll_nop
                # continue comment up to image
                generated_gif += b'\x00' * coll_p_img  # any char would do
                generated_gif += b'\x00'  # end comment
                # add image
                generated_gif += char_img
                # start comment and align with big comment (end of coll_nop)
                generated_gif += b'\x21\xfe'
                generated_gif += bytes([pad_len])
                generated_gif += b'\x00' * pad_len  # any char would do
        # add a comment and bruteforce it until GIF md5 match the md5 mask
        current_md5 = md5(generated_gif)
        print('Bruteforcing final md5...')
        for garbage in range(1 << 32):  # 32 bits of bf should be enough
            end = struct.pack('<BIBB',
                              4, garbage,  # comment sub-block
                              0,  # end comment
                              0x3b)  # trailer
            new_md5 = current_md5.copy()
            new_md5.update(end)
            for mask_char, md5_char in zip(self.md5_mask, new_md5.hexdigest()):
                if mask_char != ' ' and mask_char != md5_char:
                    break
            else:
                generated_gif += end
                break
        else:
            raise ValueError('Did not find a GIF matching the md5 mask')
        # replace colls to show md5
        print('Target md5:', md5(generated_gif).hexdigest())
        for char_pos, char in enumerate(md5(generated_gif).hexdigest()):
            if self.md5_mask[char_pos] != ' ':
                continue
            coll_pos, coll = alternatives[char_pos, int(char, 16)]
            generated_gif = (
                generated_gif[:coll_pos] + coll +
                generated_gif[coll_pos + len(coll):]
            )
        print('Final md5: ', md5(generated_gif).hexdigest())
        return generated_gif
    
    def run(self):
        """
        Create and save the hashquine

        Doing so makes sure it works well with Makefiles
        """
        generated_gif = self.generate()
        with open(self.out_filename, 'wb') as out_fd:
            out_fd.write(generated_gif)

        elapsed_time = time.time() - self.start_time
        print(f'Time Elapsed: {elapsed_time:.2f} seconds')
        
        self.cleanup()
        
    def cleanup(self):
        """
        Cleanup the generated files
        """
        print("Cleaning up...md5 collision files")
        os.remove('md5_data1')
        os.remove('md5_data2')

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python3 generate.py <output_filename>')
        sys.exit(1)
    Hashquine('template', sys.argv[1]).run()

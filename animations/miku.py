from PIL import Image
import os
import sys
import math
from time import sleep
ASCII_CHARS = "@%#*+=-:. "

def get_miku_text(): 
    text = []
    file = open("mining/miningmsg.txt", "r")
    for line in file:
        text.append(line[:len(line)-1])

    print(len(text)) 
    file.close()
    return text

def animation(): 
    srcs = [
            "mining/IMG_20250215_181757.jpg",
            "mining/IMG_20250215_181703.jpg",
            "mining/IMG_20250215_181847.jpg"]
    screen_size = get_screen_size_char()
    imgs = read_photos(screen_size.lines - 6, screen_size.columns, srcs)
    frames = []

    for img in imgs:
        frames.append(get_ascii_frame(img))
    cur_frame = 0
    dir = 1 
    text = get_miku_text()

    for frame in frames:
        for line in text: 
            frame.append(line)

    while(True):
        sleep(.5)
        print_frame(frames[cur_frame], screen_size.columns)
        cur_frame += dir 

        if cur_frame < 0: 
            cur_frame = 1 
            dir = 1 

        if cur_frame >= 3:
            cur_frame = 1
            dir = -1 


def read_photos(height, width, paths: [str]):
    ret = []
    for path in paths:
        ret.append(read_photo(height, width, path))
    return ret 

def read_photo(height, width, path):
    i = Image.open(path)
    i = i.resize((width, height))
    pixels = i.load() 
    width, height = i.size
    img = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(pixels[x, y])
        img.append(row)
    i.show
    return img


def get_screen_size_char():
    return os.get_terminal_size()

def get_ascii_char(val: int):
    ascii_len = len(ASCII_CHARS)
    print(val)
    idx = math.floor((val/255) * ascii_len) - 1
    print(idx)
    ret = ASCII_CHARS[idx]
    return ret

def get_ascii_frame(img: [[(int, int, int)]]):
    frame = []
    for row in img:
        frame_row = []
        for pixel in row:
            frame_row.append(get_ascii_char(get_grey_scale(pixel)))
        frame.append(frame_row)
    return frame 
        
def get_grey_scale(pixel: (int, int, int)):
    return math.floor(.3 * pixel[0] + .59 * pixel[1] + .11 * pixel[2])

def print_frame(frame, width):
    print_msg = ""
    for row in frame:
        print_row = ""
        for char in row: 
            print_row += char
        print_row = print_row[:width]
        print_row += "\n"
        print_msg += print_row
        
    clear_console()
    sys.stdout.write(print_msg)

def clear_console(): 
    if os.name == 'nt':  
        os.system('cls')
    else:  
        sys.stdout.write("\033c")

if __name__ == '__main__': 
    animation()

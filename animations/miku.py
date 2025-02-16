from PIL import Image
import os
import sys
import math
from time import sleep
ASCII_CHARS = "@%#*+=-:. "

ANIMATION_DIRS_AND_TIMES = {"mining" : [.5, True]} 
TEXTS = {"mining" : "text/miningmsg.txt"}

def get_frame():
    pass 

def animate(name):
    assert name in ANIMATION_DIRS_AND_TIMES 
    frames_src = os.listdir(name + "/") 
    for i, frame_src in enumerate(frames_src):
        frames_src[i] = name + "/" + frame_src
        
    frames_src.sort()

    #determines
    text = []
    minus_line_space = 2
    if name in TEXTS: 
        text = get_text(TEXTS[name])
        minus_line_space += len(text)

    frames = []

    screen_size = get_screen_size_char()

    #if we dont have space dont play video
    if screen_size.lines - minus_line_space < 0:
        return

    imgs = read_photos(screen_size.lines - minus_line_space, screen_size.columns, frames_src)
    for img in imgs:
        frames.append(get_ascii_frame(img))

    for frame in frames:
        for line in text: 
            frame.append(line)

    cur_frame = 0
    dir = 1 
    delay = ANIMATION_DIRS_AND_TIMES[name][0]
    looping = ANIMATION_DIRS_AND_TIMES[name][1]

    while(True):
        sleep(delay)
        print_frame(frames[cur_frame], screen_size.columns)
        cur_frame += dir 

        if cur_frame < 0: 
            cur_frame = 1 
            dir = 1 

        if cur_frame >= 3:
            if looping:
                cur_frame = 1
                dir = -1 
            else:
                cur_frame = 0

def get_text(file_name): 
    text = []
    file = open(file_name, "r")
    for line in file:
        text.append(line[:len(line)-1])

    print(len(text)) 
    file.close()
    return text

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
    animate("mining")

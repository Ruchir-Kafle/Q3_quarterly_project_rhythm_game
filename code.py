import time
from random import randint
import board
from adafruit_clue import clue
from adafruit_debouncer import Debouncer
import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

font = bitmap_font.load_font('/Helvetica-Bold-36.bdf')
font.load_glyphs(b'0123456789XDd')
font_color = 0x0000FF

left_button = Debouncer(lambda: clue.button_a)
right_button = Debouncer(lambda: clue.button_b)

left_label = label.Label(font, x=80, y=220, text='a', color=font_color)
right_label = label.Label(font, x=140, y=220, text='b', color=font_color)

group = displayio.Group()
group.append(left_label)
group.append(right_label)

board.DISPLAY.root_group = group

notes = []

update_on_cooldown = False
note_spawn_on_cooldown = False

def update():
    global update_on_cooldown
    if not update_on_cooldown:
        update_on_cooldown = True
        for note in notes:
            note.x -= 20
        time.sleep(1000)
        update_on_cooldown = False

def spawn_note(type):
    global note_spawn_on_cooldown
    if not note_spawn_on_cooldown:
        note_spawn_on_cooldown = True
        note = label.Label(font, x=80, y=0, text='{type}', color=font_color)
        group.append(note)
        time.sleep(2000)
        note_spawn_on_cooldown = False

while True:
    left_button.update()
    right_button.update()

    if left_button.rose:
        print("a")
    elif right_button.rose:
        print("b")

    spawn_note("x")
    update()


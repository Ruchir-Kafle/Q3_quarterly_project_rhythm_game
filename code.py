import time
import asyncio
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

left_notes = []
right_notes = []
count = 0

update_on_cooldown = False
note_spawn_on_cooldown = False

async def update():
    while True:
        global update_on_cooldown
        if not update_on_cooldown:
            update_on_cooldown = True
            for note in left_notes:
                note.y += 1
            for note in right_notes:
                note.y += 1
            await asyncio.sleep(0.1)
            update_on_cooldown = False

async def spawn_note(type):
    while True:
        global note_spawn_on_cooldown, count
        if not note_spawn_on_cooldown:
            note_spawn_on_cooldown = True
            count += 1
            x_value = 80 if count % 2 == 0 else 140
            note = label.Label(font, x=x_value, y=0, text=f'{type}', color=font_color)
            left_notes.append(note) if x_value == 80 else right_notes.append(note)
            group.append(note)
            await asyncio.sleep(3)
            note_spawn_on_cooldown = False

async def main():
    await asyncio.gather(spawn_note("x"), update())

    while True:
        left_button.update()
        right_button.update()

        if left_button.rose:
            try:
                for i in range(1, 50):
                    print("save")
        elif right_button.rose:
            print("b")

if __name__ == "__main__":
    asyncio.run(main())

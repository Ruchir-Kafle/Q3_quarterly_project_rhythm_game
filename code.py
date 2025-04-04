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
blue = 0x0000FF
red = 0xFF0000
dark_green = 0x00FF00
gray = 0x808080
yellow = 0xFFFF00
orange = 0xFFA500

left_button = Debouncer(lambda: clue.button_a)
right_button = Debouncer(lambda: clue.button_b)

speed = 1
left_pos = 40
right_pos = 100
score_x_pos = 170

missed = 0
good = 0
great = 0
perfect = 0
perfect_plus = 0

left_label = label.Label(font, x=left_pos, y=220, text='a', color=red)
right_label = label.Label(font, x=right_pos, y=220, text='b', color=red)

missed_label = label.Label(font, x=score_x_pos, y=60, text='0', color=gray)
good_label = label.Label(font, x=score_x_pos, y=90, text='0', color=blue)
great_label = label.Label(font, x=score_x_pos, y=120, text='0', color=orange)
perfect_label = label.Label(font, x=score_x_pos, y=150, text='0', color=yellow)
perfect_plus_label = label.Label(font, x=score_x_pos, y=180, text='0', color=dark_green)

group = displayio.Group()
group.append(left_label)
group.append(right_label)
group.append(missed_label)
group.append(good_label)
group.append(great_label)
group.append(perfect_label)
group.append(perfect_plus_label)

board.DISPLAY.root_group = group

update_on_cooldown = False
note_spawn_on_cooldown = False

def score(note):
    global missed, good, great, perfect, perfect_plus
    if note.y < 250 and note.y >= 235:
        great += 1
    elif note.y < 235 and note.y >= 225:
        perfect += 1
    elif note.y < 225 and note.y >= 215:
        perfect_plus += 1
    elif note.y < 215 and note.y >= 200:
        perfect += 1
    elif note.y < 200 and note.y >= 170:
        great += 1
    elif note.y < 170 and note.y >= 130:
        good += 1
    else:
        missed += 1

def update_text():
    missed_label.text = str(missed)
    good_label.text = str(good)
    great_label.text = str(great)
    perfect_label.text = str(perfect)
    perfect_plus_label.text = str(perfect_plus)

def register_inputs(column_x):
    try:
        for i in range(0, 100):
            if group[i].x == column_x and group[i].text == "o":
                score(group[i])
                group.pop(i)
                break
    except IndexError:
        print("No notes in this column at the current moment.")

async def update_positions():
    while True:
        global update_on_cooldown, missed
        if not update_on_cooldown:
            update_on_cooldown = True

            for index, note in enumerate(group):
                if group[index].text == "o":
                    note.y += speed

                    if note.y >= 250:
                        missed += 1
                        group.pop(index)

            await asyncio.sleep(0.02)
            update_on_cooldown = False

async def spawn_note(type):
    count = 0
    while True:
        global note_spawn_on_cooldown
        if not note_spawn_on_cooldown:
            note_spawn_on_cooldown = True

            count += 1
            x_value = left_pos if count % 2 == 0 else right_pos
            note = label.Label(font, x=x_value, y=0, text=f'{type}', color=blue)
            group.append(note)

            await asyncio.sleep(1)
            note_spawn_on_cooldown = False

async def main():
    while True:
        left_button.update()
        right_button.update()

        if left_button.rose:
            register_inputs(left_pos)
        elif right_button.rose:
            register_inputs(right_pos)

        update_text()

        await asyncio.sleep(0.00001)

async def start():
    await asyncio.gather(spawn_note("o"), update_positions(), main())

if __name__ == "__main__":
    asyncio.run(start())

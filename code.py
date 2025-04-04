# Module imports.
# Most module imports are custom modules for the Adafruit CLUE.
import time
import asyncio
from random import randint
import board
from adafruit_clue import clue
from adafruit_debouncer import Debouncer
import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

# Defining default and global variables.
# Font info.
font = bitmap_font.load_font('/Helvetica-Bold-36.bdf')
font.load_glyphs(b'0123456789XDd')
blue = 0x0000FF
red = 0xFF0000
dark_green = 0x00FF00
gray = 0x808080
yellow = 0xFFFF00
orange = 0xFFA500

# Getting the CLUE's buttons.
left_button = Debouncer(lambda: clue.button_a)
right_button = Debouncer(lambda: clue.button_b)

# Note & score data/presets.
# Note speed.
speed = 1
# Posititioning variables.
left_pos = 40
right_pos = 100
score_x_pos = 170

# Score variables.
missed = 0
good = 0
great = 0
perfect = 0
perfect_plus = 0

# Initializing labels that are to be displayed upon the code first running.
# "Player" labels.
left_label = label.Label(font, x=left_pos, y=220, text='a', color=red)
right_label = label.Label(font, x=right_pos, y=220, text='b', color=red)

# Score labels.
missed_label = label.Label(font, x=score_x_pos, y=60, text='0', color=gray)
good_label = label.Label(font, x=score_x_pos, y=90, text='0', color=blue)
great_label = label.Label(font, x=score_x_pos, y=120, text='0', color=orange)
perfect_label = label.Label(font, x=score_x_pos, y=150, text='0', color=yellow)
perfect_plus_label = label.Label(font, x=score_x_pos, y=180, text='0', color=dark_green)

# Display group to display to the CLUE's digitial display.
group = displayio.Group()
group.append(left_label)
group.append(right_label)
group.append(missed_label)
group.append(good_label)
group.append(great_label)
group.append(perfect_label)
group.append(perfect_plus_label)

board.DISPLAY.root_group = group

# Debounces for respective functions.
update_on_cooldown = False
note_spawn_on_cooldown = False

# Scoring function.
# Depending on when the player clicks the buttons and thus plays a note, this function scores the user's timing
# relative to the "player" labels.
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

# Updates the score labels every frame so the player can see their performance.
def update_text():
    missed_label.text = str(missed)
    good_label.text = str(good)
    great_label.text = str(great)
    perfect_label.text = str(perfect)
    perfect_plus_label.text = str(perfect_plus)

# When the user makes an input, register and trigger/destroy the closest note to the bottom of the screen.
# Loop through every single note in the group.
# Try/except to prevent index errors as the for loop will attempt to loop through 101 items in group in total,
# 101 elements which may not even exist, thus leading to an index error.
# When looping through the group, the first note in the appropriate column will be scored and destroyed.
# Only the first note as notes are sequentially ordered in group and after the first is found, the loop is broken,
# preventing further iteration.
def register_inputs(column_x):
    try:
        for i in range(0, 100):
            if group[i].x == column_x and group[i].text == "o":
                score(group[i])
                group.pop(i)
                break
    except IndexError:
        print("No notes in this column at the current moment.")

# Async function to update positions of each note.
# Async to allow it to run independently of other functions.
# While loop keeps it running over and over again.
# Debounce prevents premature fires.
# For loop to iterate through every element in the group, apply velocity, and handle out-of-bounds notes.
# Sleeps to prevent overloading the processor and (more) accurately calculate velocity.
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

# Async function to spawn notes.
# Async to allow it to run independently of other functions.
# While loop keeps it running over and over again.
# Debounce prevents premature fires.
# Count and modulus to alternate the column which notes spawn in.
# Note is spawned through initialization of a label.Label object with text of the passed in symbol
# and displayed by appending to the displayio group.
# Sleeps to determine how often notes spawn.
async def spawn_note(symbol):
    count = 0
    while True:
        global note_spawn_on_cooldown
        if not note_spawn_on_cooldown:
            note_spawn_on_cooldown = True

            count += 1
            x_value = left_pos if count % 2 == 0 else right_pos
            note = label.Label(font, x=x_value, y=0, text=f'{symbol}', color=blue)
            group.append(note)

            await asyncio.sleep(1)
            note_spawn_on_cooldown = False

# Async function to handle user inputs.
# Async to allow it to run independently of other functions.
# While loop keeps it running over and over again.
# Gets user inputs and registers them accordingly.
# Updates text.
# Sleeps to prevent overloading the processor.
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

# Async function to run the 3 main blocks of code.
# Async to use the await keyword, which allows the running of other async functions.
# asyncio.gather allows various async functions to be ran in parallel,
# spawn_note, update_positions, and main being 3 functions that need to be ran independently of each other.
async def start():
    await asyncio.gather(spawn_note("o"), update_positions(), main())

# Starts the program; ensuring the program is being entered through the running of this file.
if __name__ == "__main__":
    asyncio.run(start())

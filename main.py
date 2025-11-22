import asyncio
import time
import random
import curses
from itertools import cycle

from curses_tools import draw_frame, get_frame_size, read_controls


TIC_TIMEOUT = 0.1


async def blink(canvas, row, column, symbol='*', offset_tics=0):
    """Display blinking star at given position."""

    for _ in range(offset_tics):
        await asyncio.sleep(0)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, row, column, frames):
    """Animate spaceship with given frames at specified position."""
    tick = 0
    frames_cycle = cycle(frames)
    current_frame = next(frames_cycle)

    while True:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        row += rows_direction
        column += columns_direction

        frame_rows, frame_columns = get_frame_size(current_frame)
        max_row, max_column = canvas.getmaxyx()
        max_row -= frame_rows + 1
        max_column -= frame_columns + 1

        row = max(1, min(row, max_row))
        column = max(1, min(column, max_column))

        if tick % 2 == 0:
            current_frame = next(frames_cycle)
        tick += 1

        draw_frame(canvas, row, column, current_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, current_frame, negative=True)


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    canvas.border()
    
    height, width = canvas.getmaxyx()
    center_row, center_column = height // 2, width // 2

    with open("rocket_frame_1.txt") as file:
        frame1 = file.read()
    with open("rocket_frame_2.txt") as file:
        frame2 = file.read()
        
    frames = [frame1, frame2]
    
    ship_rows, ship_columns = get_frame_size(frame1)
    ship_row = center_row - ship_rows // 2
    ship_column = center_column - ship_columns // 2

    coroutines = []
    coroutines.append(animate_spaceship(canvas, ship_row, ship_column, frames))

    symbols = ['+', '*', '.', ':']
    stars = random.randint(100, 200)

    shot = fire(canvas, center_row, center_column)
    coroutines.append(shot)

    for _ in range(stars):
        row = random.randint(1, height - 2)
        column = random.randint(1, width - 2)
        symbol = random.choice(symbols)
        offset = random.randint(0, 20)

        coroutine = blink(canvas, row, column, symbol, offset_tics=offset)
        coroutines.append(coroutine)

    while True:
        for coroutine in coroutines[:]:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == "__main__":
    main()

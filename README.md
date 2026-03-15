# Turtle Animator

A command-line Python turtle animator. Run scripts, type live commands, or
launch built-in demos — all from your terminal. A Tkinter window opens
automatically to display the animation.

No dependencies beyond the Python standard library.

---

## Requirements

- Python 3.8 or later
- Tkinter (bundled with most Python distributions; on some Linux systems
  install `python3-tk` separately)

---

## Quick start

```bash
python main.py                    # open the interactive REPL
python main.py spiral.py          # run your own script
python main.py --demo fern        # launch a built-in demo
python main.py --list             # list all built-in demos
```

---

## Command-line options

| Flag | Default | Description |
|---|---|---|
| `--speed N` | `6` | Turtle speed 1–10 (0 = instant) |
| `--width N` | `800` | Window width in pixels |
| `--height N` | `600` | Window height in pixels |
| `--bg COLOR` | `black` | Background colour (name or hex) |
| `--demo NAME` | — | Run a built-in demo |
| `--list` | — | Print available demo names |

Examples:

```bash
python main.py --speed 0 --demo spiral
python main.py --bg "#1a1a2e" --width 1000 --height 800 my_art.py
python main.py --demo tree --speed 0 --bg "#0d1b2a"
```

---

## Interactive REPL

Start with no arguments to enter the live REPL. The turtle window opens on
your first command and persists between inputs.

```
$ python main.py
Turtle Animator REPL  |  type 'help' for commands, 'quit' to exit
Window will open on first command.

>>> t.forward(100)
>>> t.right(90)
>>> t.forward(100)
```

### Drawing commands

Any Python expression or statement is valid. The turtle `t` and `screen`
are pre-loaded along with common math functions.

```
>>> t.color("cyan"); t.circle(80)
>>> for i in range(36): t.forward(100); t.right(170)
>>> t.write("hello", font=("Arial", 24, "bold"))
>>> screen.bgcolor("navy")
```

### Multiline blocks

End a block with a **blank line**:

```
>>> for i in range(6):
...     t.forward(100 + i * 10)
...     t.right(60)
...
```

```
>>> def star(n, size):
...     for _ in range(n):
...         t.forward(size)
...         t.right(360 / n * 2)
...
>>> star(7, 120)
```

### Built-in REPL commands

| Command | Description |
|---|---|
| `help` | Show command reference |
| `clear` | Clear the canvas |
| `reset` | Reset turtle to home position |
| `demos` | List available demo scripts |
| `run <name>` | Run a built-in demo by name |
| `run <file.py>` | Run any `.py` script file |
| `quit` / `exit` | Exit the REPL |

---

## Writing scripts

Scripts are plain Python files. You do **not** import turtle — the
objects `t` (turtle) and `screen` are injected automatically, along with
a set of math helpers.

### Pre-injected names

| Name | Value |
|---|---|
| `t`, `turtle` | The `Turtle` drawing object |
| `screen` | The `Screen` object |
| `clear()` | Clear canvas and update |
| `reset()` | Reset turtle to home and update |
| `update()` | `screen.update` — call to flush drawing |
| `math` | The `math` module |
| `sin`, `cos`, `tan` | `math.sin`, `math.cos`, `math.tan` |
| `pi`, `tau` | `math.pi`, `math.tau` |
| `sqrt`, `hypot` | `math.sqrt`, `math.hypot` |
| `floor`, `ceil` | `math.floor`, `math.ceil` |
| `radians`, `degrees` | `math.radians`, `math.degrees` |
| `random` | The `random` module |

> **Note:** `screen.tracer(0)` is set on startup. Always call
> `screen.update()` at the end of your script (or periodically inside
> loops) to flush the drawing to the window.

### Minimal script

```python
# hello.py
screen.bgcolor("midnightblue")
t.speed(0)
t.color("white")

for i in range(72):
    t.forward(200)
    t.right(175)

screen.update()
```

Run it:

```bash
python main.py hello.py
```

### HSV colour helper

Because turtle accepts RGB tuples (0–1 range), a small HSV helper is
useful for colour-cycling effects:

```python
# rainbow_spiral.py
def hsv(h, s=1, v=1):
    i = int(h * 6)
    f = h * 6 - i
    p, q, w = v*(1-s), v*(1-f*s), v*(1-(1-f)*s)
    return [(v,w,p),(q,v,p),(p,v,w),(p,q,v),(w,p,v),(v,p,q)][i % 6]

t.speed(0)
t.width(2)

for n in range(360):
    t.pencolor(*hsv(n / 360))
    t.forward(n * 0.6)
    t.right(89)

screen.update()
```

### Parametric curves

```python
# lissajous.py
import math as _math

screen.bgcolor("black")
t.speed(0)
t.width(1.5)

STEPS = 2000
A, B = 3, 2          # frequency ratio
DELTA = _math.pi / 4 # phase

t.penup()
for i in range(STEPS + 1):
    angle = i * tau / STEPS
    x = 280 * sin(A * angle + DELTA)
    y = 220 * sin(B * angle)
    hue = i / STEPS
    t.pencolor(*[
        (v, w, p)
        for h6 in [hue * 6]
        for i6 in [int(h6)]
        for f in [h6 - i6]
        for p, q, v, w in [(0, 1-f, 1, 1-f)]
    ][0][::-1][:3])  # simple cycling colour
    if i == 0:
        t.goto(x, y); t.pendown()
    else:
        t.goto(x, y)

screen.update()
```

### Animated patterns

Because `screen.tracer(0)` disables automatic redraws, you control
exactly when the screen updates — allowing smooth frame-by-frame
animation:

```python
# pulse.py  — expanding / contracting rings
import time as _time

screen.bgcolor("black")
t.hideturtle()
t.speed(0)

frame = 0
while True:
    t.clear()
    for ring in range(8):
        radius = 20 + ring * 30 + (frame % 30)
        brightness = 1.0 - ring / 8
        t.penup()
        t.goto(0, -radius)
        t.pendown()
        t.pencolor(0, brightness * 0.6, brightness)
        t.circle(radius)
    screen.update()
    _time.sleep(1 / 30)
    frame += 1
```

---

## Built-in demos

Run any demo with `python main.py --demo <name>`:

| Demo | Description |
|---|---|
| `spiral` | Colour HSV spiral — 500 steps of forward + right(91) with cycling hue |
| `tree` | Recursive fractal tree — 8 levels deep with green colour gradient |
| `star` | Layered geometric stars — 5 overlapping star polygons in different colours |
| `clock` | Live analogue clock — redraws every second using `time.localtime()` |
| `fern` | Barnsley fern — 90 000-point IFS chaos game; the fern shape emerges from random dots |

---

## Examples in depth

### spiral.py — HSV colour spiral

The turtle steps forward an increasing distance and turns 91°, tracing an
outward spiral. Colour cycles through the full hue wheel using an inline
HSV-to-RGB conversion.

```python
def hsv(h, s=1, v=1):
    i = int(h * 6)
    f = h * 6 - i
    p, q, tv = v*(1-s), v*(1-f*s), v*(1-(1-f)*s)
    return [(v,tv,p),(q,v,p),(p,v,tv),(p,q,v),(tv,p,v),(v,p,q)][i%6]

for n in range(500):
    t.pencolor(*hsv(n / 500))
    t.forward(n * 0.4)
    t.right(91)
```

### tree.py — recursive fractal tree

Each recursive call draws one branch, splits left and right by 50°
total, and shortens the branch length by 30% per level. Colour shifts
from dark brown at the base to bright green at the tips.

```python
def branch(length, depth):
    if depth == 0:
        return
    green = depth / 8
    t.pencolor(0.2 + green * 0.3, green, 0.1)
    t.width(depth * 0.8)
    t.forward(length)
    t.left(25);  branch(length * 0.7, depth - 1)
    t.right(50); branch(length * 0.7, depth - 1)
    t.left(25)
    t.backward(length)

branch(110, 8)
```

### fern.py — Barnsley fern (IFS chaos game)

The Barnsley fern is defined by four affine transformations applied at
random with fixed probabilities. Starting from any point, the sequence
of outputs converges to the fractal attractor — the fern shape — after
only a handful of iterations. 90 000 dots are plotted, coloured by
height (brownish stem → mid green → bright yellow-green tips).

```python
def ifs(x, y):
    r = random.random()
    if r < 0.01:
        return 0.0, 0.16 * y                                   # stem
    elif r < 0.86:
        return  0.85*x + 0.04*y,  -0.04*x + 0.85*y + 1.6     # leaflets
    elif r < 0.93:
        return  0.20*x - 0.26*y,   0.23*x + 0.22*y + 1.6     # left leaf
    else:
        return -0.15*x + 0.28*y,   0.26*x + 0.24*y + 0.44    # right leaf
```

The fern appears to "grow" from random noise as dots accumulate — the
animation is the convergence itself.

---

## Project structure

```
turtle-animator/
├── main.py          CLI entry point — argparse, routes to animator or REPL
├── animator.py      TurtleAnimator — sets up window, runs files and expressions
├── repl.py          TurtleREPL — interactive loop with built-in commands
├── examples/
│   ├── spiral.py    HSV colour spiral
│   ├── tree.py      Recursive fractal tree
│   ├── star.py      Layered geometric stars
│   ├── clock.py     Live analogue clock
│   └── fern.py      Barnsley fern (IFS chaos game)
└── tests/
    └── test_suite.py  Full stdlib test suite (unittest)
```

---

## Running the tests

```bash
python -m unittest tests/test_suite.py -v
```

No extra packages required.

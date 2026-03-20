# Turtle Animator — Lesson Plan

A progressive curriculum for learning Python through turtle graphics, from first
commands to animated fractals. Each lesson builds on the previous one.

---

## How to run the examples

**Locally (turtle-animator REPL):**
```bash
python main.py          # type commands live
python main.py --demo spiral
```

**Online (no install required):**
See the [Copy-Paste Workflow](#copy-paste-workflow-pythonsandboxcom) section at
the bottom of this file.

---

## Lesson 1 — First Steps

**Goal:** move the turtle, understand the coordinate system.

**Concepts:** `forward`, `backward`, `left`, `right`, `penup`, `pendown`

```python
t.forward(100)
t.right(90)
t.forward(100)
t.right(90)
t.forward(100)
t.right(90)
t.forward(100)

screen.update()
```

**Challenge:** draw a triangle (hint: exterior angles of a triangle sum to 360°).

---

## Lesson 2 — Loops

**Goal:** use `for` loops to avoid repetition.

**Concepts:** `range()`, loop variables, generalising patterns

```python
# Square with a loop
for _ in range(4):
    t.forward(100)
    t.right(90)

screen.update()
```

```python
# Regular polygon — change sides to make any shape
sides = 6
for _ in range(sides):
    t.forward(80)
    t.right(360 / sides)

screen.update()
```

**Challenge:** draw a circle by using 360 sides of length 2.

---

## Lesson 3 — Colour and Style

**Goal:** make drawings visually interesting.

**Concepts:** `pencolor`, `fillcolor`, `begin_fill`/`end_fill`, `width`, `hideturtle`

```python
t.hideturtle()
t.width(3)
t.pencolor("cyan")
t.fillcolor("navy")

t.begin_fill()
for _ in range(5):
    t.forward(120)
    t.right(144)      # 360 / 5 * 2 for a star
t.end_fill()

screen.update()
```

```python
# RGB colour — values are 0.0 to 1.0
screen.colormode(1.0)
t.pencolor(1.0, 0.5, 0.0)   # orange
t.circle(80)

screen.update()
```

**Challenge:** draw a row of five circles, each a different colour.

---

## Lesson 4 — Functions

**Goal:** name and reuse drawing routines.

**Concepts:** `def`, parameters, calling functions multiple times

```python
def square(size):
    for _ in range(4):
        t.forward(size)
        t.right(90)

square(50)
t.penup(); t.forward(80); t.pendown()
square(80)
t.penup(); t.forward(120); t.pendown()
square(110)

screen.update()
```

```python
def polygon(sides, size):
    for _ in range(sides):
        t.forward(size)
        t.right(360 / sides)

for s in range(3, 9):
    polygon(s, 60)
    t.penup(); t.right(20); t.forward(80); t.pendown()

screen.update()
```

**Challenge:** write a `star(n, size)` function that draws an n-pointed star.

---

## Lesson 5 — Colour Cycling with HSV

**Goal:** cycle through rainbow colours programmatically.

**Concepts:** hue-saturation-value model, converting HSV → RGB

```python
def hsv(h, s=1, v=1):
    i = int(h * 6)
    f = h * 6 - i
    p, q, w = v*(1-s), v*(1-f*s), v*(1-(1-f)*s)
    return [(v,w,p),(q,v,p),(p,v,w),(p,q,v),(w,p,v),(v,p,q)][i % 6]

screen.colormode(1.0)
t.speed(0)
t.hideturtle()

for n in range(500):
    t.pencolor(*hsv(n / 500))
    t.forward(n * 0.4)
    t.right(91)

screen.update()
```

**Challenge:** slow the speed down and watch how the spiral forms step by step.

---

## Lesson 6 — Recursion

**Goal:** draw shapes that contain smaller versions of themselves.

**Concepts:** recursive functions, base case, depth parameter

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

t.speed(0)
t.hideturtle()
t.penup(); t.goto(0, -250); t.pendown(); t.left(90)
branch(110, 8)

screen.update()
```

**Challenge:** change the branch angle from 25° to 15° — what does the tree look like?

---

## Lesson 7 — Math and Coordinates

**Goal:** place the turtle precisely using trigonometry.

**Concepts:** `sin`, `cos`, `pi`, `goto`, parametric curves

```python
# Lissajous curve
t.speed(0)
t.hideturtle()
t.penup()

STEPS = 800
A, B = 3, 2
DELTA = pi / 4

for i in range(STEPS + 1):
    angle = i * tau / STEPS
    x = 250 * sin(A * angle + DELTA)
    y = 200 * sin(B * angle)
    if i == 0:
        t.goto(x, y); t.pendown()
    else:
        t.goto(x, y)

screen.update()
```

**Challenge:** change A and B to 5 and 4 — try other integer pairs.

---

## Lesson 8 — Randomness

**Goal:** use randomness to produce organic, unpredictable shapes.

**Concepts:** `random.random()`, probability distributions, chaos game

```python
# Barnsley fern (simplified — 30 000 points)
def ifs(x, y):
    r = random.random()
    if r < 0.01:   return 0.0, 0.16 * y
    elif r < 0.86: return  0.85*x + 0.04*y, -0.04*x + 0.85*y + 1.6
    elif r < 0.93: return  0.20*x - 0.26*y,  0.23*x + 0.22*y + 1.6
    else:          return -0.15*x + 0.28*y,  0.26*x + 0.24*y + 0.44

t.speed(0); t.hideturtle(); t.penup()
screen.colormode(1.0)
SCALE = 50
x, y = 0.0, 0.0

for _ in range(30000):
    x, y = ifs(x, y)
    t.goto(x * SCALE, y * SCALE - 250)
    frac = min(y / 10, 1.0)
    t.dot(2, (0.1, 0.4 + 0.4 * frac, 0.1))

screen.update()
```

**Challenge:** increase to 90 000 points — notice how the fern becomes sharper.

---

## Lesson 9 — Animation

**Goal:** build a live animation loop using `screen.tracer(0)`.

**Concepts:** animation loop, `t.clear()`, `screen.update()`, frame rate control

```python
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

> **Note:** this loop runs forever — press Ctrl+C in the terminal to stop.

**Challenge:** change the rings to squares or spirals.

---

## Summary Table

| Lesson | Key Skill | Demo to run |
|---|---|---|
| 1 | Basic movement | (type in REPL) |
| 2 | Loops | (type in REPL) |
| 3 | Colour & fill | `--demo star` |
| 4 | Functions | (type in REPL) |
| 5 | HSV colour cycling | `--demo spiral` |
| 6 | Recursion | `--demo tree` |
| 7 | Trig & coordinates | (paste script) |
| 8 | Randomness | `--demo fern` |
| 9 | Animation | `--demo clock` |

---

## Copy-Paste Workflow — pythonsandbox.com

Use these workflows when you don't have Python installed locally, or want to
share a sketch with someone via a URL.

### pythonsandbox.com/turtle

This sandbox supports the `turtle` module. Because turtle-animator pre-injects
`t`, `screen`, and math helpers, you need to add a short preamble when pasting
a script there.

**Preamble — paste this at the top of every script:**

```python
import turtle
import math
import random
from math import sin, cos, tan, pi, tau, sqrt, hypot, floor, ceil, radians, degrees

screen = turtle.Screen()
screen.colormode(1.0)
screen.tracer(0)
t = turtle.Turtle()
t.speed(0)
```

**Then paste your lesson code below the preamble.**

**After the drawing code, end with:**

```python
screen.update()
turtle.done()
```

**Full example — Lesson 5 spiral on pythonsandbox.com/turtle:**

```python
import turtle
import math
import random
from math import sin, cos, tan, pi, tau, sqrt, hypot, floor, ceil, radians, degrees

screen = turtle.Screen()
screen.colormode(1.0)
screen.tracer(0)
t = turtle.Turtle()
t.speed(0)
t.hideturtle()

# --- lesson code ---
def hsv(h, s=1, v=1):
    i = int(h * 6)
    f = h * 6 - i
    p, q, w = v*(1-s), v*(1-f*s), v*(1-(1-f)*s)
    return [(v,w,p),(q,v,p),(p,v,w),(p,q,v),(w,p,v),(v,p,q)][i % 6]

for n in range(500):
    t.pencolor(*hsv(n / 500))
    t.forward(n * 0.4)
    t.right(91)
# --- end lesson code ---

screen.update()
turtle.done()
```

---

### pythonsandbox.com/text

This sandbox runs standard Python with text output — no graphics window.
Use it for experimenting with the pure-Python logic (math, loops, functions)
before wiring it to the turtle.

**What works here:**
- Lessons 1–4 logic (without drawing calls)
- The `hsv()` function — print colour tuples
- The `ifs()` fern function — print coordinates
- Any pure calculation you want to test

**Example — verify the fern transform logic:**

```python
import random

def ifs(x, y):
    r = random.random()
    if r < 0.01:   return 0.0, 0.16 * y
    elif r < 0.86: return  0.85*x + 0.04*y, -0.04*x + 0.85*y + 1.6
    elif r < 0.93: return  0.20*x - 0.26*y,  0.23*x + 0.22*y + 1.6
    else:          return -0.15*x + 0.28*y,  0.26*x + 0.24*y + 0.44

x, y = 0.0, 0.0
for _ in range(10):
    x, y = ifs(x, y)
    print(f"x={x:.3f}  y={y:.3f}")
```

**Example — verify the HSV function returns valid RGB:**

```python
def hsv(h, s=1, v=1):
    i = int(h * 6)
    f = h * 6 - i
    p, q, w = v*(1-s), v*(1-f*s), v*(1-(1-f)*s)
    return [(v,w,p),(q,v,p),(p,v,w),(p,q,v),(w,p,v),(v,p,q)][i % 6]

for step in range(7):
    h = step / 6
    r, g, b = hsv(h)
    print(f"h={h:.2f}  →  r={r:.2f} g={g:.2f} b={b:.2f}")
```

---

### Quick reference — what changes between environments

| | turtle-animator (local) | pythonsandbox.com/turtle | pythonsandbox.com/text |
|---|---|---|---|
| `t` available | yes (pre-injected) | add preamble | no |
| `screen` available | yes (pre-injected) | add preamble | no |
| math helpers | yes (pre-injected) | add preamble import | import manually |
| `screen.tracer(0)` | set on startup | set in preamble | n/a |
| End with | `screen.update()` | `screen.update()` + `turtle.done()` | nothing |
| Infinite loops | Ctrl+C to stop | avoid — sandbox will time out | avoid |

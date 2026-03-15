# Barnsley Fern — IFS chaos game
#
# Four affine transformations (the "Iterated Function System") are applied
# at random with fixed probabilities.  After a warm-up, every point lands
# on the fractal attractor, so the fern shape emerges from apparent chaos.
#
# Colour gradient: brownish stem → mid green fronds → bright yellow-green tips.

import random as _random

screen.bgcolor("black")
screen.tracer(0)
t.hideturtle()
t.penup()

SCALE     = 57       # world-units → pixels
OFFSET_Y  = -295     # shift so the fern sits just above screen bottom
ITERATIONS = 90000
BATCH      = 400     # dots drawn between each screen.update()


def ifs(x, y):
    """Pick one of four affine maps by probability and apply it."""
    r = _random.random()
    if r < 0.01:                          # f1 — stem
        return 0.0,  0.16 * y
    elif r < 0.86:                        # f2 — successively smaller leaflets
        return  0.85 * x + 0.04 * y,  -0.04 * x + 0.85 * y + 1.6
    elif r < 0.93:                        # f3 — left leaf
        return  0.20 * x - 0.26 * y,   0.23 * x + 0.22 * y + 1.6
    else:                                 # f4 — right leaf
        return -0.15 * x + 0.28 * y,   0.26 * x + 0.24 * y + 0.44


def fern_color(y):
    """Map world-space height (0–10) to an RGB tuple."""
    h = max(0.0, min(y / 10.0, 1.0))
    r = 0.25 * (1.0 - h)          # slight warmth near the base
    g = 0.35 + 0.55 * h           # green intensifies toward the tip
    b = 0.05
    return r, g, b


x, y = 0.0, 0.0

for i in range(ITERATIONS):
    x, y = ifs(x, y)

    # Skip the first few points — they may not yet be on the attractor.
    if i < 20:
        continue

    t.goto(x * SCALE, y * SCALE + OFFSET_Y)
    t.pencolor(*fern_color(y))
    t.dot(2)

    if i % BATCH == 0:
        screen.update()

screen.update()

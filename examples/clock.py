# Analogue clock (live)
import time as _time

screen.bgcolor("black")
screen.tracer(0)

def hand(length, angle, width, color):
    t.penup(); t.goto(0, 0)
    t.setheading(90 - angle)
    t.pendown()
    t.width(width)
    t.pencolor(color)
    t.forward(length)

def face():
    t.hideturtle()
    t.pencolor("#333")
    t.width(1)
    for i in range(60):
        a = i * 6
        r = 170 if i % 5 == 0 else 175
        t.penup()
        t.goto(r * sin(radians(a)), r * cos(radians(a)))
        t.pendown()
        t.dot(6 if i % 5 == 0 else 2, "#aaa" if i % 5 == 0 else "#444")

face()

while True:
    t.clear()
    face()
    n = _time.localtime()
    h, m, s = n.tm_hour % 12, n.tm_min, n.tm_sec

    hand(90,  h * 30 + m * 0.5,  5, "#eee")
    hand(130, m * 6,              3, "#ccc")
    hand(150, s * 6,              1, "#ff4081")
    t.penup(); t.goto(0, 0); t.dot(8, "#fff")

    screen.update()
    _time.sleep(1)

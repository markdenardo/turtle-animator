# Layered stars
screen.bgcolor("black")
t.speed(0)
t.hideturtle()

def star(points, size, color, angle_offset=0):
    t.pencolor(color)
    t.width(1.5)
    step = 360 / points
    t.penup()
    t.goto(0, 0)
    t.setheading(angle_offset)
    t.pendown()
    for _ in range(points * 2):
        t.forward(size)
        t.right(180 - 180 / points)

configs = [
    (5,  180, "gold"),
    (7,  140, "cyan"),
    (9,  100, "magenta"),
    (11,  60, "lime"),
    (13,  30, "white"),
]

for points, size, color in configs:
    star(points, size, color)

screen.update()

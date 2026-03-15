# Fractal tree
screen.bgcolor("black")
t.speed(0)
t.left(90)

def branch(length, depth):
    if depth == 0:
        return
    green = depth / 8
    t.pencolor(0.2 + green * 0.3, green, 0.1)
    t.width(depth * 0.8)
    t.forward(length)
    t.left(25)
    branch(length * 0.7, depth - 1)
    t.right(50)
    branch(length * 0.7, depth - 1)
    t.left(25)
    t.backward(length)

t.penup()
t.goto(0, -250)
t.pendown()
branch(110, 8)
screen.update()

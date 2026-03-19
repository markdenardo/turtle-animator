# Colour spiral
t.showturtle()
t.speed(0)
t.width(2)
screen.bgcolor("black")

def hsv(h, s=1, v=1):
    i = int(h * 6)
    f = h * 6 - i
    p, q, tv = v*(1-s), v*(1-f*s), v*(1-(1-f)*s)
    return [(v,tv,p),(q,v,p),(p,v,tv),(p,q,v),(tv,p,v),(v,p,q)][i%6]

for n in range(500):
    t.pencolor(*hsv(n / 500))
    t.forward(n * 0.4)
    t.right(91)

screen.update()

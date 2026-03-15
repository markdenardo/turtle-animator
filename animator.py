"""
animator.py
Wraps Python's turtle module with a clean execution environment.
"""
import turtle
import math
import random
import os


class TurtleAnimator:
    """Sets up a turtle window and executes scripts or expressions."""

    def __init__(self, width=800, height=600, bg="black", speed=6):
        self.width  = width
        self.height = height
        self.bg     = bg
        self.speed  = speed
        self._ready = False

    def _setup(self):
        if self._ready:
            return
        screen = turtle.Screen()
        screen.setup(width=self.width, height=self.height)
        screen.bgcolor(self.bg)
        screen.title("Turtle Animator")
        screen.tracer(0)          # manual update for smooth animation
        self._screen = screen
        self._ready  = True

    def _make_globals(self, t: turtle.Turtle) -> dict:
        """Build the execution namespace injected into user scripts."""
        screen = self._screen
        return {
            # turtle object
            "t":       t,
            "turtle":  t,
            # screen helpers
            "screen":  screen,
            "clear":   lambda: (t.clear(), screen.update()),
            "reset":   lambda: (t.reset(), t.speed(self.speed), screen.update()),
            "update":  screen.update,
            "done":    turtle.done,
            # math
            "math":    math,
            "random":  random,
            "sin":     math.sin,
            "cos":     math.cos,
            "tan":     math.tan,
            "pi":      math.pi,
            "tau":     math.tau,
            "sqrt":    math.sqrt,
            "floor":   math.floor,
            "ceil":    math.ceil,
            "radians": math.radians,
            "degrees": math.degrees,
            "hypot":   math.hypot,
            # builtins
            "range":   range,
            "print":   print,
            "abs":     abs,
            "int":     int,
            "float":   float,
            "round":   round,
            "min":     min,
            "max":     max,
            "len":     len,
            "list":    list,
            "enumerate": enumerate,
            "zip":     zip,
        }

    def run_file(self, path: str):
        """Execute a .py script in the animator environment."""
        path = os.path.abspath(path)
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return

        with open(path) as f:
            code = f.read()

        self._setup()
        t = turtle.Turtle()
        t.speed(self.speed)
        t.hideturtle()

        g = self._make_globals(t)

        try:
            exec(compile(code, path, "exec"), g)
            self._screen.update()
            print(f"Done. Close the window or press Ctrl+C to exit.")
            turtle.done()
        except turtle.Terminator:
            pass
        except KeyboardInterrupt:
            print("\nInterrupted.")
        except Exception as e:
            print(f"\nError: {e}")

    def run_expr(self, code: str, g: dict):
        """Execute a single expression or statement in an existing namespace."""
        try:
            # try eval first (returns a value)
            result = eval(compile(code, "<repl>", "eval"), g)
            if result is not None:
                print(repr(result))
        except SyntaxError:
            # fall back to exec for statements
            exec(compile(code, "<repl>", "exec"), g)
        self._screen.update()

    def new_turtle(self) -> turtle.Turtle:
        """Create and return a fresh turtle on the current screen."""
        self._setup()
        t = turtle.Turtle()
        t.speed(self.speed)
        t.hideturtle()
        return t

    def get_globals(self) -> dict:
        """Return a fresh globals dict for a REPL session."""
        self._setup()
        t = self.new_turtle()
        return self._make_globals(t)

"""
turtle-animator
A command-line tool for animating Python turtle graphics.

Usage:
    python main.py                    # interactive REPL
    python main.py script.py          # run a script file
    python main.py --demo spiral      # run a built-in demo
    python main.py --demo tree
    python main.py --demo star
    python main.py --demo clock
    python main.py --list             # list available demos
"""
import argparse
import sys
from animator import TurtleAnimator
from repl import TurtleREPL


DEMOS = {
    "spiral":  "examples/spiral.py",
    "tree":    "examples/tree.py",
    "star":    "examples/star.py",
    "clock":   "examples/clock.py",
    "fern":    "examples/fern.py",
}


def main():
    parser = argparse.ArgumentParser(
        prog="turtle-animator",
        description="Command-line Python turtle animator",
    )
    parser.add_argument(
        "script", nargs="?",
        help="Python script file to animate"
    )
    parser.add_argument(
        "--demo", metavar="NAME",
        help="Run a built-in demo (spiral, tree, star, clock)"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List available built-in demos"
    )
    parser.add_argument(
        "--speed", type=int, default=6, metavar="N",
        help="Turtle speed 1-10 (default: 6)"
    )
    parser.add_argument(
        "--width", type=int, default=800,
        help="Window width (default: 800)"
    )
    parser.add_argument(
        "--height", type=int, default=600,
        help="Window height (default: 600)"
    )
    parser.add_argument(
        "--bg", default="black",
        help="Background colour (default: black)"
    )

    args = parser.parse_args()

    if args.list:
        print("\nAvailable demos:")
        for name in DEMOS:
            print(f"  {name}")
        print(f"\nUsage: python main.py --demo <name>\n")
        return

    animator = TurtleAnimator(
        width=args.width,
        height=args.height,
        bg=args.bg,
        speed=args.speed,
    )

    if args.demo:
        if args.demo not in DEMOS:
            print(f"Unknown demo '{args.demo}'. Use --list to see options.")
            sys.exit(1)
        import os
        script_path = os.path.join(os.path.dirname(__file__), DEMOS[args.demo])
        animator.run_file(script_path)

    elif args.script:
        animator.run_file(args.script)

    else:
        # interactive REPL
        repl = TurtleREPL(animator)
        repl.run()


if __name__ == "__main__":
    main()

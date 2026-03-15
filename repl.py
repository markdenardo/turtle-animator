"""
repl.py
Interactive command-line REPL for the turtle animator.
Supports Python expressions, multiline blocks, and built-in commands.
"""
import sys
import turtle


HELP_TEXT = """
Turtle Animator — Interactive REPL
───────────────────────────────────
Type Python expressions or statements. turtle `t` is pre-loaded.

Built-in commands:
  help          Show this message
  clear         Clear the canvas
  reset         Reset turtle to home
  demos         List example scripts
  run <file>    Run a .py script file
  quit / exit   Exit

Examples:
  t.forward(100)
  t.color('cyan'); t.circle(80)
  for i in range(36): t.forward(100); t.right(170)
  t.write("hello", font=("Arial", 24, "bold"))

Multiline blocks: end with a blank line.
"""

DEMOS = ["spiral", "tree", "star", "clock", "fern"]


class TurtleREPL:
    def __init__(self, animator):
        self.animator = animator
        self._globals = None

    def _ensure_globals(self):
        if self._globals is None:
            self._globals = self.animator.get_globals()

    def run(self):
        print("Turtle Animator REPL  |  type 'help' for commands, 'quit' to exit")
        print("Window will open on first command.\n")

        buffer = []

        while True:
            prompt = "... " if buffer else ">>> "
            try:
                line = input(prompt)
            except (EOFError, KeyboardInterrupt):
                print("\nBye.")
                break

            # --- built-in commands (only at top level) ---
            stripped = line.strip()

            if not buffer:
                if stripped in ("quit", "exit"):
                    print("Bye.")
                    break

                if stripped == "help":
                    print(HELP_TEXT)
                    continue

                if stripped == "demos":
                    print("Available demos: " + ", ".join(DEMOS))
                    print("Run with: run <name>  or  python main.py --demo <name>")
                    continue

                if stripped.startswith("run "):
                    import os
                    arg  = stripped[4:].strip()
                    # check built-in demo names
                    demo_paths = {
                        d: os.path.join(os.path.dirname(__file__), "examples", f"{d}.py")
                        for d in DEMOS
                    }
                    path = demo_paths.get(arg, arg)
                    self.animator.run_file(path)
                    # reset globals after file run (new turtle state)
                    self._globals = None
                    continue

                if stripped == "clear":
                    self._ensure_globals()
                    self._globals["clear"]()
                    continue

                if stripped == "reset":
                    self._ensure_globals()
                    self._globals["reset"]()
                    continue

                if stripped == "":
                    continue

            # --- multiline block handling ---
            if stripped == "" and buffer:
                # blank line ends a block
                code = "\n".join(buffer)
                buffer = []
                self._execute(code)
                continue

            # detect block starters (def, for, while, if, with, class, try)
            if stripped.endswith(":") or buffer:
                buffer.append(line)
                continue

            # single line
            self._execute(line)

    def _execute(self, code: str):
        self._ensure_globals()
        try:
            self.animator.run_expr(code, self._globals)
        except turtle.Terminator:
            print("Window closed. Reopen by typing any command.")
            self._globals = None
        except SystemExit:
            raise
        except Exception as e:
            print(f"Error: {e}")

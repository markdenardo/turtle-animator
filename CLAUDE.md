# Claude Code — Project Instructions: Turtle Animator

A command-line Python turtle animator. No browser, no server — pure terminal + Tkinter window.

---

## What this project is

Users run scripts or type Python commands in a terminal REPL. A Tkinter window opens showing
the turtle animation. Scripts are executed with `t` (turtle) and `screen` pre-injected, plus
math helpers available without import.

---

## Project structure

```
turtle-animator/
├── main.py          CLI entry point — argparse, routes to animator or REPL
├── animator.py      TurtleAnimator — sets up window, runs files, executes expressions
├── repl.py          TurtleREPL — interactive loop with built-in commands
├── examples/
│   ├── spiral.py
│   ├── tree.py
│   ├── star.py
│   └── clock.py
└── README.md
```

---

## Usage

```bash
python main.py                    # interactive REPL
python main.py script.py          # run a script file
python main.py --demo spiral      # built-in demo
python main.py --list             # list demos
python main.py --speed 10 --bg navy --demo tree
```

---

## Key invariants

- `screen.tracer(0)` is set on init — always call `screen.update()` at end of scripts
- `t` and `screen` are injected into all execution namespaces — scripts do not import turtle
- Math helpers (`sin`, `cos`, `pi`, `tau`, `sqrt`, `radians`, `degrees`) are pre-injected
- The REPL detects multiline blocks by trailing `:` — blank line ends the block

---

## Contributor rules

- Conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`
- Do not add `Co-Authored-By` lines to commits
- No dependencies beyond stdlib — turtle is built-in

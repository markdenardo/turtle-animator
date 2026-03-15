"""
tests/test_suite.py
Comprehensive test suite for turtle-animator.
Requires only the stdlib: unittest + unittest.mock.

Because turtle requires Tkinter (which may be unavailable in headless
environments), the entire `turtle` module is replaced with a MagicMock
in sys.modules before any project code is imported.
"""
import io
import math
import os
import sys
import tempfile
import unittest
from contextlib import contextmanager, redirect_stdout
from unittest.mock import MagicMock, patch, call

# ---------------------------------------------------------------------------
# Mock the turtle module globally before importing any project code.
# We keep the real Terminator class so exception handling can be tested.
# ---------------------------------------------------------------------------
class _FakeTerminator(Exception):
    """Stand-in for turtle.Terminator."""

_mock_turtle_module = MagicMock()
_mock_turtle_module.Terminator = _FakeTerminator
sys.modules["turtle"] = _mock_turtle_module

# Ensure project root is importable when run from the tests/ directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from animator import TurtleAnimator
from repl import TurtleREPL


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

@contextmanager
def patch_turtle():
    """
    Reset the mock turtle module's Screen / Turtle / done attributes for a
    single test, yielding (mock_screen_instance, mock_turtle_instance).
    """
    mock_screen = MagicMock(name="screen")
    mock_turtle_obj = MagicMock(name="turtle_obj")
    _mock_turtle_module.Screen.return_value = mock_screen
    _mock_turtle_module.Turtle.return_value = mock_turtle_obj
    _mock_turtle_module.done.reset_mock()
    yield mock_screen, mock_turtle_obj


def make_ready_animator(**kwargs):
    """Return a TurtleAnimator with _ready=True and a mock _screen."""
    anim = TurtleAnimator(**kwargs)
    anim._screen = MagicMock(name="screen")
    anim._ready = True
    return anim


def run_repl_with_inputs(repl, lines):
    """
    Drive repl.run() by feeding *lines* one at a time; raises EOFError
    once the list is exhausted so the loop exits cleanly.
    Returns captured stdout.
    """
    it = iter(lines)

    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError

    buf = io.StringIO()
    with patch("builtins.input", side_effect=fake_input), redirect_stdout(buf):
        repl.run()
    return buf.getvalue()


# ---------------------------------------------------------------------------
# 1. TurtleAnimator — __init__
# ---------------------------------------------------------------------------

class TestTurtleAnimatorInit(unittest.TestCase):

    def test_defaults_stored(self):
        anim = TurtleAnimator()
        self.assertEqual(anim.width, 800)
        self.assertEqual(anim.height, 600)
        self.assertEqual(anim.bg, "black")
        self.assertEqual(anim.speed, 6)
        self.assertFalse(anim._ready)

    def test_custom_params_stored(self):
        anim = TurtleAnimator(width=400, height=300, bg="navy", speed=2)
        self.assertEqual(anim.width, 400)
        self.assertEqual(anim.height, 300)
        self.assertEqual(anim.bg, "navy")
        self.assertEqual(anim.speed, 2)

    def test_ready_flag_false_and_no_screen_before_setup(self):
        anim = TurtleAnimator()
        self.assertFalse(anim._ready)
        self.assertFalse(hasattr(anim, "_screen"))


# ---------------------------------------------------------------------------
# 2. TurtleAnimator — _setup
# ---------------------------------------------------------------------------

class TestTurtleAnimatorSetup(unittest.TestCase):

    def test_setup_configures_screen(self):
        anim = TurtleAnimator()
        with patch_turtle() as (mock_screen, _):
            anim._setup()
        self.assertTrue(anim._ready)
        self.assertIs(anim._screen, mock_screen)
        mock_screen.setup.assert_called_once_with(width=800, height=600)
        mock_screen.bgcolor.assert_called_once_with("black")
        mock_screen.title.assert_called_once_with("Turtle Animator")
        mock_screen.tracer.assert_called_once_with(0)

    def test_setup_is_idempotent(self):
        """_setup() called twice must not create a second Screen instance."""
        _mock_turtle_module.Screen.reset_mock()
        _mock_turtle_module.Screen.return_value = MagicMock()
        anim = TurtleAnimator()
        anim._setup()
        anim._setup()
        _mock_turtle_module.Screen.assert_called_once()

    def test_setup_uses_instance_config(self):
        anim = TurtleAnimator(width=1024, height=768, bg="navy")
        with patch_turtle() as (mock_screen, _):
            anim._setup()
        mock_screen.setup.assert_called_once_with(width=1024, height=768)
        mock_screen.bgcolor.assert_called_once_with("navy")


# ---------------------------------------------------------------------------
# 3. TurtleAnimator — _make_globals
# ---------------------------------------------------------------------------

class TestMakeGlobals(unittest.TestCase):

    def setUp(self):
        self.anim = make_ready_animator()
        self.mock_t = MagicMock(name="turtle_obj")
        self.g = self.anim._make_globals(self.mock_t)

    def test_turtle_keys_present(self):
        self.assertIs(self.g["t"], self.mock_t)
        self.assertIs(self.g["turtle"], self.mock_t)

    def test_screen_key_present(self):
        self.assertIs(self.g["screen"], self.anim._screen)

    def test_math_helpers_present(self):
        cases = {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "floor": math.floor, "ceil": math.ceil,
            "radians": math.radians, "degrees": math.degrees,
            "hypot": math.hypot, "math": math,
            "pi": math.pi, "tau": math.tau,
        }
        for name, expected in cases.items():
            with self.subTest(name=name):
                self.assertEqual(self.g[name], expected)

    def test_builtins_explicitly_present(self):
        """All explicitly injected builtins must exist by name in the dict."""
        for name in ("range", "print", "abs", "int", "float", "round",
                     "min", "max", "len", "list", "enumerate", "zip"):
            with self.subTest(builtin=name):
                self.assertIn(name, self.g)

    def test_no_implicit_builtins_key(self):
        """_make_globals must not inject __builtins__ (allowlist design)."""
        self.assertNotIn("__builtins__", self.g)

    def test_clear_callable_invokes_turtle_and_screen(self):
        self.g["clear"]()
        self.mock_t.clear.assert_called_once()
        self.anim._screen.update.assert_called_once()

    def test_reset_callable_applies_speed(self):
        self.g["reset"]()
        self.mock_t.reset.assert_called_once()
        self.mock_t.speed.assert_called_with(self.anim.speed)
        self.anim._screen.update.assert_called_once()

    def test_update_is_screen_update(self):
        self.assertIs(self.g["update"], self.anim._screen.update)


# ---------------------------------------------------------------------------
# 4. TurtleAnimator — run_expr
# ---------------------------------------------------------------------------

class TestRunExpr(unittest.TestCase):

    def setUp(self):
        self.anim = make_ready_animator()
        # Provide __builtins__ so exec inside run_expr can freely use them.
        self.g = {"__builtins__": __builtins__}

    def test_eval_path_prints_result(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.anim.run_expr("1 + 1", self.g)
        self.assertIn("2", buf.getvalue())
        self.anim._screen.update.assert_called_once()

    def test_eval_none_result_not_printed(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.anim.run_expr("None", self.g)
        self.assertEqual(buf.getvalue(), "")

    def test_exec_path_statement(self):
        """Assignment falls back to exec; result must be stored in g."""
        self.anim.run_expr("x = 42", self.g)
        self.assertEqual(self.g["x"], 42)

    def test_screen_update_called_after_exec(self):
        self.anim.run_expr("pass", self.g)
        self.anim._screen.update.assert_called_once()

    def test_multiline_exec(self):
        # Flushed multiline block joined by newline must run without error.
        self.anim.run_expr("for i in range(3):\n    pass", self.g)

    def test_syntax_error_propagates(self):
        with self.assertRaises(SyntaxError):
            self.anim.run_expr("def (", self.g)


# ---------------------------------------------------------------------------
# 5. TurtleAnimator — run_file
# ---------------------------------------------------------------------------

class TestRunFile(unittest.TestCase):

    def _make_tmp(self, content):
        f = tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", delete=False, encoding="utf-8"
        )
        f.write(content)
        f.close()
        return f.name

    def test_file_not_found_prints_message(self):
        anim = TurtleAnimator()
        buf = io.StringIO()
        with redirect_stdout(buf):
            anim.run_file("/nonexistent/path/__xyz_does_not_exist__.py")
        self.assertIn("File not found", buf.getvalue())

    def test_file_executes_and_prints_done(self):
        path = self._make_tmp("x = 7 * 6\n")
        try:
            with patch_turtle():
                anim = TurtleAnimator()
                buf = io.StringIO()
                with redirect_stdout(buf):
                    anim.run_file(path)
            self.assertIn("Done", buf.getvalue())
        finally:
            os.unlink(path)

    def test_file_calls_screen_and_done(self):
        path = self._make_tmp("pass\n")
        try:
            _mock_turtle_module.Screen.reset_mock()
            _mock_turtle_module.done.reset_mock()
            _mock_turtle_module.Screen.return_value = MagicMock()
            _mock_turtle_module.Turtle.return_value = MagicMock()
            TurtleAnimator().run_file(path)
            _mock_turtle_module.Screen.assert_called_once()
            _mock_turtle_module.done.assert_called_once()
        finally:
            os.unlink(path)

    def test_file_turtle_created_with_correct_speed(self):
        path = self._make_tmp("pass\n")
        try:
            mock_t = MagicMock()
            _mock_turtle_module.Screen.return_value = MagicMock()
            _mock_turtle_module.Turtle.return_value = mock_t
            TurtleAnimator(speed=3).run_file(path)
            mock_t.speed.assert_called_once_with(3)
            mock_t.hideturtle.assert_called_once()
        finally:
            os.unlink(path)

    def test_terminator_is_silenced(self):
        """turtle.Terminator raised during exec must not escape run_file."""
        path = self._make_tmp("pass\n")
        try:
            with patch_turtle() as (mock_screen, mock_t):
                anim = TurtleAnimator()
                anim._setup()
                # Make screen.update() raise Terminator to simulate window close
                mock_screen.update.side_effect = _FakeTerminator()
                buf = io.StringIO()
                with redirect_stdout(buf):
                    anim.run_file(path)  # must not raise
        finally:
            os.unlink(path)

    def test_keyboard_interrupt_prints_interrupted(self):
        path = self._make_tmp("raise KeyboardInterrupt()\n")
        try:
            with patch_turtle():
                buf = io.StringIO()
                with redirect_stdout(buf):
                    TurtleAnimator().run_file(path)
            self.assertIn("Interrupted", buf.getvalue())
        finally:
            os.unlink(path)

    def test_generic_exception_prints_error(self):
        path = self._make_tmp("raise ValueError('boom')\n")
        try:
            with patch_turtle():
                buf = io.StringIO()
                with redirect_stdout(buf):
                    TurtleAnimator().run_file(path)
            out = buf.getvalue()
            self.assertIn("Error", out)
            self.assertIn("boom", out)
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# 6. TurtleAnimator — new_turtle / get_globals
# ---------------------------------------------------------------------------

class TestNewTurtleAndGetGlobals(unittest.TestCase):

    def test_new_turtle_returns_configured_turtle(self):
        mock_t = MagicMock()
        _mock_turtle_module.Screen.return_value = MagicMock()
        _mock_turtle_module.Turtle.return_value = mock_t
        result = TurtleAnimator(speed=4).new_turtle()
        self.assertIs(result, mock_t)
        mock_t.speed.assert_called_once_with(4)
        mock_t.hideturtle.assert_called_once()

    def test_new_turtle_triggers_setup(self):
        _mock_turtle_module.Screen.reset_mock()
        _mock_turtle_module.Screen.return_value = MagicMock()
        _mock_turtle_module.Turtle.return_value = MagicMock()
        TurtleAnimator().new_turtle()
        _mock_turtle_module.Screen.assert_called_once()

    def test_get_globals_returns_dict_with_t(self):
        mock_t = MagicMock()
        _mock_turtle_module.Screen.return_value = MagicMock()
        _mock_turtle_module.Turtle.return_value = mock_t
        g = TurtleAnimator().get_globals()
        self.assertIn("t", g)
        self.assertIs(g["t"], mock_t)

    def test_get_globals_creates_fresh_turtle_each_call(self):
        """Each get_globals() call must produce a new turtle (no caching)."""
        _mock_turtle_module.Turtle.reset_mock()
        _mock_turtle_module.Screen.return_value = MagicMock()
        _mock_turtle_module.Turtle.return_value = MagicMock()
        anim = TurtleAnimator()
        anim.get_globals()
        anim.get_globals()
        self.assertEqual(_mock_turtle_module.Turtle.call_count, 2)


# ---------------------------------------------------------------------------
# 7. TurtleREPL — init and _ensure_globals
# ---------------------------------------------------------------------------

class TestTurtleREPLInit(unittest.TestCase):

    def setUp(self):
        self.mock_anim = MagicMock()
        self.repl = TurtleREPL(self.mock_anim)

    def test_globals_none_on_init(self):
        self.assertIsNone(self.repl._globals)

    def test_ensure_globals_calls_get_globals_once(self):
        self.repl._ensure_globals()
        self.repl._ensure_globals()
        self.mock_anim.get_globals.assert_called_once()

    def test_ensure_globals_does_not_overwrite_existing(self):
        sentinel = {"x": 1}
        self.mock_anim.get_globals.return_value = sentinel
        self.repl._ensure_globals()
        self.repl._ensure_globals()
        self.assertIs(self.repl._globals, sentinel)


# ---------------------------------------------------------------------------
# 8. TurtleREPL — quit / exit / EOF
# ---------------------------------------------------------------------------

class TestREPLQuitAndExit(unittest.TestCase):

    def setUp(self):
        self.repl = TurtleREPL(MagicMock())

    def test_quit_exits_loop(self):
        out = run_repl_with_inputs(self.repl, ["quit"])
        self.assertIn("Bye", out)

    def test_exit_exits_loop(self):
        out = run_repl_with_inputs(self.repl, ["exit"])
        self.assertIn("Bye", out)

    def test_eof_exits_loop(self):
        out = run_repl_with_inputs(self.repl, [])
        self.assertIn("Bye", out)

    def test_keyboard_interrupt_exits_loop(self):
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.repl.run()
        self.assertIn("Bye", buf.getvalue())


# ---------------------------------------------------------------------------
# 9. TurtleREPL — help
# ---------------------------------------------------------------------------

class TestREPLHelp(unittest.TestCase):

    def test_help_prints_expected_content(self):
        repl = TurtleREPL(MagicMock())
        out = run_repl_with_inputs(repl, ["help", "quit"])
        self.assertIn("Built-in commands", out)
        self.assertIn("t.forward", out)


# ---------------------------------------------------------------------------
# 10. TurtleREPL — demos
# ---------------------------------------------------------------------------

class TestREPLDemos(unittest.TestCase):

    def test_demos_lists_all_five(self):
        repl = TurtleREPL(MagicMock())
        out = run_repl_with_inputs(repl, ["demos", "quit"])
        for name in ("spiral", "tree", "star", "clock", "fern"):
            self.assertIn(name, out)


# ---------------------------------------------------------------------------
# 11. TurtleREPL — run command
# ---------------------------------------------------------------------------

class TestREPLRunCommand(unittest.TestCase):

    def setUp(self):
        self.mock_anim = MagicMock()
        self.repl = TurtleREPL(self.mock_anim)

    def test_run_builtin_demo_name_resolves_to_examples_path(self):
        run_repl_with_inputs(self.repl, ["run spiral", "quit"])
        args, _ = self.mock_anim.run_file.call_args
        self.assertTrue(
            args[0].endswith(os.path.join("examples", "spiral.py"))
        )

    def test_run_arbitrary_path_passed_through(self):
        run_repl_with_inputs(self.repl, ["run /tmp/my_script.py", "quit"])
        self.mock_anim.run_file.assert_called_once_with("/tmp/my_script.py")

    def test_run_resets_globals_after_file(self):
        self.repl._globals = {"sentinel": True}
        run_repl_with_inputs(self.repl, ["run spiral", "quit"])
        self.assertIsNone(self.repl._globals)

    def test_run_extra_spaces_in_arg_trimmed(self):
        """'run  spiral' (double space) must still resolve to the demo."""
        run_repl_with_inputs(self.repl, ["run  spiral", "quit"])
        args, _ = self.mock_anim.run_file.call_args
        self.assertTrue(
            args[0].endswith(os.path.join("examples", "spiral.py"))
        )

    def test_all_demos_resolve_to_correct_paths(self):
        for demo in ("spiral", "tree", "star", "clock", "fern"):
            with self.subTest(demo=demo):
                repl = TurtleREPL(MagicMock())
                run_repl_with_inputs(repl, [f"run {demo}", "quit"])
                args, _ = repl.animator.run_file.call_args
                self.assertTrue(
                    args[0].endswith(
                        os.path.join("examples", f"{demo}.py")
                    )
                )


# ---------------------------------------------------------------------------
# 12. TurtleREPL — clear and reset
# ---------------------------------------------------------------------------

class TestREPLClearAndReset(unittest.TestCase):

    def _make_repl(self):
        mock_anim = MagicMock()
        repl = TurtleREPL(mock_anim)
        clear_fn = MagicMock()
        reset_fn = MagicMock()
        repl._globals = {"clear": clear_fn, "reset": reset_fn}
        return repl, clear_fn, reset_fn

    def test_clear_calls_globals_clear(self):
        repl, clear_fn, _ = self._make_repl()
        run_repl_with_inputs(repl, ["clear", "quit"])
        clear_fn.assert_called_once()

    def test_reset_calls_globals_reset(self):
        repl, _, reset_fn = self._make_repl()
        run_repl_with_inputs(repl, ["reset", "quit"])
        reset_fn.assert_called_once()

    def test_clear_triggers_ensure_globals_when_none(self):
        mock_anim = MagicMock()
        mock_anim.get_globals.return_value = {
            "clear": MagicMock(), "reset": MagicMock()
        }
        repl = TurtleREPL(mock_anim)
        run_repl_with_inputs(repl, ["clear", "quit"])
        mock_anim.get_globals.assert_called()


# ---------------------------------------------------------------------------
# 13. TurtleREPL — multiline blocks
# ---------------------------------------------------------------------------

class TestREPLMultilineBlocks(unittest.TestCase):

    def setUp(self):
        self.mock_anim = MagicMock()
        self.repl = TurtleREPL(self.mock_anim)

    def test_colon_line_not_immediately_executed(self):
        # Buffer collects lines; EOFError ends loop without flushing.
        run_repl_with_inputs(self.repl, ["for i in range(3):"])
        self.mock_anim.run_expr.assert_not_called()

    def test_blank_line_flushes_buffer(self):
        run_repl_with_inputs(
            self.repl, ["for i in range(3):", "    pass", "", "quit"]
        )
        self.mock_anim.run_expr.assert_called_once()
        code_arg = self.mock_anim.run_expr.call_args[0][0]
        self.assertIn("for i in range(3):", code_arg)
        self.assertIn("    pass", code_arg)

    def test_blank_line_at_top_level_does_nothing(self):
        run_repl_with_inputs(self.repl, ["", "quit"])
        self.mock_anim.run_expr.assert_not_called()

    def test_single_line_executed_immediately(self):
        run_repl_with_inputs(self.repl, ["t.forward(100)", "quit"])
        self.mock_anim.run_expr.assert_called_once()
        self.assertEqual(
            self.mock_anim.run_expr.call_args[0][0], "t.forward(100)"
        )

    def test_continued_lines_accumulate_in_buffer(self):
        run_repl_with_inputs(
            self.repl,
            ["for i in range(3):", "    x = i", "    y = x * 2", "", "quit"]
        )
        code_arg = self.mock_anim.run_expr.call_args[0][0]
        self.assertIn("    x = i", code_arg)
        self.assertIn("    y = x * 2", code_arg)

    def test_keyword_inside_buffer_not_intercepted_as_command(self):
        """'quit' as a buffer body line must not exit the REPL early."""
        run_repl_with_inputs(
            self.repl,
            ["for i in range(1):", "    x = 1  # not quit", "", "quit"]
        )
        self.mock_anim.run_expr.assert_called_once()

    def test_multiple_blocks_run_independently(self):
        run_repl_with_inputs(
            self.repl,
            ["for i in range(1):", "    pass", "",
             "for j in range(2):", "    pass", "", "quit"]
        )
        self.assertEqual(self.mock_anim.run_expr.call_count, 2)


# ---------------------------------------------------------------------------
# 14. TurtleREPL — _execute
# ---------------------------------------------------------------------------

class TestREPLExecute(unittest.TestCase):

    def setUp(self):
        self.mock_anim = MagicMock()
        self.repl = TurtleREPL(self.mock_anim)
        self.repl._globals = {"x": 1}

    def test_execute_calls_run_expr(self):
        self.repl._execute("t.forward(100)")
        self.mock_anim.run_expr.assert_called_once_with(
            "t.forward(100)", self.repl._globals
        )

    def test_execute_terminator_resets_globals_and_prints(self):
        self.mock_anim.run_expr.side_effect = _FakeTerminator()
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.repl._execute("anything")
        self.assertIsNone(self.repl._globals)
        self.assertIn("Window closed", buf.getvalue())

    def test_execute_generic_exception_prints_error_keeps_globals(self):
        self.mock_anim.run_expr.side_effect = ValueError("oops")
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.repl._execute("anything")
        self.assertIn("oops", buf.getvalue())
        # Generic exceptions must NOT reset _globals.
        self.assertIsNotNone(self.repl._globals)

    def test_execute_system_exit_propagates(self):
        self.mock_anim.run_expr.side_effect = SystemExit(0)
        with self.assertRaises(SystemExit):
            self.repl._execute("anything")


# ---------------------------------------------------------------------------
# 15. main.py — argparse routing
# ---------------------------------------------------------------------------

class TestMainArgparse(unittest.TestCase):

    def _run_main(self, argv):
        import main
        buf = io.StringIO()
        with patch.object(sys, "argv", ["main.py"] + argv), \
             redirect_stdout(buf):
            try:
                main.main()
            except SystemExit:
                pass
        return buf.getvalue()

    def test_list_flag_prints_all_demos(self):
        out = self._run_main(["--list"])
        for name in ("spiral", "tree", "star", "clock", "fern"):
            self.assertIn(name, out)

    def test_list_flag_does_not_create_animator(self):
        with patch("main.TurtleAnimator") as mock_anim_class:
            self._run_main(["--list"])
            mock_anim_class.assert_not_called()

    def test_default_args_construct_animator_with_defaults(self):
        with patch("main.TurtleAnimator") as mock_anim_class, \
             patch("main.TurtleREPL") as mock_repl_class:
            mock_repl_class.return_value.run.return_value = None
            self._run_main([])
            mock_anim_class.assert_called_once_with(
                width=800, height=600, bg="black", speed=6
            )

    def test_custom_args_forwarded_to_animator(self):
        with patch("main.TurtleAnimator") as mock_anim_class, \
             patch("main.TurtleREPL") as mock_repl_class:
            mock_repl_class.return_value.run.return_value = None
            self._run_main(
                ["--width", "1024", "--height", "768",
                 "--bg", "navy", "--speed", "3"]
            )
            mock_anim_class.assert_called_once_with(
                width=1024, height=768, bg="navy", speed=3
            )

    def test_demo_flag_calls_run_file_with_examples_path(self):
        with patch("main.TurtleAnimator") as mock_anim_class:
            mock_anim = MagicMock()
            mock_anim_class.return_value = mock_anim
            self._run_main(["--demo", "spiral"])
            args, _ = mock_anim.run_file.call_args
            self.assertTrue(
                args[0].endswith(os.path.join("examples", "spiral.py"))
            )

    def test_all_demos_resolve_via_cli(self):
        for demo in ("spiral", "tree", "star", "clock", "fern"):
            with self.subTest(demo=demo):
                with patch("main.TurtleAnimator") as mock_anim_class:
                    mock_anim = MagicMock()
                    mock_anim_class.return_value = mock_anim
                    self._run_main(["--demo", demo])
                    args, _ = mock_anim.run_file.call_args
                    self.assertTrue(
                        args[0].endswith(
                            os.path.join("examples", f"{demo}.py")
                        )
                    )

    def test_unknown_demo_prints_message(self):
        with patch("main.TurtleAnimator") as mock_anim_class:
            mock_anim_class.return_value = MagicMock()
            out = self._run_main(["--demo", "bogus"])
        self.assertIn("Unknown demo", out)

    def test_script_arg_calls_run_file(self):
        with patch("main.TurtleAnimator") as mock_anim_class:
            mock_anim = MagicMock()
            mock_anim_class.return_value = mock_anim
            self._run_main(["myscript.py"])
            mock_anim.run_file.assert_called_once_with("myscript.py")

    def test_no_args_starts_repl(self):
        with patch("main.TurtleAnimator") as mock_anim_class, \
             patch("main.TurtleREPL") as mock_repl_class:
            mock_anim = MagicMock()
            mock_anim_class.return_value = mock_anim
            mock_repl = MagicMock()
            mock_repl_class.return_value = mock_repl
            self._run_main([])
            mock_repl_class.assert_called_once_with(mock_anim)
            mock_repl.run.assert_called_once()


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()

import io
import traceback
from contextlib import redirect_stderr, redirect_stdout

_context: dict = {}


def run_code(code: str) -> tuple[str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exec(code, _context)
    except Exception:
        traceback.print_exc(file=stderr)

    stdout_str = stdout.getvalue()
    stderr_str = stderr.getvalue()
    _context["_stdout"] = stdout_str
    _context["_stderr"] = stderr_str
    return stdout_str, stderr_str

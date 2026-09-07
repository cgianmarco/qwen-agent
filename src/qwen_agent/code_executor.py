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
    return stdout.getvalue(), stderr.getvalue()

_context: dict = {}


def run_code(code: str) -> None:
    exec(code, _context)

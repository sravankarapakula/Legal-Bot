"""
UI Helpers — ANSI colors, bot messages, prompts, and banners.
"""

import textwrap
import time


# ─── ANSI Color Helpers ──────────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    GREEN   = "\033[92m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    WHITE   = "\033[97m"
    DIM     = "\033[2m"
    MAGENTA = "\033[95m"


def bot(msg: str):
    """Print a bot message inside a styled box."""
    print()
    lines = msg.strip().split("\n")
    print(f"  {C.CYAN}╔{'═' * 64}╗{C.RESET}")
    for line in lines:
        wrapped = textwrap.wrap(line, width=62) if line.strip() else [""]
        for wline in wrapped:
            pad = 62 - len(wline)
            print(f"  {C.CYAN}║{C.RESET} {C.WHITE}{wline}{' ' * pad}{C.RESET} {C.CYAN}║{C.RESET}")
    print(f"  {C.CYAN}╚{'═' * 64}╝{C.RESET}")
    print()


def user_input(prompt: str = "You") -> str:
    """Get user input with a styled prompt."""
    return input(f"  {C.GREEN}▶ {prompt}: {C.RESET}").strip()


def header(title: str):
    print(f"\n  {C.BOLD}{C.BLUE}{'━' * 66}{C.RESET}")
    print(f"  {C.BOLD}{C.BLUE}  {title}{C.RESET}")
    print(f"  {C.BOLD}{C.BLUE}{'━' * 66}{C.RESET}\n")


def step_banner(step: int, title: str):
    print(f"\n  {C.MAGENTA}┌─ Step {step}: {title} {'─' * max(0, 50 - len(title))}┐{C.RESET}")


def info(msg: str):
    print(f"  {C.DIM}{C.YELLOW}ℹ  {msg}{C.RESET}")


def success(msg: str):
    print(f"  {C.GREEN}✅ {msg}{C.RESET}")


def warning(msg: str):
    print(f"  {C.YELLOW}⚠️  {msg}{C.RESET}")


def thinking(msg: str = "Processing"):
    print(f"  {C.DIM}🔄 {msg}...", end="", flush=True)
    time.sleep(0.6)
    print(f"\r  {C.DIM}✔  {msg} complete.{C.RESET}     ")

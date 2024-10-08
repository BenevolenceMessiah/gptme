import logging
import random
import re
import sys
import textwrap
from datetime import datetime, timedelta

import tiktoken
from rich import print
from rich.console import Console
from rich.syntax import Syntax

EMOJI_WARN = "⚠️"

logger = logging.getLogger(__name__)


def get_tokenizer(model: str):
    if "gpt-4" in model or "gpt-3.5" in model:
        return tiktoken.encoding_for_model(model)
    else:  # pragma: no cover
        logger.warning(
            f"No encoder implemented for model {model}."
            "Defaulting to tiktoken cl100k_base encoder."
            "Use results only as estimates."
        )
        return tiktoken.get_encoding("cl100k_base")


actions = [
    "running",
    "jumping",
    "walking",
    "skipping",
    "hopping",
    "flying",
    "swimming",
    "crawling",
    "sneaking",
    "sprinting",
    "sneaking",
    "dancing",
    "singing",
    "laughing",
]
adjectives = [
    "funny",
    "happy",
    "sad",
    "angry",
    "silly",
    "crazy",
    "sneaky",
    "sleepy",
    "hungry",
    # colors
    "red",
    "blue",
    "green",
    "pink",
    "purple",
    "yellow",
    "orange",
]
nouns = [
    "cat",
    "dog",
    "rat",
    "mouse",
    "fish",
    "elephant",
    "dinosaur",
    # birds
    "bird",
    "pelican",
    # fictional
    "dragon",
    "unicorn",
    "mermaid",
    "monster",
    "alien",
    "robot",
    # sea creatures
    "whale",
    "shark",
    "walrus",
    "octopus",
    "squid",
    "jellyfish",
    "starfish",
    "penguin",
    "seal",
]


def generate_name():
    action = random.choice(actions)
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    return f"{action}-{adjective}-{noun}"


def is_generated_name(name: str) -> bool:
    """if name is a name generated by generate_name"""
    all_words = actions + adjectives + nouns
    return name.count("-") == 2 and all(word in all_words for word in name.split("-"))


def epoch_to_age(epoch):
    # takes epoch and returns "x minutes ago", "3 hours ago", "yesterday", etc.
    age = datetime.now() - datetime.fromtimestamp(epoch)
    if age < timedelta(minutes=1):
        return "just now"
    elif age < timedelta(hours=1):
        return f"{age.seconds // 60} minutes ago"
    elif age < timedelta(days=1):
        return f"{age.seconds // 3600} hours ago"
    elif age < timedelta(days=2):
        return "yesterday"
    else:
        return f"{age.days} days ago ({datetime.fromtimestamp(epoch).strftime('%Y-%m-%d')})"


def print_preview(code: str, lang: str):  # pragma: no cover
    print()
    print("[bold white]Preview[/bold white]")
    print(Syntax(code.strip(), lang))
    print()


def ask_execute(question="Execute code?", default=True) -> bool:  # pragma: no cover
    # TODO: add a way to outsource ask_execute decision to another agent/LLM
    console = Console()
    choicestr = f"({'Y' if default else 'y'}/{'n' if default else 'N'})"
    # answer = None
    # while not answer or answer.lower() not in ["y", "yes", "n", "no", ""]:
    print_bell()  # Ring the bell just before asking for input
    answer = console.input(
        f"[bold yellow on dark_red] {EMOJI_WARN} {question} {choicestr} [/] ",
    )
    return answer.lower() in (["y", "yes"] + [""] if default else [])


def transform_examples_to_chat_directives(s: str, strict=False) -> str:
    # transforms an example with "> Role:" dividers into ".. chat::" directive
    orig = s
    s = re.sub(
        r"(^|\n)([>] )?(.+):",
        r"\1\3:",
        s,
    )
    if strict:
        assert s != orig, "Couldn't find a message"
    s = textwrap.indent(s, "   ")
    orig = s
    s = re.sub(
        r"(^|\n)(   [# ]+(.+)(\n\s*)+)?   User:",
        r"\1\3\n\n.. chat::\n\n   User:",
        s,
    )
    if strict:
        assert s != orig, "Couldn't find place to put start of directive"
    return s


def print_bell():
    """Ring the terminal bell."""
    sys.stdout.write("\a")
    sys.stdout.flush()

#!/usr/bin/env python3
"""Simple command-line roulette game."""

from __future__ import annotations

import random
from typing import Dict, Tuple

# European roulette layout (single zero). Values from https://en.wikipedia.org/wiki/Roulette
ROULETTE_COLORS: Dict[int, str] = {
    0: "green",
    1: "red",
    2: "black",
    3: "red",
    4: "black",
    5: "red",
    6: "black",
    7: "red",
    8: "black",
    9: "red",
    10: "black",
    11: "black",
    12: "red",
    13: "black",
    14: "red",
    15: "black",
    16: "red",
    17: "black",
    18: "red",
    19: "red",
    20: "black",
    21: "red",
    22: "black",
    23: "red",
    24: "black",
    25: "red",
    26: "black",
    27: "red",
    28: "black",
    29: "black",
    30: "red",
    31: "black",
    32: "red",
    33: "black",
    34: "red",
    35: "black",
    36: "red",
}


def prompt_float(prompt: str, minimum: float, maximum: float) -> float:
    while True:
        try:
            value = float(input(prompt))
        except ValueError:
            print("Please enter a number.")
            continue
        if value < minimum or value > maximum:
            print(f"Enter a value between {minimum} and {maximum}.")
            continue
        return round(value, 2)


def prompt_choice(prompt: str, choices: Tuple[str, ...]) -> str:
    lowered = tuple(choice.lower() for choice in choices)
    while True:
        selection = input(prompt).strip().lower()
        if selection in lowered:
            return selection
        display = ", ".join(choices)
        print(f"Invalid choice. Pick from: {display}")


def spin_wheel() -> Tuple[int, str]:
    value = random.randint(0, 36)
    return value, ROULETTE_COLORS[value]


def resolve_bet(
    bet_type: str,
    bet_value: str,
    bet_amount: float,
    outcome_value: int,
    outcome_color: str,
) -> float:
    """Return profit (positive) or loss (negative)."""
    if bet_type == "number":
        if outcome_value == int(bet_value):
            return bet_amount * 35
        return -bet_amount

    if bet_type == "color":
        if outcome_color == bet_value:
            return bet_amount
        return -bet_amount

    if bet_type == "parity":
        if outcome_value == 0:
            return -bet_amount
        parity = "even" if outcome_value % 2 == 0 else "odd"
        if parity == bet_value:
            return bet_amount
        return -bet_amount

    raise ValueError(f"Unknown bet type {bet_type}")


def main() -> None:
    print("=== Welcome to CLI Roulette ===")
    balance = 100.0

    while balance > 0:
        print(f"\nCurrent balance: ${balance:.2f}")
        bet_amount = prompt_float(
            "Enter bet amount (or 0 to cash out): ",
            minimum=0,
            maximum=balance,
        )
        if bet_amount == 0:
            break

        bet_kind = prompt_choice(
            "Choose bet type (number/color/parity): ",
            ("number", "color", "parity"),
        )

        if bet_kind == "number":
            while True:
                try:
                    number = int(input("Pick a number between 0 and 36: "))
                except ValueError:
                    print("Please enter an integer.")
                    continue
                if 0 <= number <= 36:
                    bet_value = str(number)
                    break
                print("Number must be between 0 and 36.")
        elif bet_kind == "color":
            bet_value = prompt_choice("Pick a color (red/black): ", ("red", "black"))
        else:
            bet_value = prompt_choice("Pick parity (even/odd): ", ("even", "odd"))

        print("Spinning the wheel...")
        value, color = spin_wheel()
        print(f"The ball landed on {value} ({color}).")

        profit = resolve_bet(bet_kind, bet_value, bet_amount, value, color)
        balance += profit

        if profit >= 0:
            print(f"You won ${profit:.2f}!")
        else:
            print(f"You lost ${-profit:.2f}.")

    print(f"\nYou leave the table with ${balance:.2f}. Thanks for playing!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGame aborted. See you next time!")

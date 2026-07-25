#!/usr/bin/env python3
"""Main entry point for LongBook Merger application."""

from gui import LongBookMergerGUI
import sys


def main():
    """Launch the application."""
    app = LongBookMergerGUI()
    app.run()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate clean registry data and build deterministic unsigned release assets."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.release_common import build_release, cli_result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', required=True, type=int, metavar='N', help='positive registry release number')
    parser.add_argument('--out', required=True, type=Path, metavar='DIR', help='new or existing empty output directory')
    args = parser.parse_args(argv)
    return cli_result(lambda: build_release(args.registry, args.out))


if __name__ == '__main__':
    sys.exit(main())

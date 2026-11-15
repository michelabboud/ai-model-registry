#!/usr/bin/env python3
"""Verify signature, hashes, sizes and exact safe tar membership without extraction."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.release_common import cli_result, verify_release


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dir', required=True, type=Path, metavar='DIR', help='directory containing the three release assets')
    args = parser.parse_args(argv)
    return cli_result(lambda: verify_release(args.dir.resolve()))


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Verify, publish the next numbered GitHub release, and byte-check its downloads.

This command uses the network and authenticated gh. It never replaces a release
or moves/deletes a tag. Build, sign and verify separately before invoking it.
"""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.release_common import cli_result, publish_release


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dir', required=True, type=Path, metavar='DIR', help='directory containing the three verified release assets')
    args = parser.parse_args(argv)
    return cli_result(lambda: publish_release(args.dir.resolve()))


if __name__ == '__main__':
    sys.exit(main())

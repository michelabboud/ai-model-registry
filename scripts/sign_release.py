#!/usr/bin/env python3
"""Sign a release locally with OpenSSL >= 3.0 and immediately verify it."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.release_common import cli_result, sign_release


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dir', required=True, type=Path, metavar='DIR', help='directory built by build_release.py')
    parser.add_argument('--key', required=True, type=Path, metavar='PATH', help='owned regular 0600 private key outside this repository')
    args = parser.parse_args(argv)
    return cli_result(lambda: sign_release(args.dir.resolve(), args.key))


if __name__ == '__main__':
    sys.exit(main())

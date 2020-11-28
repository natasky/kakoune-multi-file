#!/usr/bin/env python3
import argparse
import re
import subprocess
import sys
import io

from collections import namedtuple, defaultdict

from digest import digest


class BadHash(Exception):
    pass


HUNK_HEADER_RE = re.compile(
    r"""
    ^ @@@ \s
    (?P<path> .+ ) \s
    (?P<first_line> \d+ ) , (?P<line_count> \d+ ) \s
    (?P<hash> \S+ ) \s
    @@@ $
    """,
    re.VERBOSE,
)


InputHunk = namedtuple("InputHunk", "path first_line line_count hash contents")
File = namedtuple("File", "path hash ordered_hunks")
Hunk = namedtuple("Hunk", "first_line line_count contents")


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dry-run", action="store_true",
    )

    return parser.parse_args()


def read_input_hunks(lines):
    hunks = []

    for line in lines:
        hunk_header_match = HUNK_HEADER_RE.match(line)

        if hunk_header_match is not None:
            hunks.append(
                InputHunk(
                    path=hunk_header_match.group("path"),
                    first_line=int(hunk_header_match.group("first_line")),
                    line_count=int(hunk_header_match.group("line_count")),
                    hash=hunk_header_match.group("hash"),
                    contents=[],
                )
            )

        else:
            if len(hunks) == 0:
                raise Exception("Bad input: first line must be hunk header")
            hunks[-1].contents.append(line)

    return hunks


def group_input_hunks_by_file(input_hunks):
    files = []

    hunks_by_file = defaultdict(list)
    for input_hunk in input_hunks:
        hunks_by_file[input_hunk.path].append(input_hunk)

    for path, input_hunks in hunks_by_file.items():
        if any(
            input_hunk.hash != input_hunks[0].hash
            for input_hunk in input_hunks
        ):

            raise Exception(f"Bad input: different hashes for {path}")

        ordered_hunks = sorted(
            (
                Hunk(
                    first_line=input_hunk.first_line,
                    line_count=input_hunk.line_count,
                    contents=input_hunk.contents,
                )
                for input_hunk in input_hunks
            ),
            key=lambda hunk: hunk.first_line,
        )

        files.append(
            File(
                path=path,
                hash=input_hunks[0].hash,
                ordered_hunks=ordered_hunks,
            )
        )

    return files


def apply_file_hunks(file):
    with open(file.path, encoding="utf8") as opened_file:
        file_lines = list(opened_file)

    hash = digest(file_lines)
    if hash != file.hash:
        raise BadHash()

    offset = 0
    for hunk in file.ordered_hunks:
        start_index = hunk.first_line - 1 + offset
        file_lines[start_index : start_index + hunk.line_count] = hunk.contents
        offset += len(hunk.contents) - hunk.line_count

    return "".join(file_lines)


def show_diff(file, new_contents):
    subprocess.run(
        ["diff", "-U3", file.path, "-"], input=new_contents.encode("utf8"),
    )


def write_back(file, new_contents):
    with open(file.path, "w", encoding="utf8") as opened_file:
        opened_file.write(new_contents)


def main():
    args = parse_args()

    try:
        input_hunks = read_input_hunks(sys.stdin)
        files = group_input_hunks_by_file(input_hunks)
    except Exception as error:
        print(f"Error while reading input: {error}")
        sys.exit(1)

    successful_files = 0
    for file in files:
        try:
            new_contents = apply_file_hunks(file)
            successful_files += 1

            if args.dry_run:
                show_diff(file, new_contents)
            else:
                write_back(file, new_contents)
                print(f"{file.path}: OK")

        except BadHash:
            print(f"{file.path}: bad checksum")

        except IOError as error:
            print(f"{file.path}: {error}")

    action = "can be applied" if args.dry_run else "applied"
    print(f"Changes on {successful_files} out of {len(files)} files {action}")

    if successful_files < len(files):
        sys.exit(1)


if __name__ == "__main__":
    main()

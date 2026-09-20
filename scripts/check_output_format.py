#!/usr/bin/env python3
"""EAS 510 - Project 1: validate a results_*.txt file against the required
output format.

Usage:
    python3 scripts/check_output_format.py results_v1.txt [results_v2.txt ...]

Checks (structural only -- accuracy is graded manually):
  * every image block has exactly one Processing line, rule lines, one Final
  * every rule line matches  "Rule N (Name): FIRED|NO MATCH - ... -> s/out points"
  * the Final Score on a block equals the sum of that block's rule scores
  * every image gets a verdict (MATCH to ... or REJECTED)

Exit code 0 = all files valid. This module may also be imported.
"""

import re
import sys

PROC_RE = re.compile(r"^Processing: (.+)$")
RULE_RE = re.compile(
    r"^Rule ([1-9][0-9]*) \(([^()]+)\): (FIRED|NO MATCH) - (.+) -> ([0-9]{1,3})/([0-9]{1,3}) points$"
)
FINAL_RE = re.compile(r"^Final Score: ([0-9]+(?:\.[0-9]+)?)/100 -> (REJECTED|MATCH to .+)$")


def _blocks(lines):
    """Group blank-line-separated image blocks."""
    block = []
    for line in lines:
        if line.strip() == "":
            if block:
                yield block
                block = []
        else:
            block.append(line)
    if block:
        yield block


def validate_text(text, min_rules=3):
    """Validate results-file text. Returns (images, errors) where errors is a
    list of human-readable problems."""
    images = 0
    errors = []
    for idx, block in enumerate(_blocks(text.splitlines()), start=1):
        if not block:
            continue
        images += 1
        procs = [l for l in block if PROC_RE.match(l)]
        rules = [l for l in block if RULE_RE.match(l)]
        finals = [l for l in block if FINAL_RE.match(l)]
        other = [l for l in block
                 if not (PROC_RE.match(l) or RULE_RE.match(l) or FINAL_RE.match(l))]
        if len(procs) != 1:
            errors.append(f"block {idx}: expected exactly 1 Processing line, got {len(procs)}")
        if len(finals) != 1:
            errors.append(f"block {idx}: expected exactly 1 Final Score line, got {len(finals)}")
        if len(rules) < min_rules:
            errors.append(f"block {idx}: expected >= {min_rules} rule lines, got {len(rules)}")
        if any(not r.endswith(" points") for r in rules):
            errors.append(f"block {idx}: malformed rule line")

        # final score must equal the sum of the block's rule scores
        if rules and finals:
            block_sum = sum(int(RULE_RE.match(r).group(5)) for r in rules)
            final_m = FINAL_RE.match(finals[0])
            try:
                final_val = int(float(final_m.group(1)))
            except ValueError:
                final_val = -1
            if final_val != block_sum:
                errors.append(
                    f"block {idx}: Final Score {final_val}/100 != rule sum {block_sum}/100"
                )
    return images, errors


def validate_file(path, min_rules=3):
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as exc:
        return 0, [str(exc)]
    return validate_text(text, min_rules=min_rules)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    min_rules = 3
    if "--expect-rules" in argv:
        i = argv.index("--expect-rules")
        min_rules = int(argv[i + 1])
        del argv[i:i + 2]
    if not argv:
        print("usage: check_output_format.py [--expect-rules N] FILE [...]")
        return 2
    ok = True
    for path in argv:
        images, errors = validate_file(path, min_rules=min_rules)
        if errors:
            ok = False
            print(f"FAIL: {path}")
            for e in errors[:10]:
                print(f"      - {e}")
            if len(errors) > 10:
                print(f"      ... and {len(errors) - 10} more")
        else:
            print(f"PASS: {path} ({images} images)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
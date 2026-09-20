"""EAS 510 - Project 1: test_system.py

Runs SimpleDetector over one or more suspect folders and writes the full
output in the assignment's required format.

Examples (run from the repository root with the dataset as a sibling clone):

    python3 test_system.py --modified --random --output results_v1.txt
    python3 test_system.py --hard --output results_v1_hard.txt
    python3 test_system.py --modified --hard --random --output results_v2.txt

Folders default to <data-dir>/{originals,modified_images,hard,random}.
"""

import argparse
import os
import sys
from pathlib import Path

from forensics_detective import MATCH_THRESHOLD, SimpleDetector

import rules


def ordered_images(data_dir, names):
    """Yield absolute paths to every image in the given folders, in order."""
    roots = []
    for name in names:
        folder = data_dir / name
        if folder.is_dir():
            roots.append(folder)
        elif name == "modified_images" and (data_dir / "modified").is_dir():
            roots.append(data_dir / "modified")
    for folder in roots:
        for entry in sorted(folder.iterdir()):
            if entry.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                yield entry


def line_for(evidence):
    r = evidence
    status = "FIRED" if r["fired"] else "NO MATCH"
    return f"Rule {r['rule']} ({r['name']}): {status} - {r['note']} -> {r['score']}/{r['out_of']} points"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the detective over image folders.")
    parser.add_argument("--originals", default=None, help="folder of known originals")
    parser.add_argument("--modified", action="store_true", help="include modified_images/")
    parser.add_argument("--hard", action="store_true", help="include hard/")
    parser.add_argument("--random", action="store_true", help="include random/")
    parser.add_argument("--output", required=True, help="output results file (e.g. results_v1.txt)")
    parser.add_argument("--data-dir", default=None,
                        help="sibling dataset repo folder (default: ../EAS510_Assignment1)")
    parser.add_argument("--rules-v2", action="store_true",
                        help="use rules_v2.py (Phase 2: Rules 1-4) instead of the V1 rule set")
    parser.add_argument("--rule", action="append", default=None,
                        help="extra rule name for Phase 2 (repeatable); V2 uses this to add rule4_*")
    args = parser.parse_args(argv)

    data_dir = _find_data_dir(args.data_dir)
    originals = Path(args.originals) if args.originals else data_dir / "originals"

    rule_names = None
    rule_modules = None
    if args.rule:
        rule_names = args.rule
    elif args.rules_v2:
        try:
            import rules_v2
        except ImportError:
            sys.exit("error: --rules-v2 needs a rules_v2.py in this folder")
        rule_names = rules_v2.RULES
        rule_modules = [rules, rules_v2]
    detective = SimpleDetector(rule_names=rule_names, rule_modules=rule_modules)
    detective.register_targets(originals)

    wanted = []
    if args.modified:
        wanted.append("modified_images")
    if args.hard:
        wanted.append("hard")
    if args.random:
        wanted.append("random")
    if not wanted:
        sys.exit("error: pick at least one of --modified, --hard, --random")

    images = list(ordered_images(data_dir, wanted))
    if not images:
        sys.exit(f"error: no images found in {wanted} under {data_dir}")

    lines = []
    for image in images:
        lines.append(f"Processing: {image.name}")
        verdict = detective.find_best_match(str(image))
        for ev in verdict["evidence"]:
            lines.append(line_for(ev))
        score = int(round(verdict["confidence"]))
        lines.append(
            f"Final Score: {score}/100 -> "
            + ("REJECTED" if verdict["rejected"] else f"MATCH to {verdict['target']}")
        )
        lines.append("")  # blank line between image blocks

    body = "\n".join(lines).rstrip("\n") + "\n"
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(body)

    n_match = sum(1 for l in lines if "-> MATCH to" in l)
    n_reject = sum(1 for l in lines if "-> REJECTED" in l)
    print(f"processed {len(images)} images: {n_match} matched, {n_reject} rejected")
    print(f"wrote {args.output}")
    return 0


def _find_data_dir(explicit):
    if explicit:
        return Path(explicit)
    candidates = [
        Path("../EAS510_Assignment1"),
        Path.home() / "workspace" / "EAS510_Assignment1",
        Path("data/EAS510_Assignment1"),
    ]
    for c in candidates:
        if (c / "modified_images").is_dir():
            return c
    sys.exit("error: could not locate the dataset. Clone EAS510_Assignment1 next to "
             "this repo or pass --data-dir /path/to/EAS510_Assignment1")


if __name__ == "__main__":
    sys.exit(main())
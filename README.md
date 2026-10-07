# EAS 510 - Assignment 1: Digital Forensics Apprentice

A rule-based expert system that matches modified images back to their originals.

This is the **starter repository** for Project 1. Two repositories matter:

| Repository | Role |
|------------|------|
| `delveccj/EAS510_Assignment1_starter` (this repo) | Your **code** lives here. You will fork it, work in your fork, and push your final submission here. |
| `delveccj/EAS510_Assignment1` | The **dataset** (read-only). Clone it for the images; never commit it to your fork. |

## Setup on your Codio box

```bash
# 1. Fork this repo on GitHub, then in your box:
git clone https://github.com/YOUR-USERNAME/EAS510_Assignment1_starter.git
cd EAS510_Assignment1_starter

# 2. Clone the read-only dataset as a sibling folder (images live there):
cd ~/workspace
git clone https://github.com/delveccj/EAS510_Assignment1.git

# 3. Install dependencies:
cd ~/workspace/EAS510_Assignment1_starter
python3 -m pip install -r requirements.txt

# 4. Point this box at YOUR fork (run once):
./setup_git.sh
```

## Repository layout

```
forensics_detective.py   SimpleDetector: register targets + find_best_match
rules.py                 Rule functions (Rule 1: Metadata, Rule 2: Histogram, Rule 3: Template)
test_system.py           Runs the detector over the data folders and writes results_*.txt
scripts/check_output_format.py   Validates a results file against the required format
setup_git.sh, submit.sh  One-time setup + commit/push helper ("backup button")
```

## The task in one paragraph

Implement three interpretable rules (metadata, color histogram, template matching)
that combine into a 0-100 confidence score. Run your system on `modified_images/`
and `random/` and save the full output as `results_v1.txt`. In Phase 2, run on
`hard/`, diagnose a systematic failure, add a **Rule 4**, and save
`results_v1_hard.txt` and `results_v2.txt`. Full instructions are in the Codio guide
and in the assignment PDF in UBLearns.

## Running

```bash
# Phase 1 (easy + random) -> results_v1.txt
python3 test_system.py --modified --random --output results_v1.txt

# Phase 1 on hard cases -> results_v1_hard.txt
python3 test_system.py --hard --output results_v1_hard.txt

# Phase 2 (everything) -> results_v2.txt
python3 test_system.py --modified --hard --random --output results_v2.txt

# Validate any results file against the required format:
python3 scripts/check_output_format.py results_v1.txt
```

The data folders are resolved from a sibling clone of `EAS510_Assignment1`.
If your data is elsewhere, pass `--data-dir /path/to/EAS510_Assignment1`.

## Output format (do not alter)

```
Processing: modified_image_01.jpg
Rule 1 (Metadata): FIRED - Size ratio 0.85 -> 20/30 points
Rule 2 (Histogram): FIRED - Correlation 0.92 -> 25/30 points
Rule 3 (Template): FIRED - Match score 0.76 -> 30/40 points
Final Score: 75/100 -> MATCH to original_03.jpg
```

## Backup doctrine

Your Codio box can be reset at any time. **Your fork on GitHub is the only safe
copy.** After every milestone run `./submit.sh "describe what you did"`. A box
restart never touches GitHub.

## License

Apache 2.0. See `LICENSE`.

## Observed weakness in V1: what failed and why
For V1 with the easy and random images, I raised correct match percentage from 51.7% (31/60) to 61.7% (37/60) by tuning Rule 3's metric threshold from 0.4 to, ultimately, 0.1. I focused on Rule 3's threshold specifically because many of the rejected crop cases were already using valuable evidence from Rules 1 and 2, whereas Rule 3 was producing nonzero template similarity scores which were being discarded because the 0.4 threshold was too high, meaning that while Rules 1 and 2 were contributing to the overall score, Rule 3 was often contributing 0 points. Since Rule 3 carries the highest weight (40 points, as opposed to 30 for Rules 1 and 2), allowing weaker template evidence to contribute was enough to recover 6 correct near-threshold matches without allowing any random samples to be accepted. It should be noted that there was 1 sample that was matched to the incorrect target image (modified_04_crop_75pct.jpg) to begin with, and this persisted after tuning the Rule 3 threshold.

For V1 with the hard images, the clearest weakness was with certain combined transformations which involved cropping (such as off-center crop + compression, of which all 10 cases were rejected, and crop + brightness + compression, of which all 10 cases were also rejected). Off-center cropping weakened Rule 3's template matching, while the added brightness changes in v2 could also reduce Rule 2's histogram score, causing multiple points of failure. For example, 'original_01__crop_keep70__bright__compress__q40__v2.jpg' scored 30/30 on Rule 1, but 0/30 on Rule 2 and 0/40 on Rule 3, resulting in rejection (30/100). In some cases ('original_01__contrast__compress__q70__v5.jpg'), contrast weakened histogram evidence (0/30 histogram score), but V1 survived as template matching remained strong (40/40), meaning that a main failure point is cropping when it significantly weakens template matching, and crop + brightness lowers overall score even more because it weakens histogram evidence as well. Cases which V1 handled successfully were rotation + compression and contrast + compression.

## Design decision for V2: what Rule 4 is and why you chose it
I chose multi-scale template matching to address V1's weakness with cropped/resized images. At first, I tried ORB because I thought local features would remain detectable even when part of an image is cropped or resized. However, ORB didn't improve the hard-image results much: initially, it produced 33 matches out of 60, and increasing the Hamming-distance threshold and increasing the number of detected features raised it to 34 matches at best. Once I saw tweaking parameters wasn't creating significant positive change, I switched to multi-scale template matching. This approach serves as an extension to Rule 3 by resizing the suspect image across several scales (0.5-1.0 with intervals of 0.1) and keeping only the strongest template match. I made it more selective by requiring the best multi-scale template match score to be at least 0.85 and actually improve the normal-scale match by at least 0.20, because Rule 4 is stronger/more supplementary if it's providing valuable new evidence that Rule 3 could not already detect.

## Effect of the change: accuracy before/after on easy vs hard

## Trade-offs: what new costs or risks did Rule 4 introduce

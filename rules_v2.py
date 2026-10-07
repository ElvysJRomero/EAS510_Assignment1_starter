"""EAS 510 - Project 1 - Phase 2: the V2 rule set.

Rules 1-3 are kept exactly as in `rules.py`. Your job is to ADD Rule 4 that
targets the systematic weakness you diagnosed from results_v1_hard.txt.

Constraint: the rules' `out_of` weights must still sum to 100 so the Final
Score stays on a /100 scale (the format validator enforces "Final Score:
<s>/100" equals the sum of the block's rule scores).

Example split that keeps the original spirit: Rules 1-3 -> 25/25/40 and
Rule 4 -> 10 (or trim the losers more aggressively).
"""

import rules
import cv2

#: Import the original rules and append your new one.
RULES = rules.RULES + ("rule4_multiscale",)


def rule4_multiscale(target, input_path):
    out = {
        "rule": 4,
        "name": "multiscale",
        "fired": False,
        "score": 0,
        "out_of": 10,
        "note": "Best match 0.00",
        "metric": 0.0,
    }

    try:
        src = rules._gray(target["path"])
        inp = rules._gray(input_path)
        if src is None or inp is None:
            return out
        #best = best template match at any tested scale -- base = score when suspect is at normal scale
        best_score = 0.0
        base_score = 0.0

        for scale in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            width = int(inp.shape[1]*scale)
            height = int(inp.shape[0]*scale)
            #Resize suspect to width, height
            resized = cv2.resize(inp, (width, height))
            if resized.shape[0] > src.shape[0] or resized.shape[1] > src.shape[1]:
                continue
            #Slides resized across src for similarity scores
            result = cv2.matchTemplate(src, resized, cv2.TM_CCOEFF_NORMED)
            #Find min and max of matchTemplate scores
            score = cv2.minMaxLoc(result)[1]
            if scale == 1.0:
                base_score = score

            best_score = max(best_score, score)

        out["metric"] = round(best_score, 3)

        #How much did the different scales improve the match?
        improvement = best_score - base_score

        out["metric"] = round(best_score, 3)
        out["note"] = (f"Best match {out['metric']:.2f}, " f"improvement {improvement:.2f}")

        if out["metric"] >= 0.85 and improvement >= 0.20:
            out["fired"] = True
            out["score"] = int(round(out["out_of"] * out["metric"]))

    except Exception:
        pass

    return out

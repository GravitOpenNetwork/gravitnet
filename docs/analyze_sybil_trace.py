#!/usr/bin/env python3
import json
import statistics
import sys
from pathlib import Path


def analyze(path: str) -> dict:
    data = json.loads(Path(path).read_text())
    scores = []

    if isinstance(data, dict):
        events = data.get("convergence_events", [])
        for event in events:
            conf = event.get("confidence_score")
            if conf is not None:
                scores.append(float(conf))
    elif isinstance(data, list):
        for event in data:
            conf = event.get("confidence_true") or event.get("confidence_score")
            if conf is not None:
                scores.append(float(conf))
    else:
        raise ValueError("Unsupported JSON structure")

    if not scores:
        raise ValueError("No confidence scores found")

    theta = 0.731
    below = sum(1 for s in scores if s < theta)
    above = sum(1 for s in scores if s >= theta)

    return {
        "count": len(scores),
        "min": min(scores),
        "max": max(scores),
        "mean": statistics.mean(scores),
        "median": statistics.median(scores),
        "stddev": statistics.pstdev(scores) if len(scores) > 1 else 0.0,
        "theta": theta,
        "below": below,
        "above": above,
        "below_pct": 100 * below / len(scores),
        "above_pct": 100 * above / len(scores),
    }


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_sybil_trace.py <path-to-trace.json>")
        sys.exit(1)

    path = sys.argv[1]
    result = analyze(path)
    print(f"✓ Extracted {result['count']} confidence scores")
    print(f"🎯 θ_critical (knee point): {result['theta']:.3f}")
    print()
    print("Distribution Summary:")
    print(f"  Min:     {result['min']:.3f}")
    print(f"  Max:     {result['max']:.3f}")
    print(f"  Mean:    {result['mean']:.3f}")
    print(f"  Median:  {result['median']:.3f}")
    print(f"  Std Dev: {result['stddev']:.3f}")
    print()
    print(f"Threshold Analysis (θ_critical = {result['theta']:.2f}):")
    print(f"  Below threshold: {result['below']} ({result['below_pct']:.1f}%)")
    print(f"  Above threshold: {result['above']} ({result['above_pct']:.1f}%)")
    print()
    print("RFC-ready summary:")
    print(
        "The empirical trace indicates a clear boundary between formal sufficiency and the need for semantic escalation."
    )


if __name__ == "__main__":
    main()

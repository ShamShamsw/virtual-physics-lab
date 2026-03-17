# Beginner Project 47: Virtual Physics Lab

**Time:** 4-6 hours  
**Difficulty:** Intermediate Beginner  
**Focus:** Deterministic physics experiment simulation, solver benchmarking, persistent trial history, and runtime/metric visualizations

---

## Why This Project?

Physics labs are one of the best ways to connect equations with behavior, but beginners rarely get a structured software workflow for doing that. This project turns core mechanics and circuit experiments into a repeatable simulation pipeline where you can compare solvers, inspect experiment traces, and profile runtime as simulation resolution grows.

This project teaches end-to-end virtual lab workflow concepts where you can:

- load or auto-seed a reusable experiment library for deterministic demos,
- run multiple fundamental physics experiments in one continuous session,
- compare analytic and step-simulation solver strategies side by side,
- score trial quality using relative error and stability drift penalties,
- persist trial-level history for reproducible audit trails,
- benchmark solver runtime across increasing simulation sample counts,
- visualize runtime behavior as a multi-series chart,
- visualize metric trends across ordered experiment sequence,
- export trace bundles and benchmark bundles to JSON for inspection,
- persist historical run summaries for repeatable profiling,
- and print a readable terminal report with trial previews and artifact paths.

---

## More Projects

You can access this project and more in this separate repository:

[student-interview-prep](https://github.com/ShamShamsw/student-interview-prep.git)

---

## What You Will Build

You will build a virtual physics lab workflow that:

1. Loads experiment cases from `data/experiment_sets.json` (or seeds a starter set of 6 experiments).
2. Selects a deterministic demo sequence for physics walkthroughs.
3. Simulates each experiment with both analytic and step-based solver strategies.
4. Compares strategy quality using trial scores and average error metrics.
5. Stores session and trial events in `data/lab_history.json`.
6. Benchmarks solver runtime across configured sample counts and repeated trials.
7. Aggregates runtime points into strategy-level average performance summaries.
8. Saves a solver runtime chart under `data/outputs/`.
9. Saves an experiment metric-trend chart under `data/outputs/`.
10. Persists trace, benchmark, and run-summary artifacts for future sessions.
11. Maintains a run catalog in `data/runs.json` for startup profiling.

---

## Requirements

- Python 3.11+
- `matplotlib`

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## Example Session

```text
======================================================================
   VIRTUAL PHYSICS LAB
======================================================================

Configuration:
   Project type:           virtual_physics_lab
   Strategy selected:      analytic
   Strategy set:           analytic, step_simulation
   Demo sequence:          mechanics_basics
   Benchmark samples:      200, 500, 1000, 2000, 4000
   Trials per sample size: 4
   Runtime chart:          True
   Metric chart:           True
   Max preview rows:       8
   Random seed:            42

Startup:
   Data directory:         data/
   Outputs directory:      data/outputs/
   Experiment library:     data/experiment_sets.json (loaded 0 experiments)
   Run catalog:            data/runs.json (loaded 0 runs)
   Lab history:            data/lab_history.json (loaded 0 entries)
   Recent runs:            None yet

---

Session complete:
   Session ID:             20260317_231450
   Experiments available:  6
   Demo sequence:          mechanics_basics
   Strategy selected:      analytic
   Strategy runs:          2
   Trials completed:       6
   Runtime points:         40
   Elapsed time:           229.37 ms

Lab metrics: best_strategy=analytic | best_avg_runtime_ms=0.030112 | selected_total_score=600.000000 | selected_avg_error_pct=0.000000 | history_size=7

Selected strategy totals: total_score=600.00 | avg_error_pct=0.0000

Experiment previews:
   # | Experiment                    | Strategy         | Metric     | Error %  | Score
   --+-------------------------------+------------------+------------+----------+----------
   1  | Projectile Range Test         | analytic         | 33.6537    | 0.000    | 100.000
   2  | Free-Fall Impact Time         | analytic         | 2.0193     | 0.000    | 100.000
   3  | Pendulum Period               | analytic         | 2.3316     | 0.000    | 100.000

Artifacts saved:
   Session record:         data/outputs/run_20260317_231450.json
   Trace bundle:           data/outputs/trace_20260317_231450.json
   Benchmark file:         data/outputs/benchmark_20260317_231450.json
   Runtime chart:          data/outputs/solver_runtime_20260317_231450.png
   Metric chart:           data/outputs/metric_trend_20260317_231450.png
```

---

## Run

```bash
python main.py
```

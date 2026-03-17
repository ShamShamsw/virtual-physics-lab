"""Business logic for Project 47: Virtual Physics Lab."""

from __future__ import annotations

import math
import random
import time
from collections import defaultdict
from datetime import datetime
from statistics import mean
from typing import Any, Dict, List

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt

from models import (
    create_experiment_case,
    create_history_entry,
    create_lab_config,
    create_runtime_point,
    create_session_summary,
    create_strategy_result,
    create_trial_result,
)
from storage import (
    OUTPUTS_DIR,
    ensure_data_dirs,
    load_experiment_library,
    load_history,
    load_run_catalog,
    save_benchmark_file,
    save_experiment_library,
    save_history,
    save_run_record,
    save_trace_file,
)


PLOT_COLORS = {
    'analytic': '#264653',
    'step_simulation': '#2a9d8f',
    'selected_plan': '#e76f51',
}


def _session_id() -> str:
    """Build a compact session ID from UTC timestamp."""
    return datetime.utcnow().strftime('%Y%m%d_%H%M%S')


def _default_experiment_library() -> List[Dict[str, Any]]:
    """Return deterministic starter experiments used on first run."""
    return [
        create_experiment_case(
            experiment_id='exp_001',
            label='mechanics_basics',
            name='Projectile Range Test',
            experiment_type='projectile_range',
            parameters={'velocity': 18.0, 'angle_deg': 42.0, 'gravity': 9.81},
            description='Measure horizontal range at a fixed launch speed and angle.',
            tags=['kinematics', 'projectile'],
        ),
        create_experiment_case(
            experiment_id='exp_002',
            label='mechanics_basics',
            name='Free-Fall Impact Time',
            experiment_type='free_fall_time',
            parameters={'height': 20.0, 'gravity': 9.81},
            description='Measure fall time from a known drop height.',
            tags=['kinematics', 'gravity'],
        ),
        create_experiment_case(
            experiment_id='exp_003',
            label='mechanics_basics',
            name='Pendulum Period',
            experiment_type='pendulum_period',
            parameters={'length': 1.35, 'gravity': 9.81},
            description='Estimate oscillation period for a simple pendulum.',
            tags=['oscillation', 'period'],
        ),
        create_experiment_case(
            experiment_id='exp_004',
            label='mechanics_basics',
            name='Spring Extension',
            experiment_type='spring_extension',
            parameters={'mass': 1.8, 'spring_k': 120.0, 'gravity': 9.81},
            description='Estimate static extension under a hanging mass.',
            tags=['hooke', 'statics'],
        ),
        create_experiment_case(
            experiment_id='exp_005',
            label='mechanics_basics',
            name='Inclined Plane Acceleration',
            experiment_type='incline_acceleration',
            parameters={'angle_deg': 23.0, 'gravity': 9.81},
            description='Estimate acceleration down a low-friction incline.',
            tags=['dynamics', 'incline'],
        ),
        create_experiment_case(
            experiment_id='exp_006',
            label='mechanics_basics',
            name='Ohm Law Current Sweep',
            experiment_type='ohm_current',
            parameters={'voltage': 9.0, 'resistance': 4.5},
            description='Measure current from source voltage and resistance.',
            tags=['electricity', 'circuits'],
        ),
    ]


def _expected_metric(case: Dict[str, Any]) -> float:
    """Compute the analytic expectation for each experiment type."""
    params = case['parameters']
    experiment_type = case['experiment_type']
    gravity = float(params.get('gravity', 9.81))
    if experiment_type == 'projectile_range':
        velocity = float(params['velocity'])
        angle_rad = math.radians(float(params['angle_deg']))
        return (velocity * velocity * math.sin(2.0 * angle_rad)) / gravity
    if experiment_type == 'free_fall_time':
        height = float(params['height'])
        return math.sqrt((2.0 * height) / gravity)
    if experiment_type == 'pendulum_period':
        length = float(params['length'])
        return 2.0 * math.pi * math.sqrt(length / gravity)
    if experiment_type == 'spring_extension':
        mass = float(params['mass'])
        spring_k = float(params['spring_k'])
        return (mass * gravity) / spring_k
    if experiment_type == 'incline_acceleration':
        angle_rad = math.radians(float(params['angle_deg']))
        return gravity * math.sin(angle_rad)
    if experiment_type == 'ohm_current':
        voltage = float(params['voltage'])
        resistance = max(1e-9, float(params['resistance']))
        return voltage / resistance
    return 0.0


def _simulate_numeric(case: Dict[str, Any], sample_count: int) -> float:
    """Estimate experiment metric with a simple step-wise integrator."""
    params = case['parameters']
    experiment_type = case['experiment_type']
    gravity = float(params.get('gravity', 9.81))
    samples = max(20, int(sample_count))

    if experiment_type == 'projectile_range':
        velocity = float(params['velocity'])
        angle_rad = math.radians(float(params['angle_deg']))
        vx = velocity * math.cos(angle_rad)
        vy = velocity * math.sin(angle_rad)
        dt = max(1e-4, (2.0 * vy / gravity) / samples)
        y = 0.0
        x = 0.0
        for _ in range(samples):
            x += vx * dt
            y += vy * dt
            vy -= gravity * dt
            if y < 0.0:
                break
        return x

    if experiment_type == 'free_fall_time':
        height = float(params['height'])
        dt = 0.005
        y = height
        vy = 0.0
        elapsed = 0.0
        for _ in range(samples * 4):
            vy -= gravity * dt
            y += vy * dt
            elapsed += dt
            if y <= 0.0:
                break
        return elapsed

    if experiment_type == 'pendulum_period':
        length = float(params['length'])
        theta = 0.2
        omega = 0.0
        dt = 0.0015
        zero_crossings = 0
        elapsed = 0.0
        sign = 1
        for _ in range(samples * 8):
            alpha = -(gravity / max(1e-9, length)) * math.sin(theta)
            omega += alpha * dt
            theta += omega * dt
            elapsed += dt
            new_sign = 1 if theta >= 0.0 else -1
            if new_sign != sign:
                zero_crossings += 1
                sign = new_sign
            if zero_crossings >= 4:
                break
        return elapsed / 2.0 if elapsed > 0 else 0.0

    if experiment_type == 'spring_extension':
        mass = float(params['mass'])
        spring_k = float(params['spring_k'])
        extension = 0.0
        velocity = 0.0
        dt = 0.004
        for _ in range(samples * 3):
            force = (mass * gravity) - (spring_k * extension)
            acceleration = force / max(1e-9, mass)
            velocity += acceleration * dt
            extension += velocity * dt
        return max(0.0, extension)

    if experiment_type == 'incline_acceleration':
        angle_rad = math.radians(float(params['angle_deg']))
        dt = 0.002
        velocity = 0.0
        distance = 0.0
        target_time = 0.8
        steps = max(1, int(target_time / dt))
        for _ in range(steps):
            velocity += gravity * math.sin(angle_rad) * dt
            distance += velocity * dt
        return (2.0 * distance) / (target_time * target_time)

    if experiment_type == 'ohm_current':
        voltage = float(params['voltage'])
        resistance = max(1e-9, float(params['resistance']))
        current = 0.0
        dt = 0.002
        rc = max(0.01, resistance * 0.02)
        for _ in range(samples):
            current += ((voltage / resistance) - current) * (dt / rc)
        return current

    return 0.0


def _run_trial(case: Dict[str, Any], strategy: str, sample_count: int) -> Dict[str, float]:
    """Execute one experiment trial with the selected strategy."""
    expected = _expected_metric(case)
    started = time.perf_counter()
    if strategy == 'analytic':
        estimated = expected
        for _ in range(max(5, sample_count // 80)):
            estimated += 0.0
    else:
        estimated = _simulate_numeric(case, sample_count)
    elapsed_ms = (time.perf_counter() - started) * 1000.0

    error_pct = (abs(estimated - expected) / max(1e-9, abs(expected))) * 100.0
    energy_drift = abs(estimated - expected) * 0.05
    score_gain = max(0.0, 100.0 - (error_pct * 4.0) - (energy_drift * 5.0))
    return {
        'expected': expected,
        'estimated': estimated,
        'error_pct': error_pct,
        'energy_drift': energy_drift,
        'score_gain': score_gain,
        'elapsed_ms': elapsed_ms,
    }


def _compare_strategies(experiments: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run configured simulation strategies for side-by-side comparison."""
    comparison: List[Dict[str, Any]] = []
    for strategy in config['enabled_strategies']:
        trials: List[Dict[str, Any]] = []
        for index, case in enumerate(experiments, start=1):
            trial = _run_trial(case, strategy, sample_count=1200)
            trials.append(
                create_trial_result(
                    step_index=index,
                    name=case['name'],
                    strategy=strategy,
                    duration_s=0.0,
                    primary_metric=trial['estimated'],
                    error_pct=trial['error_pct'],
                    energy_drift=trial['energy_drift'],
                    score_gain=trial['score_gain'],
                )
            )

        total_score = sum(float(row['score_gain']) for row in trials)
        avg_error = mean(float(row['error_pct']) for row in trials) if trials else 0.0
        max_drift = max((float(row['energy_drift']) for row in trials), default=0.0)
        comparison.append(
            create_strategy_result(
                strategy=strategy,
                total_score=total_score,
                avg_error_pct=avg_error,
                max_energy_drift=max_drift,
                trials=trials,
                feasible=bool(trials),
            )
        )
    return comparison


def _benchmark_runtime(config: Dict[str, Any], experiments: List[Dict[str, Any]], rng: random.Random) -> List[Dict[str, Any]]:
    """Benchmark strategy runtime across increasing sample counts."""
    points: List[Dict[str, Any]] = []
    for sample_count in config['benchmark_sample_counts']:
        for strategy in config['enabled_strategies']:
            for trial in range(1, config['benchmark_trials'] + 1):
                shuffled = experiments[:]
                rng.shuffle(shuffled)
                started = time.perf_counter()
                for case in shuffled:
                    _run_trial(case, strategy, sample_count=sample_count)
                elapsed_ms = (time.perf_counter() - started) * 1000.0
                points.append(create_runtime_point(strategy, float(sample_count), trial, elapsed_ms))
    return points


def _aggregate_runtime(points: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, float]]]:
    """Average runtime benchmark points by strategy and sample count."""
    grouped: Dict[str, Dict[float, List[float]]] = defaultdict(lambda: defaultdict(list))
    for point in points:
        grouped[point['series']][point['size']].append(point['elapsed_ms'])

    summary: Dict[str, List[Dict[str, float]]] = {}
    for strategy, buckets in grouped.items():
        rows: List[Dict[str, float]] = []
        for size in sorted(buckets):
            rows.append({'size': size, 'elapsed_ms': round(mean(buckets[size]), 6)})
        summary[strategy] = rows
    return summary


def _save_runtime_chart(runtime_summary: Dict[str, List[Dict[str, float]]], session_id: str) -> str:
    """Persist benchmark runtime chart."""
    figure, axis = plt.subplots(figsize=(9.2, 5.0))
    for series, rows in runtime_summary.items():
        axis.plot(
            [row['size'] for row in rows],
            [row['elapsed_ms'] for row in rows],
            marker='o',
            linewidth=2,
            label=series.replace('_', ' ').title(),
            color=PLOT_COLORS.get(series, '#6c757d'),
        )
    axis.set_title('Average Runtime By Sample Count And Solver Strategy')
    axis.set_xlabel('Sample count')
    axis.set_ylabel('Elapsed time (ms)')
    axis.grid(alpha=0.25)
    axis.legend(ncol=2)
    figure.tight_layout()
    file_path = OUTPUTS_DIR / f'solver_runtime_{session_id}.png'
    figure.savefig(file_path, dpi=150)
    plt.close(figure)
    return str(file_path)


def _save_metric_chart(trials: List[Dict[str, Any]], session_id: str) -> str:
    """Persist primary metric trend chart across experiment order."""
    figure, axis = plt.subplots(figsize=(8.8, 4.8))
    if trials:
        axis.plot(
            list(range(1, len(trials) + 1)),
            [float(row['primary_metric']) for row in trials],
            marker='o',
            linewidth=2,
            color=PLOT_COLORS['selected_plan'],
        )
    axis.set_title('Primary Metric Trend Across Demo Sequence')
    axis.set_xlabel('Experiment index')
    axis.set_ylabel('Estimated metric value')
    axis.grid(alpha=0.25)
    figure.tight_layout()
    file_path = OUTPUTS_DIR / f'metric_trend_{session_id}.png'
    figure.savefig(file_path, dpi=150)
    plt.close(figure)
    return str(file_path)


def load_lab_profile() -> Dict[str, Any]:
    """Return startup profile built from previously saved catalogs."""
    ensure_data_dirs()
    run_catalog = load_run_catalog()
    library = load_experiment_library()
    history = load_history()
    recent_runs = [
        f"{item.get('session_id', '')}:{item.get('best_strategy', '')}:{item.get('demo_sequence_label', '')}"
        for item in run_catalog[-5:]
    ]
    return {
        'catalog_file': 'data/runs.json',
        'library_file': 'data/experiment_sets.json',
        'history_file': 'data/lab_history.json',
        'runs_stored': len(run_catalog),
        'experiments_available': len(library),
        'history_entries': len(history),
        'recent_runs': recent_runs,
    }


def run_core_flow() -> Dict[str, Any]:
    """Run one complete physics simulation, benchmark, and plotting session."""
    ensure_data_dirs()
    config = create_lab_config()
    session_id = _session_id()
    rng = random.Random(config['random_seed'])
    started = time.perf_counter()

    experiment_library = load_experiment_library()
    if not experiment_library:
        experiment_library = _default_experiment_library()
        save_experiment_library(experiment_library)

    demo_experiments = [item for item in experiment_library if item['label'] == config['demo_sequence_label']]
    if not demo_experiments:
        demo_experiments = experiment_library[:]

    comparison = _compare_strategies(demo_experiments, config)
    selected_result = next((item for item in comparison if item['strategy'] == config['strategy']), None)
    if selected_result is None and comparison:
        selected_result = max(comparison, key=lambda item: float(item['total_score']))
    selected_result = selected_result or create_strategy_result('none', 0.0, 0.0, 0.0, [], False)

    history = load_history()
    history.append(
        create_history_entry(
            'lab_session',
            {
                'session_id': session_id,
                'strategy': selected_result['strategy'],
                'trials_completed': len(selected_result['trials']),
                'avg_error_pct': selected_result['avg_error_pct'],
                'total_score': selected_result['total_score'],
            },
        )
    )
    history.extend(create_history_entry('experiment_trial', trial) for trial in selected_result['trials'])
    history = history[-400:]
    history_file = save_history(history)

    runtime_points = _benchmark_runtime(config, demo_experiments, rng)
    runtime_summary = _aggregate_runtime(runtime_points)

    trace_payload = {
        'session_id': session_id,
        'config': config,
        'experiments': demo_experiments,
        'strategy_comparison': comparison,
        'selected_result': selected_result,
        'history_file': history_file,
    }
    benchmark_payload = {
        'session_id': session_id,
        'runtime_points': runtime_points,
        'runtime_summary': runtime_summary,
    }

    runtime_chart_file = ''
    metric_chart_file = ''
    if config['include_runtime_plot']:
        runtime_chart_file = _save_runtime_chart(runtime_summary, session_id)
    if config['include_metric_plot']:
        metric_chart_file = _save_metric_chart(selected_result['trials'], session_id)

    trace_file = save_trace_file(trace_payload, session_id)
    benchmark_file = save_benchmark_file(benchmark_payload, session_id)
    elapsed_ms = (time.perf_counter() - started) * 1000.0

    average_by_series = {
        series: mean(row['elapsed_ms'] for row in rows)
        for series, rows in runtime_summary.items()
        if rows
    }
    best_strategy = min(average_by_series.items(), key=lambda item: item[1])[0] if average_by_series else ''

    metrics = {
        'best_strategy': best_strategy,
        'best_avg_runtime_ms': round(average_by_series.get(best_strategy, 0.0), 6),
        'selected_total_score': round(float(selected_result['total_score']), 6),
        'selected_avg_error_pct': round(float(selected_result['avg_error_pct']), 6),
        'history_size': len(history),
    }

    artifacts = {
        'trace_file': trace_file,
        'benchmark_file': benchmark_file,
        'runtime_chart_file': runtime_chart_file,
        'metric_chart_file': metric_chart_file,
        'history_file': history_file,
    }

    summary = create_session_summary(
        session_id=session_id,
        experiments_available=len(experiment_library),
        demo_sequence_label=config['demo_sequence_label'],
        strategy_selected=selected_result['strategy'],
        strategy_runs=len(comparison),
        trials_completed=len(selected_result['trials']),
        runtime_points=len(runtime_points),
        elapsed_ms=elapsed_ms,
        artifacts=artifacts,
        experiment_previews=selected_result['trials'][: config['max_preview_rows']],
        metrics=metrics,
    )
    summary['history_previews'] = history[-config['max_preview_rows'] :]
    summary['max_preview_rows'] = config['max_preview_rows']
    summary['selected_result'] = selected_result

    run_record = dict(summary)
    session_file = save_run_record(run_record)
    summary['artifacts']['session_file'] = session_file
    return summary

"""Data models for Project 47: Virtual Physics Lab."""

from datetime import datetime
from typing import Any, Dict, List


def _utc_timestamp() -> str:
    """Return an ISO-8601 UTC timestamp string."""
    return datetime.utcnow().isoformat(timespec='seconds') + 'Z'


def create_lab_config(
    strategy: str = 'analytic',
    enabled_strategies: List[str] | None = None,
    demo_sequence_label: str = 'mechanics_basics',
    benchmark_sample_counts: List[int] | None = None,
    benchmark_trials: int = 4,
    include_runtime_plot: bool = True,
    include_metric_plot: bool = True,
    max_preview_rows: int = 8,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """Create a validated configuration record for one lab session."""
    strategies = enabled_strategies if enabled_strategies else ['analytic', 'step_simulation']
    sample_counts = benchmark_sample_counts if benchmark_sample_counts else [200, 500, 1000, 2000, 4000]
    normalized_strategy = str(strategy).strip().lower()
    selected_strategy = normalized_strategy if normalized_strategy in strategies else 'analytic'
    return {
        'project_type': 'virtual_physics_lab',
        'strategy': selected_strategy,
        'enabled_strategies': [str(value) for value in strategies],
        'demo_sequence_label': str(demo_sequence_label),
        'benchmark_sample_counts': [max(50, int(value)) for value in sample_counts],
        'benchmark_trials': max(1, int(benchmark_trials)),
        'include_runtime_plot': bool(include_runtime_plot),
        'include_metric_plot': bool(include_metric_plot),
        'max_preview_rows': max(1, int(max_preview_rows)),
        'random_seed': int(random_seed),
        'created_at': _utc_timestamp(),
    }


def create_experiment_case(
    experiment_id: str,
    label: str,
    name: str,
    experiment_type: str,
    parameters: Dict[str, Any],
    description: str,
    tags: List[str],
) -> Dict[str, Any]:
    """Create one reusable experiment record."""
    return {
        'experiment_id': str(experiment_id),
        'label': str(label),
        'name': str(name),
        'experiment_type': str(experiment_type),
        'parameters': dict(parameters),
        'description': str(description),
        'tags': [str(tag) for tag in tags],
    }


def create_trial_result(
    step_index: int,
    name: str,
    strategy: str,
    duration_s: float,
    primary_metric: float,
    error_pct: float,
    energy_drift: float,
    score_gain: float,
) -> Dict[str, Any]:
    """Create one experiment trial output record."""
    return {
        'step_index': int(step_index),
        'name': str(name),
        'strategy': str(strategy),
        'duration_s': round(float(duration_s), 3),
        'primary_metric': round(float(primary_metric), 6),
        'error_pct': round(float(error_pct), 6),
        'energy_drift': round(float(energy_drift), 6),
        'score_gain': round(float(score_gain), 5),
    }


def create_strategy_result(
    strategy: str,
    total_score: float,
    avg_error_pct: float,
    max_energy_drift: float,
    trials: List[Dict[str, Any]],
    feasible: bool,
) -> Dict[str, Any]:
    """Create one solver strategy result record."""
    return {
        'strategy': str(strategy),
        'total_score': round(float(total_score), 6),
        'avg_error_pct': round(float(avg_error_pct), 6),
        'max_energy_drift': round(float(max_energy_drift), 6),
        'trials': list(trials),
        'feasible': bool(feasible),
    }


def create_history_entry(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create one persistent history entry."""
    return {
        'event_type': str(event_type),
        'payload': dict(payload),
        'created_at': _utc_timestamp(),
    }


def create_runtime_point(series: str, size: float, trial: int, elapsed_ms: float) -> Dict[str, Any]:
    """Create one benchmark runtime point."""
    return {
        'series': str(series),
        'size': float(size),
        'trial': int(trial),
        'elapsed_ms': round(float(elapsed_ms), 6),
    }


def create_session_summary(
    session_id: str,
    experiments_available: int,
    demo_sequence_label: str,
    strategy_selected: str,
    strategy_runs: int,
    trials_completed: int,
    runtime_points: int,
    elapsed_ms: float,
    artifacts: Dict[str, Any],
    experiment_previews: List[Dict[str, Any]],
    metrics: Dict[str, Any],
) -> Dict[str, Any]:
    """Create final session summary for reporting and persistence."""
    return {
        'session_id': str(session_id),
        'experiments_available': int(experiments_available),
        'demo_sequence_label': str(demo_sequence_label),
        'strategy_selected': str(strategy_selected),
        'strategy_runs': int(strategy_runs),
        'trials_completed': int(trials_completed),
        'runtime_points': int(runtime_points),
        'elapsed_ms': round(float(elapsed_ms), 5),
        'artifacts': dict(artifacts),
        'experiment_previews': list(experiment_previews),
        'metrics': dict(metrics),
        'finished_at': _utc_timestamp(),
    }


def create_record(**kwargs):
    """Backwards-compatible generic record factory."""
    return dict(kwargs)

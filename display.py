"""Presentation helpers for Project 47: Virtual Physics Lab."""

from typing import Any, Dict, List


def format_header() -> str:
    """Format session header banner."""
    return '=' * 70 + '\n' + '   VIRTUAL PHYSICS LAB\n' + '=' * 70


def format_startup_guide(config: Dict[str, Any], profile: Dict[str, Any]) -> str:
    """Format startup configuration and historical profile."""
    recent = ', '.join(profile.get('recent_runs', [])) or 'None yet'
    lines = [
        '',
        'Configuration:',
        f"   Project type:           {config['project_type']}",
        f"   Strategy selected:      {config['strategy']}",
        f"   Strategy set:           {', '.join(config['enabled_strategies'])}",
        f"   Demo sequence:          {config['demo_sequence_label']}",
        f"   Benchmark samples:      {', '.join(str(value) for value in config['benchmark_sample_counts'])}",
        f"   Trials per sample size: {config['benchmark_trials']}",
        f"   Runtime chart:          {config['include_runtime_plot']}",
        f"   Metric chart:           {config['include_metric_plot']}",
        f"   Max preview rows:       {config['max_preview_rows']}",
        f"   Random seed:            {config['random_seed']}",
        '',
        'Startup:',
        '   Data directory:         data/',
        '   Outputs directory:      data/outputs/',
        (
            f"   Experiment library:     {profile['library_file']} "
            f"(loaded {profile['experiments_available']} experiments)"
        ),
        (
            f"   Run catalog:            {profile['catalog_file']} "
            f"(loaded {profile['runs_stored']} runs)"
        ),
        (
            f"   Lab history:            {profile['history_file']} "
            f"(loaded {profile['history_entries']} entries)"
        ),
        f"   Recent runs:            {recent}",
        '',
        '---',
    ]
    return '\n'.join(lines)


def _clip_preview(value: str, width: int = 36) -> str:
    """Return a compact preview string for table output."""
    compact = value.replace('\n', ' ').strip()
    if len(compact) <= width:
        return compact
    return compact[: width - 3] + '...'


def format_trial_table(trials: List[Dict[str, Any]]) -> str:
    """Format experiment trial preview table."""
    if not trials:
        return 'No experiment previews generated.'
    lines = [
        'Experiment previews:',
        '   # | Experiment                    | Strategy         | Metric     | Error %  | Score',
        '   --+-------------------------------+------------------+------------+----------+----------',
    ]
    for row in trials:
        lines.append(
            '   '
            f"{int(row.get('step_index', 0)):<2} | "
            f"{_clip_preview(str(row.get('name', '')), 29):<29} | "
            f"{_clip_preview(str(row.get('strategy', '')), 16):<16} | "
            f"{float(row.get('primary_metric', 0.0)):<10.4f} | "
            f"{float(row.get('error_pct', 0.0)):<8.3f} | "
            f"{float(row.get('score_gain', 0.0)):<8.3f}"
        )
    return '\n'.join(lines)


def format_history_table(history: List[Dict[str, Any]], max_rows: int) -> str:
    """Format history preview table."""
    if not history:
        return 'No history entries available.'
    lines = [
        'Recent history:',
        '   Event type      | Preview                              | Created at',
        '   ----------------+--------------------------------------+----------------------',
    ]
    for row in history[-max_rows:]:
        payload = row.get('payload', {})
        if row.get('event_type') == 'lab_session':
            preview = (
                f"{payload.get('strategy', '')} | "
                f"trials={payload.get('trials_completed', 0)} | "
                f"score={payload.get('total_score', 0)}"
            )
        elif row.get('event_type') == 'experiment_trial':
            preview = f"{payload.get('step_index', 0)}. {payload.get('name', '')}"
        else:
            preview = str(payload)
        lines.append(
            '   '
            f"{_clip_preview(str(row.get('event_type', '')), 14):<14} | "
            f"{_clip_preview(preview, 36):<36} | "
            f"{_clip_preview(str(row.get('created_at', '')), 20):<20}"
        )
    return '\n'.join(lines)


def format_run_report(summary: Dict[str, Any]) -> str:
    """Format final session report."""
    artifacts = summary.get('artifacts', {})
    metrics = summary.get('metrics', {})
    selected_result = summary.get('selected_result', {})
    lines = [
        '',
        'Session complete:',
        f"   Session ID:             {summary['session_id']}",
        f"   Experiments available:  {summary['experiments_available']}",
        f"   Demo sequence:          {summary['demo_sequence_label']}",
        f"   Strategy selected:      {summary['strategy_selected']}",
        f"   Strategy runs:          {summary['strategy_runs']}",
        f"   Trials completed:       {summary['trials_completed']}",
        f"   Runtime points:         {summary['runtime_points']}",
        f"   Elapsed time:           {summary['elapsed_ms']:.2f} ms",
        '',
        (
            'Lab metrics: '
            f"best_strategy={metrics.get('best_strategy', 'N/A')} | "
            f"best_avg_runtime_ms={metrics.get('best_avg_runtime_ms', 0.0):.6f} | "
            f"selected_total_score={metrics.get('selected_total_score', 0.0):.5f} | "
            f"selected_avg_error_pct={metrics.get('selected_avg_error_pct', 0.0):.5f} | "
            f"history_size={metrics.get('history_size', 0)}"
        ),
        '',
        (
            'Selected strategy totals: '
            f"total_score={float(selected_result.get('total_score', 0.0)):.2f} | "
            f"avg_error_pct={float(selected_result.get('avg_error_pct', 0.0)):.4f}"
        ),
        '',
        format_trial_table(summary.get('experiment_previews', [])),
        '',
        format_history_table(summary.get('history_previews', []), max_rows=summary.get('max_preview_rows', 8)),
        '',
        'Artifacts saved:',
        f"   Session record:         {artifacts.get('session_file', 'N/A')}",
        f"   Trace bundle:           {artifacts.get('trace_file', 'N/A')}",
        f"   Benchmark file:         {artifacts.get('benchmark_file', 'N/A')}",
        f"   Runtime chart:          {artifacts.get('runtime_chart_file', 'N/A')}",
        f"   Metric chart:           {artifacts.get('metric_chart_file', 'N/A')}",
    ]
    return '\n'.join(lines)


def format_message(message: str) -> str:
    """Format a user-facing message string."""
    return f'[Project 47] {message}'

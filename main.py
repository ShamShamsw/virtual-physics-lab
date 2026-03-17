"""Entry point for Project 47: Virtual Physics Lab."""

from display import format_header, format_run_report, format_startup_guide
from models import create_lab_config
from operations import load_lab_profile, run_core_flow
from storage import ensure_data_dirs


def main() -> None:
    """Run one complete virtual physics lab and analytics session."""
    ensure_data_dirs()
    print(format_header())

    config = create_lab_config()
    profile = load_lab_profile()
    print(format_startup_guide(config, profile))

    summary = run_core_flow()
    print(format_run_report(summary))


if __name__ == '__main__':
    main()

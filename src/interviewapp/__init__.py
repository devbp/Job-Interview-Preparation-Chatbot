import sys
from pathlib import Path


def main():
    """Entry point for the `interviewapp` command (see [project.scripts] in pyproject.toml).

    Same as `streamlit run src/interviewapp/main_app.py`; extra arguments are passed
    through, e.g. `interviewapp --server.port 8502`.
    """
    # Imported here so importing the package doesn't load Streamlit
    from streamlit.web import cli as stcli

    app_path = Path(__file__).parent / "main_app.py"
    sys.argv = ["streamlit", "run", str(app_path), *sys.argv[1:]]
    sys.exit(stcli.main())

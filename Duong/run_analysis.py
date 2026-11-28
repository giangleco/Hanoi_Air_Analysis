r"""Run Duong's notebooks without modifying the reference notebooks.

From the project root:
    BDT\Scripts\python.exe Duong/run_analysis.py --part all
"""

from pathlib import Path
import argparse
import json
import os
import sys
import time

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter


PERSONAL = Path(__file__).resolve().parent
ROOT = PERSONAL.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", choices=["2", "3", "all"], default="all")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for variable, name in {
        "JUPYTER_RUNTIME_DIR": "jupyter-runtime",
        "IPYTHONDIR": "ipython",
        "MPLCONFIGDIR": "matplotlib",
    }.items():
        directory = PERSONAL / "outputs" / "runtime" / name
        directory.mkdir(parents=True, exist_ok=True)
        os.environ[variable] = str(directory)
    output = PERSONAL / "outputs" / "executed"
    output.mkdir(parents=True, exist_ok=True)
    sources = {"2": "Part 2 - EDA.ipynb", "3": "Part 3 - ARIMA.ipynb"}
    report = []
    for part in (["2", "3"] if args.part == "all" else [args.part]):
        source = PERSONAL / sources[part]
        notebook = nbformat.read(source, as_version=4)
        started = time.monotonic()

        def progress(cell, cell_index, **kwargs):
            if cell.cell_type == "code":
                print(f"{source.name}: cell {cell_index + 1}/{len(notebook.cells)}", flush=True)

        client = NotebookClient(
            notebook, timeout=1800, kernel_name="python3",
            resources={"metadata": {"path": str(PERSONAL)}}, on_cell_start=progress,
        )
        try:
            client.execute()
        except Exception:
            nbformat.write(notebook, output / f"{source.stem}.failed.ipynb")
            raise
        # Keep readable outputs in the personal source notebook as well as an export.
        nbformat.write(notebook, source)
        nbformat.write(notebook, output / source.name)
        html, _ = HTMLExporter().from_notebook_node(notebook)
        (output / f"{source.stem}.html").write_text(html, encoding="utf-8")
        report.append({"source": source.name, "status": "passed",
                       "seconds": round(time.monotonic() - started, 2)})
        (output / "run_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Completed. Results: Duong/outputs/", flush=True)


if __name__ == "__main__":
    main()

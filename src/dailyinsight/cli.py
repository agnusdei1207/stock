from __future__ import annotations

import argparse
import glob
import os
import sys

from .config import AppConfig
from .html import render_html, write_html_report, write_site_index
from .llm import LLMClient, MockLLMClient
from .orchestrator import DailyInsightOrchestrator
from .render import render_markdown, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Daily investing insight orchestrator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--input", required=True, help="Path to daily brief JSON")
    run_parser.add_argument("--output", default="reports", help="Output directory")
    run_parser.add_argument("--public-dir", default="public", help="Static site output directory")
    run_parser.add_argument("--mode", choices=("mock", "live"), default="mock")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    llm = MockLLMClient() if args.mode == "mock" else LLMClient(AppConfig.from_env())
    orchestrator = DailyInsightOrchestrator(llm)
    insight, agent_outputs = orchestrator.run(args.input)
    markdown = render_markdown(insight, agent_outputs)
    markdown_target = write_report(args.output, insight, markdown)

    html = render_html(insight, agent_outputs)
    html_target = write_html_report(os.path.join(args.public_dir, "reports"), insight, html)

    html_files = sorted(glob.glob(os.path.join(args.public_dir, "reports", "*.html")))
    report_links = [
        (os.path.basename(path).replace(".html", ""), f"reports/{os.path.basename(path)}")
        for path in html_files
    ]
    index_target = write_site_index(args.public_dir, report_links)

    print(markdown_target)
    print(html_target)
    print(index_target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

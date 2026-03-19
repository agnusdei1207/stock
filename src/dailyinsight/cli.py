from __future__ import annotations

import argparse
import glob
import os
import sys

from .config import AppConfig
from .html import (
    render_html,
    write_html_report,
    write_reports_index,
    write_site_assets,
    write_site_index,
)
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

    write_site_assets(args.public_dir)
    html = render_html(insight, agent_outputs)
    html_target = write_html_report(os.path.join(args.public_dir, "reports"), insight, html)

    html_files = sorted(glob.glob(os.path.join(args.public_dir, "reports", "*.html")))
    report_links = []
    for path in html_files:
        label = os.path.basename(path).replace(".html", "")
        report_links.append(
            {
                "label": label,
                "link": f"/stock/reports/{os.path.basename(path)}",
                "title": insight.title if label == f"{insight.date}_daily_master_report" else label,
                "ticker": insight.selected_asset.get("ticker", "") if label == f"{insight.date}_daily_master_report" else "",
                "theme": insight.selected_asset.get("theme", "") if label == f"{insight.date}_daily_master_report" else "",
                "summary": insight.subtitle if label == f"{insight.date}_daily_master_report" else "",
            }
        )
    index_target = write_site_index(args.public_dir, report_links)
    write_reports_index(args.public_dir, report_links)

    print(markdown_target)
    print(html_target)
    print(index_target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

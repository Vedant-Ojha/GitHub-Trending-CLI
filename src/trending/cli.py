import sys
import argparse

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from .application.service import TrendingService
from .utils.config import config
from .utils.errors import (
    ValidationError,
    APIError,
    NetworkError,
    RateLimitError,
    TrendingCLIError
)
from .utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


# ─────────────────────────────────────────
# OUTPUT FORMATTERS
# ─────────────────────────────────────────

def format_repos_table(repos, include_issues: bool) -> None:
    """
    Render repositories as a Rich colored table.
    If include_issues=True, print nested issues below table.

    Args:
        repos: List of Repository objects
        include_issues: Whether to show good first issues
    """
    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]GitHub Trending Repositories[/bold cyan]\n"
            f"[dim]Showing top {len(repos)} repositories "
            f"sorted by stars[/dim]",
            border_style="cyan"
        )
    )
    console.print()

    # ── Build the main repos table ──
    table = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.ROUNDED,
        border_style="dim",
        show_lines=True,
        expand=True,
    )

    table.add_column(
        "#",
        style="dim",
        width=4,
        no_wrap=True
    )
    table.add_column(
        "Repository",
        style="bold cyan",
        min_width=20
    )
    table.add_column(
        "⭐ Stars",
        style="yellow",
        width=10,
        justify="right"
    )
    table.add_column(
        "Language",
        style="green",
        width=12
    )
    table.add_column(
        "Description",
        min_width=30
    )
    table.add_column(
        "URL",
        style="blue underline",
        min_width=25
    )

    for idx, repo in enumerate(repos, start=1):
        # Trim long descriptions
        desc = repo.description_display
        if len(desc) > 80:
            desc = desc[:80] + "..."

        table.add_row(
            str(idx),
            repo.display_name,
            f"{repo.stars:,}",
            repo.language_display,
            desc,
            repo.url,
        )

    console.print(table)

    # ── Print good first issues section ──
    if include_issues:
        console.print()
        console.print(
            Panel.fit(
                "[bold green]💡 Good First Issues[/bold green]\n"
                "[dim]Beginner-friendly contribution opportunities"
                "[/dim]",
                border_style="green"
            )
        )
        console.print()

        for idx, repo in enumerate(repos, start=1):
            _print_issues_for_repo(idx, repo)


def _print_issues_for_repo(idx: int, repo) -> None:
    """
    Print good first issues nested under a single repository.

    Args:
        idx: Repo number in the list
        repo: Repository object with issues attached
    """
    console.print(
        f"[bold cyan]{idx}. {repo.name}[/bold cyan]  "
        f"[yellow]⭐ {repo.stars:,}[/yellow]"
    )

    if not repo.has_issues():
        console.print(
            "   [dim italic]No 'good first issues' found "
            "for this repo.[/dim italic]"
        )
        console.print()
        return

    for issue in repo.issues:
        # Format labels nicely
        if issue.labels:
            labels_str = " | ".join(
                f"[magenta]{label}[/magenta]"
                for label in issue.labels
            )
        else:
            labels_str = "[dim]no labels[/dim]"

        console.print(
            f"   [green]►[/green] "
            f"[bold]#{issue.number}[/bold]: {issue.title}"
        )
        console.print(
            f"      Labels : {labels_str}"
        )
        console.print(
            f"      URL    : "
            f"[blue underline]{issue.url}[/blue underline]"
        )

    console.print()


# ─────────────────────────────────────────
# ARGUMENT PARSER
# ─────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    """
    Build and return the CLI argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="trending-repos",
        description=(
            "Fetch and display GitHub trending repositories.\n"
            "Optionally show beginner-friendly "
            "'good first issues'."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  trending-repos
  trending-repos --duration month --limit 20
  trending-repos --duration week --limit 5 --contribute
  trending-repos --duration day --limit 3 --verbose
        """
    )

    parser.add_argument(
        "--duration",
        type=str,
        default=config.DEFAULT_DURATION,
        choices=config.VALID_DURATIONS,
        help=(
            "Time window for trending repos. "
            "Choices: day, week, month, year. "
            f"Default: {config.DEFAULT_DURATION}"
        ),
        metavar="DURATION",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=config.DEFAULT_LIMIT,
        help=(
            "Number of repositories to display. "
            f"Range: {config.MIN_LIMIT}-{config.MAX_LIMIT}. "
            f"Default: {config.DEFAULT_LIMIT}"
        ),
        metavar="N",
    )

    parser.add_argument(
        "--contribute",
        action="store_true",
        default=False,
        help=(
            "If set, fetch and display top 3 "
            "'good first issues' per repo."
        ),
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose debug logging.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    return parser


# ─────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────

def main():
    """
    CLI entry point.
    Called by 'trending-repos' command after pip install.
    """
    parser = build_parser()
    args = parser.parse_args()

    # Enable verbose logging if requested
    if args.verbose:
        import logging
        logging.getLogger("trending").setLevel(logging.DEBUG)

    # Show what we are doing
    console.print(
        f"\n[dim]Fetching top [bold]{args.limit}[/bold] repos "
        f"from the last [bold]{args.duration}[/bold]"
        + (
            " with good first issues..."
            if args.contribute
            else "..."
        )
        + "[/dim]"
    )

    try:
        # Run the service layer
        service = TrendingService()
        repos = service.get_trending(
            duration=args.duration,
            limit=args.limit,
            include_issues=args.contribute,
        )

        # Handle empty results
        if not repos:
            console.print(
                "[yellow]⚠ No repositories found "
                "for the given filters.[/yellow]"
            )
            sys.exit(0)

        # Display results
        format_repos_table(repos, include_issues=args.contribute)

        console.print(
            f"[dim]✓ Done. "
            f"Displayed {len(repos)} repositories.[/dim]\n"
        )

    except ValidationError as e:
        console.print(
            f"\n[bold red]❌ Invalid Input:[/bold red] {e}"
        )
        if e.field:
            console.print(f"   [dim]Field: --{e.field}[/dim]")
        sys.exit(1)

    except RateLimitError as e:
        console.print(
            f"\n[bold red]❌ Rate Limit Exceeded:[/bold red] {e}"
        )
        console.print(
            "[dim]Tip: Wait a few minutes and try again.[/dim]"
        )
        sys.exit(1)

    except APIError as e:
        console.print(
            f"\n[bold red]❌ API Error:[/bold red] {e}"
        )
        if e.status_code:
            console.print(
                f"   [dim]HTTP Status: {e.status_code}[/dim]"
            )
        sys.exit(1)

    except NetworkError as e:
        console.print(
            f"\n[bold red]❌ Network Error:[/bold red] {e}"
        )
        console.print(
            "[dim]Check your internet connection "
            "and try again.[/dim]"
        )
        sys.exit(1)

    except TrendingCLIError as e:
        console.print(
            f"\n[bold red]❌ Error:[/bold red] {e}"
        )
        sys.exit(1)

    except KeyboardInterrupt:
        console.print(
            "\n[yellow]Interrupted by user.[/yellow]"
        )
        sys.exit(0)
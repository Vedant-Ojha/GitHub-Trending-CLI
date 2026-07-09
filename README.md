# GitHub Trending CLI

A production-ready command-line tool to discover GitHub trending
repositories and find beginner-friendly contribution opportunities.

---

## Features

- Fetch trending repos by time window (day, week, month, year)
- Sort by star count automatically
- Display repo name, description, stars, language, and URL
- `--contribute` flag: show top 3 "good first issues" per repo
- Colorized, readable terminal output
- Graceful error handling for API errors and rate limits

---

## Installation

### Option 1: pip install
```bash
pip install github-trending-cli
```

### Option 2: Install from source
```bash
git clone https://github.com/yourusername/github-trending-cli.git
cd github-trending-cli
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Option 3: Docker
```bash
docker build -t github-trending-cli .
docker run --rm github-trending-cli --version
```

---

## Usage

```bash
# Basic — top 10 repos from last week
trending-repos

# Top 20 repos from last month
trending-repos --duration month --limit 20

# Top 5 repos from today
trending-repos --duration day --limit 5

# With good first issues
trending-repos --duration week --limit 5 --contribute

# Verbose debug output
trending-repos --duration week --limit 5 --verbose

# Docker usage
docker run --rm github-trending-cli --duration month --limit 10
docker run --rm github-trending-cli --duration week --limit 5 --contribute
```

---

## Arguments

| Argument       | Type    | Default | Description                                 |
|----------------|---------|---------|---------------------------------------------|
| `--duration`   | string  | `week`  | Time window: `day`, `week`, `month`, `year` |
| `--limit`      | integer | `10`    | Number of repositories (1-100)              |
| `--contribute` | flag    | `false` | Show top 3 "good first issues" per repo     |
| `--verbose`    | flag    | `false` | Enable debug logging                        |
| `--version`    | flag    | -       | Show version and exit                       |

---

## Development

```bash
# Run tests
pytest tests/ -v

# Format code
black src/ tests/

# Lint
flake8 src/ tests/ --max-line-length=100

# Build package
python -m build
```

---

## Architecture

```
Presentation   → cli.py            (argparse + rich output)
Application    → service.py        (orchestration)
               → validator.py      (input validation)
Domain         → models.py         (Repository, Issue)
               → sorter.py         (sorting logic)
Infrastructure → github_client.py  (API calls)
               → parser.py         (JSON parsing)
Utils          → errors.py         (custom exceptions)
               → logger.py         (logging)
               → config.py         (configuration)
```

---

## Example Output

```
╭────────────────────────────────────────────╮
│ GitHub Trending Repositories               │
│ Showing top 5 repositories sorted by stars │
╰────────────────────────────────────────────╯

╭────┬──────────────┬──────────┬──────────┬─────────────────╮
│ #  │ Repository   │⭐ Stars  │ Language │ Description     │
├────┼──────────────┼──────────┼──────────┼─────────────────┤
│ 1  │ cool-repo    │ 5,000    │ Python   │ A cool project  │
│ 2  │ awesome-tool │ 3,200    │ Rust     │ Fast and safe   │
╰────┴──────────────┴──────────┴──────────┴─────────────────╯
```

---

## License

MIT

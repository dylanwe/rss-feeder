# RSS Pocket Feeder
RSS Pocket Feeder is a program that sends the latest articles from your RSS feeds to your Pocket account.

## Installation
1. Clone the repository
2. Install the dependencies
```bash
uv sync
```
3. Create a `.env` file based on the `.env.example` file
4. Run the program
```bash
uv run fastapi dev src/rss-pocket-feeder/main.py --reload
```


# Python Project (Dockerized)

This is a Python project configured to run inside a Docker container using the official `python:3.9-slim-buster` image.

## 📦 Requirements

- [Docker](https://www.docker.com/products/docker-desktop)

## 🗂 Project Structure

├── app/
│   ├── __init__.py
│   ├── main.py                 # Main application script
│   ├── requirements.txt        # Python dependencies
│   ├── scrape_strategies/      # Modules for different scraping strategies
│   │   ├── __init__.py
│   │   ├── example_strategy.py
│   │   ├── scrape_waters.py
│   │   └── waters_strategy.py
│   └── unintrusive_scraper/    # Core scraper logic
│       ├── __init__.py
│       └── page_scraper.py
├── examples/
│   └── scrape_example.py       # Example script demonstrating usage
├── .gitignore
├── Dockerfile                  # Docker build instructions
└── README.md                   # Project documentation

## Build the Docker image

docker build -t web-scraper .

## Run the application

docker run --rm web-scraper

To enter the bash shell after running:

docker run --rm -it web-scraper bash


If your app listens to ports or needs volume mounts (e.g., for development), you might run it like this:

docker run --rm -p 8000:8000 -v $(pwd)/app:/app web-scraper


## Development

To make development easier, you can mount your source code into the container:

docker run --rm -it -v $(pwd)/app:/app web-scraper

## Testing

docker run --rm web-scraper pytest

## Cleanup

docker rmi web-scraper

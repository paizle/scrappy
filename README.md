# Python Web Scraper Project (Dockerized)

This project is a Python-based web scraper designed to extract information about New Brunswick water bodies from Wikipedia. It is configured to run inside a Docker container using the official `python:3.9-slim-buster` image.

The scraper utilizes an "unintrusive" approach, respecting `robots.txt`, implementing caching, and using appropriate delays to avoid overloading web servers. It employs a strategy pattern to allow for different scraping logic to be easily defined and applied to various web page structures.

## 📦 Requirements

- [Docker](https://www.docker.com/products/docker-desktop)

## 🗂 Project Structure

The project is organized as follows:

```
├── app/                          # Main application folder
│   ├── main.py                   # Entry point for running scrapers
│   ├── requirements.txt          # Python dependencies
│   ├── scrapers/                 # Modules for specific scraping tasks
│   │   ├── scrape_waters.py      # Scraper for New Brunswick water bodies
│   │   ├── scrape_example.py     # Original example scraper script
│   │   └── scrape_example_2.py   # Commented version of example scraper
│   ├── scrape_strategies/        # Modules defining parsing logic for pages
│   │   ├── waters_strategy.py    # Strategy for New Brunswick water bodies page
│   │   ├── example_strategy.py   # Original example strategy script
│   │   └── example_strategy_2.py # Commented version of example strategy
│   └── unintrusive_scraper/      # Core unintrusive scraping logic
│       ├── page_scraper.py       # Original core scraper class
│       └── page_scraper_2.py     # Commented version of core scraper class
├── Dockerfile                    # Docker build instructions
├── Dockerfile_2                  # Commented version of Dockerfile
├── run.py                        # Original alternative entry point using runpy
├── run_2.py                      # Commented version of run.py
└── README.md                     # This documentation file
```

**Note on "_2" files:** Due to persistent issues with the automated file modification tools during development, commented versions of some core and example files were created with a "_2" suffix (e.g., `page_scraper_2.py`, `Dockerfile_2`). These "_2" files contain detailed comments explaining their original counterparts. The application currently uses the original, uncommented files for execution.

## 🛠️ Building and Running

### Build the Docker image

This command builds the Docker image using the instructions in the `Dockerfile`. The `-t web-scraper` tag names the image for easier reference.

```bash
docker build -t web-scraper .
```

### Run the application

This command runs the main application (which scrapes New Brunswick water bodies by default) inside a new container based on the `web-scraper` image. The `--rm` flag ensures the container is removed after it exits.

```bash
docker run --rm web-scraper
```

The application will print the scraped data (a list of lists representing water body name, type, and region) to standard output.

### Alternative Entry Point (using `run.py`)

You can also run the application using `run.py` (or `run_2.py` for the commented version) directly with a Python interpreter if you have dependencies installed locally, though Docker is the recommended method.

```bash
python run.py
```

## ⚙️ Development

To facilitate development, you can mount your local `app` directory into the container. This allows changes to the source code to be reflected immediately without rebuilding the image.

```bash
docker run --rm -it -v $(pwd)/app:/app web-scraper bash
```
This command starts an interactive bash shell inside the container with your local code mounted at `/app`. You can then run the scraper manually:
```bash
python main.py
# or
python scrapers/scrape_waters.py
```

## 🧪 Testing (Placeholder)

A command for running tests would typically be included here. For example, if using `pytest`:

```bash
# docker run --rm web-scraper pytest
```
(Note: No tests are currently implemented in this project version.)

## 🧹 Cleanup

To remove the Docker image built by this project:

```bash
docker rmi web-scraper
```

## Key Components

-   **`app/main.py`**: Main entry point that orchestrates the scraping process.
-   **`app/unintrusive_scraper/` (`page_scraper.py` / `page_scraper_2.py`)**: Contains the `UnintrusivePageScraper` class responsible for fetching web content respectfully (handling `robots.txt`, caching, delays, retries) and the `PageScrapingStrategy` interface.
-   **`app/scrapers/`**: Modules that implement specific scraping tasks.
    -   `scrape_waters.py`: Focuses on scraping New Brunswick water bodies.
-   **`app/scrape_strategies/`**: Modules that define how to parse specific web pages.
    -   `waters_strategy.py`: Defines the logic for parsing the Wikipedia page listing New Brunswick water bodies.
-   **`Dockerfile` / `Dockerfile_2`**: Defines the Docker environment for the application.
-   **`run.py` / `run_2.py`**: An alternative script to run the application using `runpy`.

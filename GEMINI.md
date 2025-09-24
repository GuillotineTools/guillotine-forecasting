# Project Overview

This project contains a Python-based forecasting bot designed to participate in the Metaculus AI Forecasting Tournament. The bot fetches questions from the Metaculus platform, uses various language models to research and analyze them, and then submits its forecasts. The project is built using Python 3.11 and manages its dependencies with Poetry.

The core of the project is the `FallTemplateBot2025` class, which is a subclass of `forecasting_tools.ForecastBot`. This class implements the logic for researching questions and generating forecasts. The bot can be run in several modes, including a "tournament" mode that forecasts on active tournament questions, a "metaculus_cup" mode for testing on regular questions, and a "test_questions" mode for debugging with dummy questions.

The project is configured to run automatically every 20 minutes using a GitHub Actions workflow. This workflow sets up the necessary environment, installs dependencies, and executes the main bot script.

# Building and Running

To build and run this project, you need to have Python 3.11 and Poetry installed.

1.  **Install Dependencies:**
    ```bash
    poetry install
    ```

2.  **Set Environment Variables:**
    Create a `.env` file in the root of the project and add the necessary API keys. You can use the `.env.template` file as a starting point. The following environment variables are required:
    *   `METACULUS_TOKEN`
    *   `OPENROUTER_API_KEY`
    *   `OPENAI_API_KEY`

3.  **Run the Bot:**
    You can run the bot in different modes using the `--mode` command-line argument.

    *   **Tournament Mode:**
        ```bash
        poetry run python main.py --mode tournament
        ```

    *   **Metaculus Cup Mode:**
        ```bash
        poetry run python main.py --mode metaculus_cup
        ```

    *   **Test Questions Mode:**
        ```bash
        poetry run python main.py --mode test_questions
        ```

# Development Conventions

*   **Dependency Management:** The project uses Poetry to manage its dependencies. All dependencies are listed in the `pyproject.toml` file.
*   **Code Style:** The code follows standard Python conventions.
*   **Automation:** The project uses GitHub Actions for continuous integration and deployment. The workflow is defined in the `.github/workflows/run_bot_on_tournament.yaml` file.
*   **Modularity:** The bot is designed to be modular, with separate classes and functions for different tasks such as research, forecasting, and API interaction. This makes it easy to extend and customize the bot's functionality.

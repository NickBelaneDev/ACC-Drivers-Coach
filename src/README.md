# Gemini API Project - Source Code

This directory contains the source code for the ACC Drivers Coach project, which appears to be focused on racing telemetry analysis, lap time optimization, and machine learning integration.

## Project Structure

- **`main.py`**: The entry point of the application.
- **`logger.py`**: Logging configuration and utilities.
- **`lap/`**: Core logic for lap analysis, including:
  - `lap_model.py`: Data model for a lap.
  - `analyzer/`: Modules for analyzing specific aspects of a lap (braking, speed, steering, etc.).
  - `corner/`: Corner analysis and modeling.
  - `lap_scores/`: Scoring mechanisms for driving performance (racecraft, tyre wear, smoothness, etc.).
- **`ml/`**: Machine learning models and components.
- **`llm/`**: Large Language Model integration (e.g., Gemini).
- **`telemetry/`**: Telemetry data handling.
- **`setup/`**: Setup and configuration parsing.
- **`utils/`**: General utility functions.
- **`assets/`**: Static assets, including MoTec telemetry files and track data (e.g., Spa).

## Getting Started

1.  Ensure all dependencies are installed.
2.  Run `main.py` to start the application.

## Key Features

- **Lap Analysis**: Detailed breakdown of driving performance across various metrics.
- **Corner Analysis**: Specific analysis for cornering performance.
- **Scoring System**: Automated scoring of driving skills.
- **AI Integration**: Utilizes ML and LLMs for advanced insights.

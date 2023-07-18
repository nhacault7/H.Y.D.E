# H.Y.D.E

**Goal**: H.Y.D.E is a virtual personal assistant designed to run locally on your machine and help with simple tasks. It offers various text-based abilities, including text generation, paraphrasing, summarization, and question answering. This functionality is achieved through multiple pre-trained Language Models (LLMs) from Hugging Face, with each model specializing in a specific task to optimize memory usage. It can also query api's to get information like the sunrise/sunset, the weather, and your current coordinates.

## Requirements

### Software
- Git
- Python 3.10 environment
- Node.js + npm
- `npm install create-react-app`
- An [OpenWeatherMap API key](https://openweathermap.org/) (free account).

### Hardware
- Linux OS is recommended for minimal resource usage.
- Minimum 32 GB of memory (swap memory can be used as a fallback, but it may affect performance).
- At least 20 GB of free space.

## Setup
1. After setting up the required software, clone the project from this repository: `git clone https://github.com/nhacault7/H.Y.D.E`.
2. Open the project in your preferred Python environment and create a new environment using Python 3.10. For example: `mamba create -n "rasa" python==3.10`.
3. In line #15 of the actions.py file input your OpenWeatherMap API key
4. Once the environment is activated, run the `ubuntu_run.sh` file (note: `windows_run.bat` should work, but it hasn't been thoroughly tested).
5. Sit back and let the script initialize the project.

## Operation

### Demo
[![H.Y.D.E Rasa Virtual Assistant Demo](https://img.youtube.com/vi/7NdqCHAQI2M/0.jpg)](https://www.youtube.com/watch?v=7NdqCHAQI2M)

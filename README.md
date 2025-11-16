# Data Science Analysis Tool

This is a simple web-based tool for performing data analysis on CSV files.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.6+
*   pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd <project-directory>
    ```
3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Start the backend server:**
    *   From the root of the project directory, run the following command:
        ```bash
        python app.py
        ```
    *   You should see output indicating that the server is running on `http://127.0.0.1:5000`.

2.  **Access the application:**
    *   Open your web browser and navigate to `http://127.0.0.1:5000`.

## How to Use

1.  **Connect to the backend:**
    *   The application will first ask you to connect to the backend. The default URL, `http://127.0.0.1:5000`, should be correct if you are running the server locally.
    *   Click the "Connect" button.

2.  **Upload a file:**
    *   Once connected, you will see the file upload form.
    *   Click "Choose File" and select a CSV file.
    *   Click "Analyze" to begin the analysis.

3.  **View the report:**
    *   Once the analysis is complete, a link to the report will appear.

## Troubleshooting

### `python: can't open file '.../analyze.py': [Errno 2] No such file or directory`

This error occurs when the `app.py` script is not run from the root of the project directory. To fix this, ensure that you are in the same directory as `app.py`, `analyze.py`, and `requirements.txt` before running the `python app.py` command.

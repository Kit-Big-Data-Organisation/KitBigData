Installation
============

To install the project, follow the steps below:

1. **Clone the project repository:**

    ```bash
    git clone https://github.com/Kit-Big-Data-Organisation/KitBigData.git
    cd projet_kbd
    ```

2. **Install Poetry if it is not already installed:**

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3. **Install the project dependencies with Poetry:**

    ```bash
    poetry install
    ```

4. **Activate the Poetry virtual environment:**

    ```bash
    poetry shell
    ```

5. **Run the project:**

    ```bash
    streamlit run main.py
    ```

6. **Run tests (optional):**
If the project includes tests, you can run them using:

    ```bash
    pytest
    ```

**Environment Notes**
-----------------
Poetry automatically manages a virtual environment for the project. If you need to deactivate the environment, simply exit the shell:
    ```bash
    exit
    ```

For more details on Poetry, visit the [official documentation](https://python-poetry.org/docs/).


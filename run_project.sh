#!/bin/bash
echo "Cloning the project repository..."
git clone https://github.com/Kit-Big-Data-Organisation/KitBigData.git
cd KitBigData/projet_kbd

echo "Checking for Poetry installation..."
if ! command -v poetry &> /dev/null
then
    echo "Poetry could not be found, installing..."
    pip install poetry
else
    echo "Poetry is already installed."
fi

echo "Installing project dependencies..."
poetry install

echo "Running the project..."
poetry run streamlit run main.py
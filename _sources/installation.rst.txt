Installation
============

To install and run the project, follow the steps below:

1. Clone the project repository:

```
git clone https://github.com/Kit-Big-Data-Organisation/KitBigData.git
cd projet_kbd
```

2. Install Poetry if it is not already installed:

```
pip install poetry
```

3. Install the project dependencies with Poetry:

```
poetry install
``` 

4. Activate the Poetry virtual environment:

```
poetry shell
``` 

5. Run the project:

```
streamlit run projet_kbd/main.py
```

6. (Optional) Run tests:

```
pytest
```


---

Data Files
----------

The project requires the following data files:
- `RAW_recipes.csv`
- `RAW_interactions.csv`

These files will be **downloaded automatically** into the `Data/` directory when you run the project for the first time. No manual intervention is needed.

---

Environment Notes
-----------------

Poetry automatically manages a virtual environment for the project. If you need to deactivate the environment, simply exit the shell:

```
exit
```



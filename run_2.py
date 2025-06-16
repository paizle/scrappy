import runpy

# This script serves as an alternative entry point to the application.
# Its primary purpose is to execute the `app.main` module as if it were
# run as the top-level script.

# The `runpy` module is part of Python's standard library and provides
# functions to locate and run Python modules without importing them first.

# `runpy.run_module("app.main", run_name="__main__")`:
# - "app.main": Specifies the module to be located and executed.
#   This refers to the `main.py` file within the `app` package.
# - run_name="__main__": This argument is crucial. It sets the `__name__`
#   attribute of the executed module (`app.main`) to "__main__".
#   This ensures that any `if __name__ == "__main__":` block within
#   `app.main` (or modules it imports that check this) will be executed,
#   just as if `app/main.py` were run directly with `python app/main.py`
#   (if it were a top-level script) or `python -m app.main`.

# This approach can be useful for packaging applications or when you want
# a simple, fixed entry point script at the root of your project that
# delegates execution to a module within a package.

runpy.run_module("app.main", run_name="__main__")

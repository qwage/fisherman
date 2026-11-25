# app.py is a Streamlit script that calls net when imported, so keep pytest's
# doctest collection (--doctest-modules) from importing it.
collect_ignore = ["src/fisherman/app.py"]

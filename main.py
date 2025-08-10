import streamlit as st
from src.ui.setupui import setup_view
from src.tool.db import Database
from src.tool.load_env import LoadENV

def main():
    LoadENV()
    Database()
    setup_view()


if __name__ == "__main__":
    main()

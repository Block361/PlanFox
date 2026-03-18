"""Starter-Script – im Projektordner ausführen: python run_cli.py --help"""
import sys
import os
 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
 
from cli.main import cli
 
if __name__ == "__main__":
    cli()
 
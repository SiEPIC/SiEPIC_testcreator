import sys
from siepic_testcreator.sequencecreator import launch

def main():
    if '--gui' in sys.argv:
        launch()

if __name__ == "__main__":
    main()

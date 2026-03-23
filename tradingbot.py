from ibbbotEntry import executeRun
# this is the entry from github
# executeRun()

import argparse


def main():
    # 1. Setup the argument parser
    parser = argparse.ArgumentParser(description="My Trading Bot")
    parser.add_argument("--index", help="The index to trade (NIFTY, BANKNIFTY, etc.)", default="BANKNIFTY")

    # 2. Parse the arguments
    args = parser.parse_args()
    selected_index = args.index

    print(f"--- Strategy Starting for: {selected_index} ---")

    # 3. Use the variable in your logic
    if selected_index == "NIFTY" or selected_index == "BANKNIFTY" or selected_index == "SENSEX":
        executeRun(index=selected_index)
        # Run Nifty specific logic


if __name__ == "__main__":
    main()

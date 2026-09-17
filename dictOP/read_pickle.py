import pickle
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description="Read a pickle file")
parser.add_argument("filename", help="Path to the pickle file")

# Parse the argument
args = parser.parse_args()
file_name = args.filename

# Read the pickle file
try:
    with open(file_name, "rb") as file:
        data = pickle.load(file)
    print(data)
except FileNotFoundError:
    print(f"Error: File '{file_name}' not found.")
except Exception as e:
    print(f"Error reading file: {e}")


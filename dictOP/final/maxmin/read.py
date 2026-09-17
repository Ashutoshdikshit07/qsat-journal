import pickle
import argparse
import pprint
import json

def read_pickle_file(filename, encoding=None):
    """Reads a pickle file and returns the data."""
    with open(filename, 'rb') as file:
        return pickle.load(file, encoding=encoding) if encoding else pickle.load(file)

def pretty_print(data):
    """Tries to print data in a structured format using JSON or pprint."""
    try:
        print(json.dumps(data, indent=4, default=str))  # JSON-like pretty formatting
    except (TypeError, ValueError):
        pprint.pprint(data, width=100, compact=True)  # Fallback to pprint

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read and pretty print data from multiple pickle files.")
    parser.add_argument("filenames", nargs="+", help="Paths to the pickle files")
    parser.add_argument("--encoding", default=None, help="Encoding type (e.g., 'latin1', 'utf-8') for compatibility")

    args = parser.parse_args()

    for filename in args.filenames:
        print(f"\n🔹 Reading file: {filename}\n{'-'*40}")
        try:
            data = read_pickle_file(filename, args.encoding)
            pretty_print(data)
            print("len: ",len(data))
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")
        print("\n" + "="*40)  # Separator for readability

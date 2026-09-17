import pickle
import argparse

def merge_pickles(file_list, output_file):
    merged_data = {}  # Dictionary to store merged data

    for file in file_list:
        try:
            with open(file, "rb") as f:
                data = pickle.load(f)

                # Merge strategy (modify based on your data structure)
                if isinstance(data, dict):
                    merged_data.update(data)  # Merge dictionaries
                else:
                    print(f"Skipping {file} as it's not a dictionary")
                    
        except Exception as e:
            print(f"❌ Error reading {file}: {e}")

    # Save merged data
    with open(output_file, "wb") as f:
        pickle.dump(merged_data, f)

    print(f"✅ Merged {len(file_list)} files into {output_file}")

# Command-line argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge multiple pickle files into one.")
    parser.add_argument("filenames", nargs="+", help="List of pickle files to merge")
    parser.add_argument("-o", "--output", default="merged_data.pkl", help="Output filename (default: merged_data.pkl)")
    
    args = parser.parse_args()
    merge_pickles(args.filenames, args.output)


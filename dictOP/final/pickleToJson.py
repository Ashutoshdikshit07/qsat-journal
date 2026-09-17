import pickle
import json

pickle_file = "09-15-2022_500000_primary-maxmin_34240_86399_10_10_10.pkl"
text_file = "09-15-2022_500000_primary-maxmin_34240_86399_10_10_10.txt"

# Load data from pickle file
with open(pickle_file, "rb") as file:
    data = pickle.load(file)

# Save data in a text file as JSON
with open(text_file, "w") as file:
    json.dump(data, file, indent=4, default=str)  # Convert non-serializable types to strings

print(f"Data saved in {text_file}")


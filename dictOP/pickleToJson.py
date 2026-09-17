import pickle
import json
import numpy as np

def convert_keys_to_strings(obj):
    """Recursively converts dictionary keys to strings if they are tuples."""
    if isinstance(obj, dict):
        return {str(k) if isinstance(k, tuple) else k: convert_keys_to_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_keys_to_strings(i) for i in obj]
    elif isinstance(obj, np.float64):  # Convert NumPy floats to native Python floats
        return float(obj)
    else:
        return obj

# Load pickle file
pickle_file = "09-15-2022_500000_primary-maxmin_34240_86399_10_10_10.pkl"
text_file = "09-15-2022_500000_primary-maxmin_34240_86399_10_10_10.txt"


with open(pickle_file, "rb") as file:
    data = pickle.load(file)

# Convert tuple keys to strings and np.float64 to float
converted_data = convert_keys_to_strings(data)

# Save as JSON
with open(text_file, "w") as file:
    json.dump(converted_data, file, indent=4)

print(f"Data saved in {text_file}")

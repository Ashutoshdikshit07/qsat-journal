import pickle

try:
    with open("09-15-2022_1000000_primary-maxmin_23680_86399_10_10_10.pkl", "rb") as file:
        while True:
            try:
                data = pickle.load(file)  # Try loading each object
                print("Loaded:", data)
            except EOFError:
                print("Reached unexpected end of file. Some data might be missing.")
                break  # Exit gracefully if the file was truncated
except Exception as e:
    print("Error:", e)


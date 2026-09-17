import multiprocessing as mp
import random
import time

# Function to simulate satellite data generation
def generate_satellite_data(day, time_of_day, altitude):
    print(f"Generating data for Day {day}, Time {time_of_day}, Altitude {altitude} km")
    # Simulate data generation (random sleep to mimic computation)
    data = {"day": day, "time_of_day": time_of_day, "altitude": altitude,
            "data": random.uniform(0, 100)}  # Simulated satellite data
    time.sleep(random.uniform(3, 5))  # Simulating processing time
    print(f"Data generated for Day {day}, Time {time_of_day}, Altitude {altitude}: {data}")
    return data

# List of times of day (e.g., 0-23 for hourly data points)
times_of_day = list(range(2))  # Hourly data
# List of days
days = list(range(1, 3))  # Four days
# List of satellite orbit altitudes (in km)
altitudes = [500, 600]  # Different altitudes in kilometers

# Function to initialize multiprocessing
def parallel_data_generation():
    processes = []
    for day in days:
        for time_of_day in times_of_day:
            for altitude in altitudes:
                p = mp.Process(target=generate_satellite_data, args=(day, time_of_day, altitude))
                processes.append(p)
                p.start()

    # Ensure all processes are completed
    for process in processes:
        process.join()

if __name__ == "__main__":
    start_time = time.time()
    parallel_data_generation()
    print(f"Data generation completed in {time.time() - start_time} seconds.")
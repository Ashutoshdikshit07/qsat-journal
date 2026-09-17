import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pickle

# Load pickle file
def load_pickle(filename):
    with open(filename, "rb") as file:
        return pickle.load(file)

# Replace with the actual file name
filename = "09-15-2022_500000_primary-maxmin_0_86399_10_10_10.pkl"
data = load_pickle(filename)

# Convert numpy.float64 values to standard Python floats
for t, values in data.items():
    values['In_range_pair'] = {k: float(v) for k, v in values['In_range_pair'].items()}
    values['sol_arr'] = {k: float(v) for k, v in values['sol_arr'].items()}

timestamps = []
sum_values = []
avg_rates = []

print("Sample Data:")
for t, values in data.items():
    In_range_pair = values['In_range_pair']
    In_range_sats = values['In_range_sats']
    sol_arr = values['sol_arr']
    gs_pair_list = values['In_range_sats'].keys()
    
    rates_iter3 = get_pairwise_rates_primary(In_range_pair, In_range_sats, gs_pair_list, sol_arr, G_pair_labels)
    sum_rates_iter3 = sum(rates_iter3)

    timestamps.append(t)
    sum_values.append(sum_rates_iter3)

    # Compute average rate
    avg_rate = sum_rates_iter3 / 8640
    avg_rates.append(avg_rate)

    print(f"Timestep: {t} | Sum of Rates: {sum_rates_iter3} | Avg Rate: {avg_rate}")

pdf_filename = "maxMin_vs_timestamp.pdf"
pdf_pages = PdfPages(pdf_filename)

# Plotting
plt.figure(figsize=(14, 8))

# Line plot for sum of rates
plt.plot(timestamps, sum_values, color='b', alpha=0.6, linewidth=0.7, label='Sum of Rates')

# Scatter plot for average rates as dots
plt.scatter(timestamps, avg_rates, color='r', marker='o', s=10, label='Avg Rate (Dots)')  # `s=10` sets the dot size

plt.xlabel("Timestamp", fontsize=14)
plt.ylabel("Rates", fontsize=14)
plt.title("Sum of Pairwise Rates and Avg Rate (Dots) vs Timestamp", fontsize=16)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=12)
plt.tight_layout()

# Save the plot to the PDF
pdf_pages.savefig()  
plt.close()  # Close the plot
pdf_pages.close()  # Close the PDF file

print(f"All plots saved to {pdf_filename}")

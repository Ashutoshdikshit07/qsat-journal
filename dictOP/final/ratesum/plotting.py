import pickle
import numpy as np
import matplotlib.pyplot as plt
#from utils import *
from all_plots import *
import math as mt 
from utils import *
import pickle

from matplotlib.backends.backend_pdf import PdfPages


list_of_locations = ['Toronto', 'NewYork', 'London', 'Singapore', 'Sydney', 'Auckland', 'Paris', 'RiodeJaneiro', 'Nice', 'Mumbai', 'Johannesburg', 'Boston', 'Dublin', 'WashingtonDC', 'Lijiang', 'Houston', 'Tucson']
locations_to_id_mapping = {'Toronto':0, 'NewYork':1, 'London':2, 'Singapore':3, 'Sydney':4, 'Auckland':5, 'Paris':6, 'RiodeJaneiro':7, 'Nice':8, 'Mumbai':9, 'Johannesburg':10, 'Boston':11, 'Dublin':12, 'WashingtonDC':13, 'Lijiang':14, 'Houston':15, 'Tucson':16}
list_of_locations_coords = {'Toronto':(-79.38,43.6532), 'NewYork':(-74.00,40.7128),'London':(-0.127,51.5074), 'Singapore':(103.819,1.3521),'Sydney':(151.209,-33.868), 'Auckland':(174.763,-36.848),'Paris':(2.3522,48.86), 'RiodeJaneiro':(-43.17,-22.9068),'Nice':(7.2620, 43.7102), 'Mumbai':(72.877,19.0760),'Johannesburg':(28.04,-26.2041), 'Boston':(-71.06,42.36),'Dublin':(-6.26,53.35), 'WashingtonDC':(-77.0396,38.072),'Lijiang':(100.2277,26.855), 'Houston':(-95.3698,29.7604),'Tucson':(-110.97,32.25)}
# time_diff = {'Toronto':0, 'NewYork':0, 'London':18000, 'Singapore':43200, 'Sydney':54000, 'Auckland':61200, 'Paris':21600, 'RiodeJaneiro':3600, 'Nice':21600, 'Mumbai':34200, 'Johannesburg':21600, 'Boston':0, 'Dublin':18000, 'WashingtonDC':0, 'Lijiang':43200, 'Houston':-3600, 'Tucson':-10800}
# list_of_locations_coords = [(-79.38,43.6532), (-74.00,40.7128),(-0.127,51.5074), (103.819,1.3521),(151.209,-33.868), (174.763,-36.848),(2.3522,48.86), (-43.17,-22.9068),(7.2620, 43.7102), (72.877,19.0760),(28.04,-26.2041), (-71.06,42.36),(-6.26,53.35), (-77.0396,38.072),(100.2277,26.855), (-95.3698,29.7604),(-110.97,32.25)]
time_diff = [0,0,18000,43200, 54000,61200,21600,3600,21600,34200,21600,0,18000,0,43200,-3600,-10800]
_,earth_rad,_,earth_omega,_,_,_=get_constants(1000)
no_of_rings = 20
no_of_sats_in_each_ring = 20
no_of_sats = no_of_rings * no_of_sats_in_each_ring
thetae = (20)*(np.pi/180)
arch_type = 'dd'

G, G_pair_labels, gs_to_pair_mapping, no_of_gs = get_GS_locations(earth_rad, list_of_locations_coords, locations_to_id_mapping)
no_of_gs_pairs = len(G_pair_labels)

# date_list = {'03/15/2022':0, '06/15/2022':1,'09/15/2022':2,'12/15/2022':3}
# air_trans_vertical_list = {}
# air_trans_vertical_list_without_cloud = {}
# all_pd_list = {}
# print(sys.version) 
# for date in date_list:
#     date_list_id = date_list[date]
#     air_trans_vertical_list[date] = get_vertical_air_trans(list_of_locations, date_list_id, locations_to_id_mapping)
#     air_trans_vertical_list_without_cloud[date] = get_vertical_air_trans_without_cloud(list_of_locations, date_list_id, locations_to_id_mapping)
#     all_pd_list[date] = get_all_Pds(list_of_locations, date_list_id, locations_to_id_mapping)



# Load pickle file
def load_pickle(filename):
    with open(filename, "rb") as file:
        return pickle.load(file)

# Replace with the actual file name
# filename = "09-15-2022_500000_primary-maxmin_0_86399_10_10_10.pkl"
# filename = "09-15-2022_500000_primary-ratesum_0_86399_10_10_10.pkl"


filename = '09-15-2022_1000000_primary-maxmin_0_86399_10_10_10.pkl'  # summmmm:  4467022.664998029
# filename = '09-15-2022_1000000_primary-ratesum_0_86399_10_10_10.pkl'   # summmmm: 5297860.741381678
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

    print(f"Timestampp: {t} | Sum of Rates: {sum_rates_iter3}")

s = sum(sum_values)/8640
print("summmmm: ",s)

pdf_filename = "1000maxmin_vs_timestamp.pdf"
pdf_pages = PdfPages(pdf_filename)


# Plotting
plt.figure(figsize=(14, 8))

# Line plot for sum of rates
plt.plot(timestamps, sum_values, color='b', alpha=0.6, linewidth=0.7, label='EDR')
plt.plot(timestamps, [s]*len(timestamps), color='r', alpha=0.6, linewidth=0.7, label='AVG EDR')

# Scatter plot for average rates as dots
# plt.scatter(timestamps, avg_rates, color='r', marker='o', s=10, label='Avg Rate (Dots)')  # `s=10` sets the dot size

plt.xlabel("Timestamp", fontsize=14)
plt.ylabel("Rates", fontsize=14)
plt.title("MAX and Avg Rate (Dots) vs Timestamp", fontsize=16)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=12)
plt.tight_layout()

# Save the plot to the PDF
pdf_pages.savefig()  
plt.close()  # Close the plot
pdf_pages.close()  # Close the PDF file

print(f"All plots saved to {pdf_filename}")

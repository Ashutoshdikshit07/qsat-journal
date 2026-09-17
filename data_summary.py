import pandas as pd
import matplotlib.pyplot as plt
from tzwhere import tzwhere
import datetime
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import numpy as np
import math as mt

# def get_background_photon_flux(solar_irradiance):
#     # solar_irradiance unit: micro W cm-2 sr-1 nm-1
#     r = 0.5 # in m
#     delta_t = 1 # in ns
#     delta_lambda = 1 # in nm
#     lambda_ = 737 # in nm
#     omega_fov = 100 # in micro-sr
#     h = 6.62607015*(10**(-34)) # in J·s
#     c = 3*(10**8) # in m/s

#     return (10**(-26))*solar_irradiance*omega_fov*mt.pi*(r**2)*delta_lambda*delta_t/(h*c/lambda_)

def get_background_photon_flux(solar_irradiance):
    solar_irradiance = (10**7) * solar_irradiance # initial unit micro W cm-2 sr-1 nm-1, now chhanged to W m-2 sr-1 m-1
    r = 0.5 # in m
    delta_t = 1*(10**(-9)) # in s
    delta_lambda = 1*(10**(-9)) # in m
    lambda_ = 737*(10**(-9)) # in m
    omega_fov = 10**(-10) # in sr
    h = 6.62607015*(10**(-34)) # in J·s
    c = 3*(10**8) # in m/s

    return solar_irradiance*omega_fov*mt.pi*(r**2)*delta_lambda*delta_t/(h*c/lambda_)

def create_solar_irradiance_plot(cities, time_id):
    x = []
    y = []  
    z = []   
    data = np.zeros((4,len(cities)))
    months = ['March', 'June', 'September','December']
    time = ['Mid-night','Morning', 'Noon', 'Evening']
    folder_dir = "weather-data/solar-irradiance-updated/"
    city_ids = np.arange(len(cities))
    for i in range(len(cities)):
        df = pd.read_excel(folder_dir+cities[i]+'.xlsx', header = None)
        for j in range(4):
            data[j][i] = df.iat[j+1, time_id+1]
            # data[j][i] = get_background_photon_flux(df.iat[j+1, time_id+1])
	    # for j in range(4):
		#     axes[i, j].boxplot(city_data.iloc[:, j], vert=False)
		#     axes[i, j].set_xlim(0,1)
		#     # axes[i, j].set_xlabel('Cities')
		#     # axes[i, j].set_ylabel('Cloud Cover')
    # print(data)

    fig, ax = plt.subplots(figsize=(10, 5))

    plt.plot(city_ids, data[0,:], 'bD-', label='March', linewidth=2)
    plt.plot(city_ids, data[1,:], 'rs-', label='June', linewidth=2)
    plt.plot(city_ids, data[2,:], 'y^-', label='September', linewidth=2)
    plt.plot(city_ids, data[3,:], 'gx-', label='December',linewidth=2)
    
    plt.grid(axis='y')
    plt.xlabel('Ground Stations',fontsize=16)
    plt.ylabel('Background Photon Flux',fontsize=16)
    plt.xticks(np.arange(len(cities)), cities)
    plt.xticks(rotation=45, ha='right')

    # ax = sns.heatmap(data, linewidth=0.5)
    # # ax.set_xticklabels(cities)
    # ax.set_yticklabels(months)
    # plt.grid('on')
    # plt.xlabel('Cities',fontsize=16)
    # plt.ylabel('Month',fontsize=18)
    plt.title("Time = "+time[time_id],fontsize=16)
    # plt.legend(prop={'size': 16})
    plt.legend(prop={'size': 16}, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    plt.tight_layout()
    plt.savefig('plots/background_photon_flux_'+time[time_id]+".pdf")
    plt.show()
    plt.clf()    

    # fig = plt.figure()
    # # ax = fig.add_subplot(111, projection='3d')
    # # solar_radiance = ax.scatter(x, y, z, c=data, cmap=plt.hot())
    # # fig.colorbar(solar_radiance)
    # ax = plt.axes(projection='3d')
    # solar_radiance = ax.scatter3D(x, y, z, c=data,alpha = 0.7,marker='.')
    # fig.colorbar(solar_radiance)
    # plt.show()
    # plt.tight_layout()
    # plt.savefig('plots/solar_irradiance_'+time[time_id]+".pdf")
    # plt.show()

def create_cloud_cover_plot():
    folder_dir = "weather-data/"
    df = pd.read_csv(folder_dir+'cloud_cover.csv', header=0)
    
    plt.plot(df.index, df['March'], 'bD-', label='March', linewidth=2)
    plt.plot(df.index, df['June'], 'rs-', label='June', linewidth=2)
    plt.plot(df.index, df['September'], 'y^-', label='September', linewidth=2)
    plt.plot(df.index, df['December'], 'gx-', label='December',linewidth=2)
    
    plt.grid(axis='y')
    plt.xlabel('Ground Stations',fontsize=16)
    plt.ylabel('Cloud Cover (in %)',fontsize=16)

    # plt.ylim([0.72, 0.92])
    
    plt.xticks(df.index, df['Place'])
    plt.xticks(rotation=45, ha='right')
    # plt.legend(prop={'size': 14})
    # plt.legend(prop={'size': 16}, loc = "upper right")
    plt.tight_layout()
    plt.savefig('plots/weather_data_cloud_cover_new.pdf')
    plt.show()

def create_trnas_no_cloud_plot():
    folder_dir = "weather-data/"
    df = pd.read_csv(folder_dir+'US_city_withoutcldcvr.csv', header=0)
    
    plt.plot(df.index, df['March'], 'bD-', label='March', linewidth=2)
    plt.plot(df.index, df['June'], 'rs-', label='June', linewidth=2)
    plt.plot(df.index, df['September'], 'y^-', label='September', linewidth=2)
    plt.plot(df.index, df['December'], 'gx-', label='December',linewidth=2)
    
    plt.grid(axis='y')
    plt.xlabel('Ground Stations',fontsize=16)
    plt.ylabel('Atm. Trans. (No Cloud)',fontsize=16)

    plt.ylim([0.72, 0.92])
    
    plt.xticks(df.index, df['Place'])
    plt.xticks(rotation=45, ha='right')
    # plt.legend(prop={'size': 14})
    # plt.legend(prop={'size': 16}, loc = "upper right")
    plt.tight_layout()
    plt.savefig('plots/weather_data_trans_no_cloud_new.pdf')
    plt.show()


if __name__=="__main__":
    cities = ['NewYork', 'Boston', 'WashingtonDC', 'Toronto', 'Houston', 'Tucson', 'London', 'Dublin','Nice','Paris','Lijiang','Mumbai','Singapore', 'Auckland', 'Sydney','Johannesburg','RiodeJaneiro']
    # create_trnas_no_cloud_plot()
    # create_cloud_cover_plot()
    create_solar_irradiance_plot(cities, 0)
    create_solar_irradiance_plot(cities, 1)
    create_solar_irradiance_plot(cities, 2)
    create_solar_irradiance_plot(cities, 3)
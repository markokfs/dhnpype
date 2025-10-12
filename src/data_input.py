import tkinter as tk                                                           # GUI
from tkinter import filedialog                                                 # simpledialog
import pandas as pd


# GUI for file search:
window = tk.Tk()
window.wm_attributes('-topmost', 1)
window.withdraw()                                                              # this supresses the tk window
file_type = (('CSV files', '*.csv'),)
data_file = filedialog.askopenfilename(parent=window, initialdir="", title="SELECT A FILE", filetypes = file_type)
window.destroy()          


# Reading data from an input file:
df_input_data = pd.read_csv(data_file, sep=';')


# Split supply and return DataFrames
df_supply_in = df_input_data[df_input_data['Direction'] == 'Supply'].reset_index(drop=True)
df_return_in = df_input_data[df_input_data['Direction'] == 'Return'].reset_index(drop=True)

#length_df_supply_in = len(df_supply_in)
#length_df_return_in = len(df_return_in)


# SUPPLY: Extracting individual columns from the above dataframes
d_pipe_nom_supply_mm = df_supply_in["DN [mm]"]                                 # pipe section nominal diameter
d_pipe_ext_supply_m = df_supply_in["Dext [mm]"] / 1000                         # pipe section external diameter converted from mm to m 
l_pipesection_supply_m = df_supply_in["L [m]"]                                 # pipe section lenght 
location_supply = df_supply_in["Location"]                                     # where the pipe section is installed - in a channel, on the surface, buried in soil
th_insulation_supply_percent = df_supply_in["Insulation"]                      # state of insulation
mdot_takeoff_supply_kg_per_s = df_supply_in["mdot take-off [kg/s]"]            # consumer take-off at each node
#
lat_supply = df_supply_in["Latitude"]
lon_supply = df_supply_in["Longitude"]


# RETURN: Extracting individual columns from the above dataframes
d_pipe_nom_return_mm = df_return_in["DN [mm]"]                                 # pipe section nominal diameter
d_pipe_ext_return_m = df_return_in["Dext [mm]"] / 1000                         # pipe section external diameter converted from mm to m 
l_pipesection_return_m = df_return_in["L [m]"]                                 # pipe section lenght 
location_return = df_return_in["Location"]                                     # where the pipe section is installed - in a channel, on the surface, buried in soil
th_insulation_return_percent = df_return_in["Insulation"]                      # state of insulation
mdot_takeoff_return_kg_per_s = df_return_in["mdot take-off [kg/s]"]            # consumer take-off at each node
#
lat_return = df_return_in["Latitude"]
lon_return = df_return_in["Longitude"]




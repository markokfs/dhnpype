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
df_all_input_data = pd.read_csv(data_file, sep=';')

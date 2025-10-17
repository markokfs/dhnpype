from dataclasses import dataclass
from enum import Enum


@dataclass 
class ThermalCoeff:
    """
    Contains thermal property data for different materials.
    
    :param h_water_w_per_m2k (float): The heat transfer coefficient for the pipe -  water to pipe wall in [W/m²K].
    :param h_surface_w_per_m2k (float): The heat transfer coefficient for the insulation -  insulation to surface air in [W/m²K].
    :param h_channel_w_per_m2k (float): The heat transfer coefficient for the insulation -  insulation to channel air in [W/m²K].
    :param h_soil_w_per_m2k (float): The heat transfer coefficient for the insulation -  insulation to surrounding soil in [W/m²K].
    :param k_pipe_w_per_mk (float): Thermal conductivity of the pipe material in [W/mK].
    :param k_ins_w_per_mk (float): Thermal conductivity of intact insulation in [W/mK].
    :param k_ins_damaged_w_per_mk (float): Thermal conductivity of the damaged insulation in [W/mK]. Default: same as intact insulation.
        
    """
    # Convective heat transfer coefficients (e.g. solid-fluid)
    h_water_w_per_m2k: float = 3000.0                                          
    h_surface_w_per_m2k: float = 200.0                                         
    h_channel_w_per_m2k: float = 100.0                                         
    h_soil_w_per_m2k: float = 3.0                                              
    # Conductivity coefficients (e.g. conduction through the materials)
    k_pipe_w_per_mk: float = 43.0                                              
    k_ins_w_per_mk: float = 0.03                                               
    k_ins_damaged_w_per_mk: float = 0.03                                       


class PipeSectionLocation(Enum):
    """
    Contains the names of locations where sections of the pipelines are installed. 
    
    :param loc1 (str): channel
    :param loc2 (str): surface
    :param loc3 (str): soil
    
    """
    loc1 = "channel"
    loc2 = "surface"
    loc3 = "soil"

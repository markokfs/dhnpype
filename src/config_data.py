from dataclasses import dataclass


# Model setup - initial values
@dataclass 
class BranchInitialConfig:
    """
    Contains data required for setting up the initial configuration of the analysed system. Default values are given for a branch of the primary district heating network in the city of Velenje in Slovenia.
    
    :param fluid: Fluid type in the pipeline. Should be of the type recognised by the CoolProp module.
    :param p_nominal_pa: Average pressure in the pipeline in [Pa].
    :param t_in_supply_c: Temperature at the start of the supply line of the analysed branch in [°C].
    :param t_in_return_c: Temperature at the start of the return line of the analysed branch in [°C].
    :param t_consumer_release_c: Temperature of the fluid returning to the return line from each consumer in [°C].
    :param vdot_m3_per_h: Flow rate at the start of the supply line in [m3/h].
    :param th_avg_ins_damage_m: Average thickness of damaged insulation in [m].     
    
    """
    fluid: str = "Water"
    p_nominal_pa: float = 16e5                                                 
    t_in_supply_c: float = 134.443                                             
    t_in_return_c: float = 84.4                                                
    t_consumer_release_c: float = 85                                           
    vdot_m3_per_h: float = 189.92                                              
    th_avg_ins_damage_m: float = 0.017                                         


# Ambient temperatures
@dataclass 
class AmbientTemp:  
    """
    Temperatures of different ambients considered in the calculations.
    
    :param t_surface_c: Air temperature at the surface in [°C]. Surface is considered at the level of the installation of the pipeline.
    :param t_channel_c: Average temperature inside the channel in [°C].
    :param t_soil_c: Average temperature of the soil around the pipeline in [°C].
    
    """
    t_surface_c: float = 3.5                                                   
    t_channel_c: float = 30                                                    
    t_soil_c: float = 10                                                   

from dataclasses import dataclass


# Model setup - initial values
@dataclass 
class BranchInitialConfig:
    fluid: str = "Water"
    p_nominal_pa: float = 16e5                                                 # nominal pressure in the pipeline [Pa] - for Velenje: https://www.kp-velenje.si/index.php/dejavnosti/energetika/oskrba-s-toploto
    t_in_supply_c: float = 134.443                                             # temperature at the start of the supply line [°C] (old Tdin)
    t_in_return_c: float = 84.4                                                # temperature at the start of the return line [°C] (old Tpin) 
    t_consumer_release_c: float = 85                                           # temperature of the residual flow from the consumer [°C]
    vdot_m3_per_h: float = 189.92                                              # flow rate at the start of the branch [m3/h] 
    th_avg_ins_damage_m: float = 0.017                                         # average thickness of damaged insulation [m]


# Ambient temperatures
@dataclass 
class AmbientTemp:  
    t_surface_c: float = 3.5                                                   
    t_channel_c: float = 30                                                    
    t_soil_c: float = 10                                                   



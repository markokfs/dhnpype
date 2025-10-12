import numpy as np
import CoolProp.CoolProp as CP                                                 # for fluids

from model_param import ThermalCoeff
from config_data import AmbientTemp
from typing import Tuple                                                       # for type hints of function arguments


def calculate_r_conduction(d_outer_m:float, d_inner_m:float, l_m:float, k_w_per_mk:float) -> float:   # toplotna upornost - Rth [K/W]
    """
    Calculates the conduction resistance of a cylindrical element.

    :param d_outer: pipe external diameter in [m]
    :param d_inner: pipe internal diameter in [m]
    :param l_m: pipe (section) lenght in [m]
    :param k_w_per_mk: the material conductivity coefficient in [W/mK] 
    :return r_cond: conduction resistance in [K/W]
    
    """
    r_cond = (np.log(d_outer_m / d_inner_m)) / (2 * l_m * k_w_per_mk * np.pi)
    return r_cond


def calculate_r_convection(d_m:float, l_m:float, h_w_per_m2k:float) -> float:
    """
    Calculates the convection resistance of a cylindrical element.

    :param d_m: diameter of the surface for the convection in [m]
    :param l_m: pipe (section) lenght in [m]
    :param h_w_per_m2k: the material convection coefficient in [W/m2K] 
    :return r_conv: convection resistance in [K/W]
    
    """    
    r_conv = 1 / (d_m * l_m * h_w_per_m2k * np.pi)
    return r_conv


def calculate_r_total(d_pipe_inner_m:float, l_m:float, h_mat1_w_per_m2k:float, d_pipe_outer_m:float, k_mat1_w_per_mk:float, d_ins_outer_m:float, k_mat2_w_per_mk:float, h_loc_w_per_m2k:float) -> float:
    """
    Calculates the total thermal resistance of a cylindrical element ---> fluid-pipe-insulation-air.

    :param d_pipe_inner_m: diameter of the surface for the convection inside the pipe section in [m]
    :param l_m: pipe section lenght in [m]
    :param h_mat1_w_per_m2k: the pipe heat transfer coefficient in [W/m2K]
    :param d_pipe_outer_m: external diameter of the pipe section in [m]
    :param k_mat1_w_per_mk: the pipe conductivity coefficient in [W/mK] 
    :param d_ins_outer_m: external diameter of the insulation in [m]
    :param k_mat2_w_per_mk: the insulation conductivity coefficient in [W/mK]
    :param h_loc_w_per_m2k: heat transfer coefficient based on the location of the pipe section (surface, channel, soil) in [W/m2K] 
    :return r_tot: total thermal resistance in [K/W]
    
    """     
    r1 = calculate_r_convection(d_pipe_inner_m, l_m, h_mat1_w_per_m2k)                              # convection from the fluid to the pipe material
    r2 = calculate_r_conduction(d_pipe_outer_m, d_pipe_inner_m, l_m, k_mat1_w_per_mk)               # heat transfer through the pipe material
    r3 = calculate_r_conduction(d_ins_outer_m, d_pipe_outer_m, l_m, k_mat2_w_per_mk)                # heat transfer through the insulation material
    r4 = calculate_r_convection(d_ins_outer_m, l_m, h_loc_w_per_m2k)                                # convection from the outside surface to ambient air
    #
    r_tot = (r1 + r2 + r3 + r4)
    return r_tot


def calculate_heat_flow_loss(r_tot:float, t_outer:float, t_inner:float) -> float:
    """
    Calculates the flow of thermal energy loss in [W].

    :param r_tot: total thermal resistance of a pipe section in [K/W]
    :param t_outer: ambient temperature in [K]
    :param t_inner: temperature of the fluid inside the pipeline in [K]
    :return qdot_loss: heat loss flow in [W]
    
    """    
    qdot_loss = (t_inner - t_outer) / r_tot
    return qdot_loss


def calculate_heat_flow(t_high:float, t_low:float, mdot:float, cp:float) -> float:
    """
    Calculates the flow of thermal energy inside the pipeline [W].

    :param t_high: higher temperature in [°C]
    :param t_low: lower temperature in [°C]
    :param mdot: mass flow in [kg/s]
    :param cp: specific heating capacity coefficient in [Ws/kgK]
    :return qdot: heat flow in [W]
    
    """    
    delta_t = t_high - t_low
    qdot = mdot * cp * delta_t
    return qdot


def calculate_flow_velocity(den_fluid:float, mdot_flow:float, d_pipe_inner:float) -> float:
    """
    Calculates the velocity inside an individual segment of the pipeline (based on mass flow) in [m/s].

    :param den_fluid: density of the fluid in [kg/m3]
    :param mdot_flow: fluid mass flow in [kg/s]
    :param d_pipe_inner: the internal diameter of the pipeline section in [m] 
    :return v_flow: velocity of flow [m/s]
    
    """      
    v_flow = (4 * mdot_flow) / (np.pi * den_fluid * (d_pipe_inner * d_pipe_inner))
    return v_flow


def calculate_average_flow_velocity(v_flow_m_per_s:list) -> float:
    """
    Calculates the average velocity of the fluid flow in the pipeline in [m/s].

    :param v_flow_m_per_s: list of fluid values in each pipe section in [m/s]
    :return v_avg_m_per_s: average flow velocity in the pipeline in [m/s]
    
    """    
    i = 0
    v_sum = 0
    for i in range(len(v_flow_m_per_s) - 1):
        v_sum = v_sum + v_flow_m_per_s[i]
    
    v_avg_m_per_s = v_sum / len(v_flow_m_per_s)
    return v_avg_m_per_s


def select_heat_transfer_coeff(location:str) -> float:
    """
    Selects the heat transfer coefficient based on the location of the pipeline section.

    :param location: position of pipeline section
    :return h_conv: value of the heat transfer coefficient read from data table
    
    """    
    if (location == 'surface'):
        h_conv = ThermalCoeff.h_surface_w_per_m2k
        return h_conv
    elif (location == 'channel'):
        h_conv = ThermalCoeff.h_channel_w_per_m2k
        return h_conv
    elif (location == 'soil'):
        h_conv = ThermalCoeff.h_soil_w_per_m2k
        return h_conv
    else:
        raise ValueError(f"Unknown location '{location}'. Must be one of: 'soil', 'channel', or 'surface'.")
        

def select_ambient_temperature(location:str) -> float:
    """
    Selects the external temperature based on the location of the pipeline section.

    :param location: position of pipeline section
    :return t_amb: temperature of the sorounding ambient in [°C]
    
    """        
    if (location == 'surface'):
        t_amb = AmbientTemp.t_surface_c
        return t_amb
    elif (location == 'channel'):
        t_amb = AmbientTemp.t_channel_c
        return t_amb
    elif (location == 'soil'):
        t_amb = AmbientTemp.t_soil_c
        return t_amb
    else:
        raise ValueError(f"Unknown location '{location}'. Must be one of: 'soil', 'channel', or 'ambient'.")


def calculate_pipe_internal_diameter(d_pipe_external:float, th_pipe:float) -> float:
    """
    Calculates the internal diameter of a chosen pipe section.

    :param d_pipe_external: external diameter of the chosen pipe section in [m]
    :param th_pipe: pipe wall thickness of the chosen section in [m]
    :return d_pipe_internal: internal diameter of the chosen pipe section in [m]
    
    """  
    d_pipe_internal = d_pipe_external - (2 * th_pipe)
    return d_pipe_internal


def calculate_insulation_external_diameter(d_pipe_external:float, th_insulation:float) -> float:
    """
    Calculates the external diameter of the insulation of a chosen pipe section.

    :param d_pipe_external: external diameter of the chosen pipe section in [m]
    :param th_insulation: insulation thickness of the chosen section in [m]
    :return d_insulation_external: external diameter of the chosen section in [m]
    
    """  
    d_insulation_external = d_pipe_external + (2 * th_insulation)
    return d_insulation_external

    
def calculate_insulation_thickness(location:str, d_pipe_nominal:str, th_insulation_dict:dict) -> float:
    """
    Calculates the thickness of pipe section insulation based on its location in [m].
    
    :param location: 'channel', 'surface', or 'soil'
    :param d_pipe_external: External pipe diameter at the given index in [m]
    :param th_insulation_dict: Dictionary with thickness data
    :return: th_insulation: Insulation thickness in [m]
    
    """
    if location not in th_insulation_dict:
        raise ValueError(f"Invalid location '{location}'. Expected one of: {list(th_insulation_dict.keys())}.")

    th_data = th_insulation_dict[location]

    if d_pipe_nominal not in th_data:
        raise ValueError(
            f"Invalid nominal pipe diameter '{d_pipe_nominal}' for location '{location}'. Available sizes: {list(th_data.keys())}")

    th_insulation = th_data[d_pipe_nominal] / 1000 
    return th_insulation

 
def calculate_output_temperature(t_in:float, t_amb:float, mdot:float, cp:float,
                                 r_tot:float, tolerance:float = 0.001) -> Tuple[float, float]:
    """
    Iteratively compute the outlet temperature accounting for energy loss and return the final heat loss.

    :param t_in: Inlet temperature in [°C]
    :param t_amb: Ambient temperature in [°C]
    :param mdot: Mass flow rate in [kg/s]
    :param cp: Specific heat coefficient in [Ws/kgK]
    :param r_tot: Total thermal resistance in [K/W]
    :param tolerance: Convergence tolerance (default 0.01 = 1%)
    
    :returns:
        t_out_c: Final outlet temperature in [°C]
        qdot_loss: Final heat flow loss in [W]
        
    """
    qdot_loss_initial = calculate_heat_flow_loss(r_tot, t_amb, t_in)
    
    t_out_ref = t_in                                                           # setting the initial reference temperature ---> equal to inlet node temperature
    t_out = t_in - (qdot_loss_initial / (mdot * cp))                           # calculates the outlet temperature value for the first iteration 
    
    qdot_loss = qdot_loss_initial
    
    while abs((t_out_ref - t_out) / t_out_ref) > tolerance:                    # loops until the temperature at the outlet node (T_out) is calculated 
        if t_out <= t_amb:                                                     # if the temperature inside the pipe is equal to the temperature around it
            #t_out_ref = t_out
            t_out = t_amb
            break
            qdot_loss = 0.0   
        else:
            if (t_in <= 0) or (t_out <= 0):
                raise ValueError(f"Temperature values at the inlet ({t_in}°C) and the outlet ({t_out}°C) nodes cannot be zero or negative.")
            else:
                try:
                    t_avg = (t_in - t_out) / (np.log(t_in) - np.log(t_out))    # calcualating heat flow loss with the logarithmic mean temperature difference (inside the pipe section!)
                except ZeroDivisionError:
                    t_avg = (t_in - t_out) / 2                                 # fallback to arithmetic average to avoid division by 0                                

            qdot_loss = calculate_heat_flow_loss(r_tot, t_amb, t_avg)
                            
            t_out_ref = t_out                                                  # T_ref becomes the current T_out
            t_out = t_in - (qdot_loss / (mdot * cp))                           # a new T_out is calculated (until new T_out < current T_out)
            
    return t_out, qdot_loss


# ______________________ FLUIDS _______________________________________________

def calculate_fluid_density(p:float, t:float, fluid:str = "Water") -> float:
    """
    Defines the fluid density in [kg/m3].

    :param p: avrega pressure in the pipeline in [Pa]
    :param t: temperature in [K]
    :param fluid: fluid type
    :return den: density in [kg/m3]
    
    """        
    den = CP.PropsSI("D", "P", p, "T", t, fluid)
    return den


def calculate_fluid_specific_heat(p:float, t:float, fluid:str = "Water") -> float:
    """
    Defines the fluid specific heat in [Ws/kgK].

    :param p: avrega pressure in the pipeline in [Pa]
    :param t: temperature in [K]
    :param fluid: fluid type
    :return cp: specific heat coefficient in [Ws/kgK]
    
    """        
    cp = CP.PropsSI("C", "P", p, "T", t, fluid) 
    
    return cp 


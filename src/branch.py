import pandas as pd
import json

import data_input
# Supply
from data_input import (d_pipe_ext_supply_m, d_pipe_nom_supply_mm, l_pipesection_supply_m, th_insulation_supply_percent, location_supply, 
                        mdot_takeoff_supply_kg_per_s, lat_supply, lon_supply, )
# Return
from data_input import (d_pipe_ext_return_m, d_pipe_nom_return_mm, l_pipesection_return_m, th_insulation_return_percent, location_return, 
                        mdot_takeoff_return_kg_per_s, lat_return, lon_return, )
import data_output
from data_output import PipeRow, SystemRow 
from config_data import BranchInitialConfig
from utils.constants import TZERO
from utils.functions import (calculate_flow_velocity, calculate_fluid_density, calculate_fluid_specific_heat, calculate_pipe_internal_diameter, 
                            calculate_insulation_external_diameter, calculate_insulation_thickness, 
                            select_heat_transfer_coeff, calculate_r_total, select_ambient_temperature, 
                            calculate_output_temperature, )
from utils.validation import validate_damage
from utils.exceptions import SupplyDataMissingError
from model_param import ThermalCoeff, PipeSectionLocation


# Getting thickness data
thickness_data_location = "../data/insulation_thickness.json"

try:
    with open(thickness_data_location, "r") as th_file:
        data = json.load(th_file)
        th_mm = data.get("thickness_data", {})
except FileNotFoundError:
    print("File not found.")
    th_mm = {}


# Calculations
class Branch:
    
    class_instances_created = 0                                                # used to check the number of branches created with the Branch class (class attribute only!)

    _DAMAGE_MODE_AVERAGE = "average"                                           # class constants
    _DAMAGE_MODE_ELEMENT = "element"
      
    def __init__(self, initial_values = None, th_values: dict = None, **kwargs):
        self.iv = initial_values or BranchInitialConfig()
        self.th_all = th_values or th_mm                                       # pipe & insulation thickness from data in the JSON file
        
        self.tolerance = 0.001                                                 # for the while loop in the <calculate_output_temperature> function
        
        # Pipe thickness                                                       # data from the JSON file
        self.th_pipe = self.th_all["th_pipe"] 
        
        # Average thickness of the damaged insulation
        self.th_avg_damage = self.iv.th_avg_ins_damage_m                       # average insulation damage
            
        # From **kwargs: thickness of the damaged insulation (includes type validation in utils\validation.py)
        self.ins_damage_mode = kwargs.get("damage_mode", self.__class__._DAMAGE_MODE_AVERAGE)            # options for how the program uses the thickness of the damaged insulation: "average" or "element"
        damage = kwargs.get("damage", self.th_avg_damage if self.ins_damage_mode == self.__class__._DAMAGE_MODE_AVERAGE else [])
        self.th_ins_damage_avg_m, self.th_ins_damage_elem_percent = validate_damage(self.ins_damage_mode, damage)
        
        # Insulation thickness data
        self.th_ins_supply_dict = {                                            # insulation based on the location     
            PipeSectionLocation.loc1.value: self.th_all["th_insulation_channel_supply"],
            PipeSectionLocation.loc2.value: self.th_all["th_insulation_surface_supply"],
            PipeSectionLocation.loc3.value: self.th_all["th_insulation_soil_supply"]
        }
        self.th_ins_return_dict = {                                            # insulation based on the location     
            PipeSectionLocation.loc1.value: self.th_all["th_insulation_channel_return"],
            PipeSectionLocation.loc2.value: self.th_all["th_insulation_surface_return"],
            PipeSectionLocation.loc3.value: self.th_all["th_insulation_soil_return"]
        }
                      
        # From **kwargs: counting the number of instances                      # counts only objects created with the 'name' argument // if name is not provided, the object will not be counted
        self.class_instance_name = kwargs.get("name", None)
        if self.class_instance_name is not None:
            self.__class__.class_instances_created += 1            
        
   
    #______________________ Helper methods ____________________________________
      
    def _calculate_internal_diameter(self, d_nominal:str, d_external_m:float) -> float:
        """
        Returns the pipe internal diameter for a given nominal pipe size.
        Used to calculate initial values.

        Returns
        -------
        float
            Internal diameter in [m]
        """
        if d_nominal not in self.th_pipe:
            raise KeyError(f"Nominal pipe size {d_nominal} not found in pipe wall thickness data. Please choose a different pipe size.")
        
        th_pipe_m = self.th_pipe[d_nominal] / 1000                             # pipe thickness
        d_pipe_int = d_external_m - (2 * th_pipe_m)                            # pipe internal diameter         
        return d_pipe_int
        
    
    @classmethod
    def get_class_instance_count(cls) -> int:                                  # returns the number of Branch objects created - used for tracking the number of instances created
        """
        Returns the number of Branch objects created (used for tracking the number of instances created).

        Returns
        -------
        int
            Number of class instances
        """
        return cls.class_instances_created
    
    
    def print_input_data(self) -> None:
        """
        Outputs to terminal information about input data:
            - Insulation damage mode (average or per element)
            - Level of damage in percent

        -------
        """
        print(f"Insulation damage mode: {self.ins_damage_mode}")
        print(f"Damage (avg, per-element): {self.th_ins_damage_avg_m}, {self.th_ins_damage_elem_percent}")   
    

    def calculate_branch_length(self) -> float:
        """
        Sums lengths of all pipeline elements to get the length of the analysed branch.

        Returns
        -------
        float
            Length in [m]
        """        
        l_branch = l_pipesection_supply_m.sum()
        #print(f"\nBranch length: {l_branch:.2f} m\n") 
        return l_branch  
         
    
    #____________________ CALCULATIONS - SUPPLY _______________________________
    
    def calculate_supply(self):
        """
        Performs calculations only for the supply branch.
        """        
        # (i) Branch setup:
        th_ins_supply_dict_i = self.th_ins_supply_dict
        
        # (ii) Initial values:
        t_in_s_i_c = self.iv.t_in_supply_c                                     # temperature at the start of the pipe section (= inlet temperature)
        #
        den_s_i_kg_per_m3 = calculate_fluid_density(p = self.iv.p_nominal_pa, 
                                                  t = t_in_s_i_c + (- TZERO),
                                                  fluid = self.iv.fluid)
        mdot_s_i_kg_per_s = self.iv.vdot_m3_per_h * den_s_i_kg_per_m3 / 3600   # mass flow at the start of the pipe section - calculated from vol. flow data
        #
        l_tot_s_i_m = 0                                                        # position of the start of the section on the pipeline
        qdot_loss_s_i_w = 0                                                    # heat flow loss at the start of the pipeline
        #qdotnorm_loss_i_w_per_m = 0                                           # normalised heat flow loss at the start of the pipeline
        qdot_loss_tot_s_i_w = 0                                                # total heat flow loss at the start of the pipeline  
        #
        qdot_in_tot_s_i_w = mdot_s_i_kg_per_s * (t_in_s_i_c - TZERO) * calculate_fluid_specific_heat(     # total (absolute) heat flow at the start of the pipeline 
                                                                               p = self.iv.p_nominal_pa, 
                                                                               t = (t_in_s_i_c - TZERO),
                                                                               fluid = self.iv.fluid)           
        
        i = 0
        
        for i in range(len(data_input.df_supply_in)):           
            ### PART 1: DEFINING GEOMETRY & COEFFICIENTS & THERMAL RESISTANCE FOR EACH ELEMENT
            location_s_i = location_supply[i]
            
            d_pipe_ext_s_i_m = d_pipe_ext_supply_m[i]
            
            d_nom_s_i = str(int(d_pipe_nom_supply_mm[i]))                      # DN - nominal diameter
            
            th_pipe_s_i_m = self.th_pipe[d_nom_s_i] / 1000
            
            if th_pipe_s_i_m is None:
                raise ValueError(f"No thickness found for diameter {d_pipe_ext_s_i_m} m.")
            
            d_pipe_int_s_i_m = calculate_pipe_internal_diameter(d_pipe_ext_s_i_m, th_pipe_s_i_m)   # internal pipe diameter of the selected section 
                    
            h_ins2ambient_s_i_w_per_m2k = select_heat_transfer_coeff(location_s_i)                 # convective heat transfer coefficient depending on the location of the pipe section ---> insulation to external environment
            
            l_s_i_m = l_pipesection_supply_m[i]                                # length of the section
            
            # Calculates total thermal resistance depending on damage mode:
            if self.ins_damage_mode == self.__class__._DAMAGE_MODE_AVERAGE:    # for the average damage:
                
                if th_insulation_supply_percent[i] == 0:                       # if the value in the input file is 0, use the average value
                    th_insulation_s_i_m = self.th_ins_damage_avg_m
                    d_insulation_ext_s_i_m = calculate_insulation_external_diameter(d_pipe_ext_s_i_m, th_insulation_s_i_m)
                    k_ins_s_i_w_per_mk = ThermalCoeff.k_ins_damaged_w_per_mk                
                else:                                                          # if value in the input file is not 0, choose insulation thickness according to pipe nominal diameter and the location of the chosen section
                    th_insulation_s_i_m = calculate_insulation_thickness(location_s_i, d_nom_s_i, th_ins_supply_dict_i)
                    d_insulation_ext_s_i_m = calculate_insulation_external_diameter(d_pipe_ext_s_i_m, th_insulation_s_i_m)
                    k_ins_s_i_w_per_mk = ThermalCoeff.k_ins_w_per_mk
            
            elif self.ins_damage_mode == self.__class__._DAMAGE_MODE_ELEMENT:  # for the per element damage: each element has assigned its thickness
                th_insulation_s_i_percent = th_insulation_supply_percent[i]    # reads the amount of insulation damage in [%] 
                th_insulation_s_i_m = calculate_insulation_thickness(location_s_i, d_nom_s_i, th_ins_supply_dict_i) * th_insulation_s_i_percent 
                d_insulation_ext_s_i_m = calculate_insulation_external_diameter(d_pipe_ext_s_i_m, th_insulation_s_i_m)
                k_ins_s_i_w_per_mk = ThermalCoeff.k_ins_w_per_mk
                
            # thermal resistance:                   pipe int. diam.---length---heat from water to pipe---------pipe ext. diam.-----heat through pipe-----------insulation ext. diam.---heat through ins.---heat to ambient          
            r_total_s_i_w_per_k = calculate_r_total(d_pipe_int_s_i_m, l_s_i_m, ThermalCoeff.h_water_w_per_m2k, d_pipe_ext_s_i_m, ThermalCoeff.k_pipe_w_per_mk, d_insulation_ext_s_i_m, k_ins_s_i_w_per_mk, h_ins2ambient_s_i_w_per_m2k)
            
            
            ### PART 2: HEAT FLOW LOSS CALCULATION FOR EACH ELEMENT
            t_ambient_s_i_c = select_ambient_temperature(location_s_i)
            
            cp_s_i_ws_per_kgk = calculate_fluid_specific_heat(self.iv.p_nominal_pa, (t_in_s_i_c - TZERO))
            
            # Calculates outlet node temperature and element heat flow loss (contains: while loop)
            t_out_s_i_c, qdot_loss_s_i_w = calculate_output_temperature(t_in_s_i_c, t_ambient_s_i_c, mdot_s_i_kg_per_s, cp_s_i_ws_per_kgk, r_total_s_i_w_per_k, self.tolerance)
            
            
            ### PART 3: OTHER CALCULATIONS 
            # (i) Position on the pipeline
            l_tot_s_i_m += l_s_i_m
            
            # (ii) Total heat flow loss
            qdot_loss_tot_s_i_w += qdot_loss_s_i_w    
            
            # (iii) Flow velocity
            den_s_i_kg_per_m3 = calculate_fluid_density(p = self.iv.p_nominal_pa, t = t_in_s_i_c + (- TZERO), fluid = self.iv.fluid)   
            v_s_i_m_per_s = calculate_flow_velocity(den_s_i_kg_per_m3, mdot_s_i_kg_per_s, d_pipe_int_s_i_m)
            
            # (iv) Heat flow for the consumer - absolute value
            qdot_cons_abs_s_i_w = abs(mdot_takeoff_supply_kg_per_s[i]) * cp_s_i_ws_per_kgk * (t_out_s_i_c - TZERO)
            
            # (v) Useful heat flow for the consumer
            qdot_cons_act_s_i_w = abs(mdot_takeoff_supply_kg_per_s[i]) * cp_s_i_ws_per_kgk * (t_out_s_i_c - self.iv.t_consumer_release_c)
          
            # (vi) Total heat flow in the system
            qdot_in_tot_s_i_w = qdot_in_tot_s_i_w - qdot_loss_s_i_w - qdot_cons_abs_s_i_w
            
            
            # ### PART 4: WRITING CALCULATED VALUES TO THE DATAFRAMES
            row_supply_i = PipeRow(
                lat               = lat_supply[i],                             # from the PipeRow class in data_output.py
                lon               = lon_supply[i],
                l_tot             = l_tot_s_i_m,
                t_in              = t_out_s_i_c,
                mdot              = mdot_s_i_kg_per_s,
                qdot_loss         = qdot_loss_s_i_w,
                qdotnorm_loss     = qdot_loss_s_i_w / l_s_i_m,                 # qdot loss normalised [W/m]
                qdot_loss_tot     = qdot_loss_tot_s_i_w,
                v_fluid           = v_s_i_m_per_s,
                mdot_consumer     = mdot_takeoff_supply_kg_per_s[i],
                qdot_consumer_abs = qdot_cons_abs_s_i_w,
                qdot_consumer_act = qdot_cons_act_s_i_w,
                qdot_tot          = qdot_in_tot_s_i_w
            ) 
            data_output.df_supply_out = pd.concat([data_output.df_supply_out, pd.DataFrame([row_supply_i.convert_to_dict_pipe()])], ignore_index = True)   
           
           
            ### PART 5: SETTING VALUES FOR THE NEXT NODE (i --> i+1)
            t_in_s_i_c = t_out_s_i_c                                           # the inlet temperature of the next element is the same as the outlet temperature of the preceding element                                                      
            mdot_s_i_kg_per_s += mdot_takeoff_supply_kg_per_s[i]               # reducing the supply mass flow by the take-off amount (take-off is specified in a separate file)
        
    #''''''''''''''''''''''' SUPPLY END '''''''''''''''''''''''''''''''''''''''
 
    
    #____________________ CALCULATIONS - RETURTN ______________________________
    
    
    def calculate_return(self):
        """
        Performs calculations only for the return branch.
        """  
        # (i) Check supply data:
        if data_output.df_supply_out.empty:                                    # checks if the calculation of the supply line has been run
            raise SupplyDataMissingError("Supply DataFrame is empty. Make sure method < calculate_supply() > is run before < calculate_return() >. Supply data must be calculated before calculating return.")
        
        # (ii) Branch setup:
        th_ins_return_dict_i = self.th_ins_return_dict
        
        # (iii) Initial values:
        t_in_r_i_c = self.iv.t_in_return_c                                     # temperature at the start of the pipe section (= inlet temperature)
        #
        mdot_r_i_kg_per_s = data_output.df_supply_out["mdot [kg/s]"].iloc[-1]  # last value in the dataframe ---> mass flow at the start of the pipe section - calculated with the mass flow of the last node on the supply line (assumption: entire flow from the supply line goes to the return line)
        #
        #l_tot_r_i_m = 0                                                        # position of the start of the section on the pipeline
        l_tot_r_i_m = self.calculate_branch_length()
        qdot_loss_r_i_w = 0                                                    # heat flow loss at the start of the pipeline
        #qdotnorm_loss_r_i_w_per_m = 0                                          # normalised heat flow loss at the start of the pipeline
        qdot_loss_tot_r_i_w = 0                                                # total heat flow loss at the start of the pipeline  
        #
        qdot_in_tot_r_i_w = mdot_r_i_kg_per_s * (t_in_r_i_c - TZERO) * calculate_fluid_specific_heat(          # total (absolute) heat flow at the start of the return pipeline 
                                                                               p = self.iv.p_nominal_pa, 
                                                                               t = (t_in_r_i_c - TZERO),
                                                                               fluid = self.iv.fluid)           
        
        i = 0                                                                  # for the for loop ---> loops through all elements of the return line
        
        j = len(data_input.df_supply_in) - 1                                   # for the if loop for the consumer in the for loop ---> to determine the return flow from the consumer

        for i in range(len(data_input.df_return_in)):           
            ### PART 1: DEFINING GEOMETRY & COEFFICIENTS & THERMAL RESISTANCE FOR EACH ELEMENT
            location_r_i = location_return[i]
            
            d_pipe_ext_r_i_m = d_pipe_ext_return_m[i]
            
            d_nom_r_i = str(int(d_pipe_nom_return_mm[i]))                      # DN - nominal diameter
            
            th_pipe_r_i_m = self.th_pipe[d_nom_r_i] / 1000
            
            if th_pipe_r_i_m is None:
                raise ValueError(f"No thickness found for diameter {d_pipe_ext_r_i_m} m.")
            
            d_pipe_int_r_i_m = calculate_pipe_internal_diameter(d_pipe_ext_r_i_m, th_pipe_r_i_m)   # internal pipe diameter of the selected section 
                    
            h_ins2ambient_r_i_w_per_m2k = select_heat_transfer_coeff(location_r_i)                 # convective heat transfer coefficient depending on the location of the pipe section ---> insulation to external environment
            
            l_r_i_m = l_pipesection_return_m[i]                                # length of the section
            
            # Calculates total thermal resistance depending on damage mode:
            if self.ins_damage_mode == self.__class__._DAMAGE_MODE_AVERAGE:    # for the average damage:
                
                if th_insulation_return_percent[i] == 0:                       # if the value in the input file is 0, use the average value
                    th_insulation_r_i_m = self.th_ins_damage_avg_m
                    d_insulation_ext_r_i_m = calculate_insulation_external_diameter(d_pipe_ext_r_i_m, th_insulation_r_i_m)
                    k_ins_r_i_w_per_mk = ThermalCoeff.k_ins_damaged_w_per_mk                
                else:                                                          # if value in the input file is not 0, choose insulation thickness according to pipe nominal diameter and the location of the chosen section
                    th_insulation_r_i_m = calculate_insulation_thickness(location_r_i, d_nom_r_i, th_ins_return_dict_i)
                    d_insulation_ext_r_i_m = calculate_insulation_external_diameter(d_pipe_ext_r_i_m, th_insulation_r_i_m)
                    k_ins_r_i_w_per_mk = ThermalCoeff.k_ins_w_per_mk
            
            elif self.ins_damage_mode == self.__class__._DAMAGE_MODE_ELEMENT:  # for the per element damage: each element has assigned its thickness
                th_insulation_r_i_percent = th_insulation_return_percent[i]    # reads the amount of insulation damage in [%] 
                th_insulation_r_i_m = calculate_insulation_thickness(location_r_i, d_nom_r_i, th_ins_return_dict_i) * th_insulation_r_i_percent 
                d_insulation_ext_r_i_m = calculate_insulation_external_diameter(d_pipe_ext_r_i_m, th_insulation_r_i_m)
                k_ins_r_i_w_per_mk = ThermalCoeff.k_ins_w_per_mk
                
            # thermal resistance:                   pipe int. diam.---length---heat from water to pipe---------pipe ext. diam.---heat through pipe-------------insulation ext. diam.---heat through ins.---heat to ambient          
            r_total_r_i_w_per_k = calculate_r_total(d_pipe_int_r_i_m, l_r_i_m, ThermalCoeff.h_water_w_per_m2k, d_pipe_ext_r_i_m, ThermalCoeff.k_pipe_w_per_mk, d_insulation_ext_r_i_m, k_ins_r_i_w_per_mk, h_ins2ambient_r_i_w_per_m2k)
            
            
            ### PART 2: HEAT FLOW LOSS CALCULATION FOR EACH ELEMENT
            t_ambient_r_i_c = select_ambient_temperature(location_r_i)
            
            cp_r_i_ws_per_kgk = calculate_fluid_specific_heat(self.iv.p_nominal_pa, (t_in_r_i_c - TZERO))
            
            # Calculates outlet node temperature and element heat flow loss (contains: while loop)
            t_out_r_i_c, qdot_loss_r_i_w = calculate_output_temperature(t_in_r_i_c, t_ambient_r_i_c, mdot_r_i_kg_per_s, cp_r_i_ws_per_kgk, r_total_r_i_w_per_k, self.tolerance)         
            
            # Connecting the correct sections of the supply and return lines, because they may not have the same number of elements (non-symmetrical pipelines)
            if data_input.df_return_in["mdot take-off [kg/s]"][i] != 0:
                while data_input.df_supply_in["mdot take-off [kg/s]"][j] == 0:
                    j -= 1
                #
                mdot_consumer_r_i_kg_per_s = - data_output.df_supply_out["mdot consumer [kg/s]"][j]
                j -= 1
            else:
                mdot_consumer_r_i_kg_per_s = 0
                
            # Temperature of the mixture on the return line: fluid from the consumer mixes with the fluid in the return line ---> residual heat flows from the consumer into the return line
            t_mix_r_i_c = ((t_out_r_i_c * mdot_r_i_kg_per_s) + (self.iv.t_consumer_release_c * mdot_consumer_r_i_kg_per_s)) / (mdot_r_i_kg_per_s + mdot_consumer_r_i_kg_per_s)                 
            

            ### PART 3: OTHER CALCULATIONS 
            # (i) Position on the pipeline
            l_tot_r_i_m -= l_r_i_m
            
            # (ii) Total heat flow loss
            qdot_loss_tot_r_i_w += qdot_loss_r_i_w    
            
            # (iii) Flow velocity
            den_r_i_kg_per_m3 = calculate_fluid_density(p = self.iv.p_nominal_pa, t = t_in_r_i_c + (- TZERO), fluid = self.iv.fluid)   
            v_r_i_m_per_s = calculate_flow_velocity(den_r_i_kg_per_m3, mdot_r_i_kg_per_s, d_pipe_int_r_i_m)
            
            # (iv) Heat flow for the consumer - absolute value
            qdot_cons_abs_r_i_w = abs(mdot_takeoff_return_kg_per_s[i]) * cp_r_i_ws_per_kgk * (t_out_r_i_c - TZERO)
            
            # (v) Useful heat flow for the consumer
            qdot_cons_act_r_i_w = abs(mdot_takeoff_return_kg_per_s[i]) * cp_r_i_ws_per_kgk * (t_out_r_i_c - self.iv.t_consumer_release_c)
          
            # (vi) Total heat flow in the system
            qdot_in_tot_r_i_w = qdot_in_tot_r_i_w - qdot_loss_r_i_w + qdot_cons_abs_r_i_w
            
            
            # ### PART 4: WRITING CALCULATED VALUES TO THE DATAFRAMES
            row_return_i = PipeRow(
                lat               = lat_return[i],                             # from the PipeRow class in data_output.py
                lon               = lon_return[i],
                l_tot             = l_tot_r_i_m,
                t_in              = t_out_r_i_c,
                mdot              = mdot_r_i_kg_per_s,
                qdot_loss         = qdot_loss_r_i_w,
                qdotnorm_loss     = qdot_loss_r_i_w / l_r_i_m,                 # qdot loss normalised [W/m]
                qdot_loss_tot     = qdot_loss_tot_r_i_w,
                v_fluid           = v_r_i_m_per_s,
                mdot_consumer     = mdot_consumer_r_i_kg_per_s,
                qdot_consumer_abs = qdot_cons_abs_r_i_w,
                qdot_consumer_act = qdot_cons_act_r_i_w,
                qdot_tot          = qdot_in_tot_r_i_w
            ) 
            data_output.df_return_out = pd.concat([data_output.df_return_out, pd.DataFrame([row_return_i.convert_to_dict_pipe()])], ignore_index = True)   
            
           
            ### PART 5: SETTING VALUES FOR THE NEXT NODE (i --> i+1)
            t_in_r_i_c = t_mix_r_i_c                                           # the inlet temperature of the next element is the same as the outlet temperature of the preceding element                                                      
            mdot_r_i_kg_per_s += mdot_consumer_r_i_kg_per_s                    # reducing the supply mass flow by the take-off amount (take-off is specified in a separate file)
            
    #''''''''''''''''''''''' RETURN END '''''''''''''''''''''''''''''''''''''''

    
    #____________________ CALCULATIONS - SYSTEM _______________________________
 
    def calculate_system_heat_flow(self) -> None:
        """
        Gathers total heat flow data from the supply and return calculations to calculate the total system heat flow:
            Q̇ _total_system = Q̇ _total_supply - Q̇ _total_return.
        """  
        i = 0
        j = 0
                
        # Determine the shorter dataframe
        if data_output.df_supply_out.shape[0] <= data_output.df_return_out.shape[0]:
            length_qdot_sys = len(data_output.df_supply_out)
        elif data_output.df_return_out.shape[0] < data_output.df_supply_out.shape[0]:
            length_qdot_sys = len(data_output.df_return_out)
            
        df_length_diff = len(data_output.df_supply_out) - len(data_output.df_return_out)
        if df_length_diff > 0:
            diff = 0
        elif df_length_diff <= 0:
            diff = abs(df_length_diff)
            
        for i in range(len(data_output.df_supply_out)):
            if (data_input.mdot_takeoff_return_kg_per_s[length_qdot_sys - i] != 0) or (i == length_qdot_sys):
                
                qdot_sys_supply_i = data_output.df_supply_out["Qdot tot [W]"][j]/1e6
                qdot_sys_return_i = data_output.df_return_out["Qdot tot [W]"][len(data_output.df_return_out) - diff - i]/1e6
                
                qdot_system_i_w = qdot_sys_supply_i - qdot_sys_return_i
                
                j += 1
                
            #print(f"{i} \t {lat_supply[i]} \t {lon_supply[i]} \t {data_output.df_supply_out["L tot [m]"][i]} \t {qdot_system_i_w}")
                
            row_system_i = SystemRow(
                lat         = lat_supply[i],
                lon         = lon_supply[i],
                l_tot       = data_output.df_supply_out["L tot [m]"][i],
                qdot_system = qdot_system_i_w  
            )
            data_output.df_system_out = pd.concat([data_output.df_system_out, pd.DataFrame([row_system_i.convert_to_dict_system()])], ignore_index = True)   

    #''''''''''''''''''''''' SYSTEM END '''''''''''''''''''''''''''''''''''''''

    
        
### OPTION 2: USE DATACLASS TO ENSURE TYPE CHECKING
import pandas as pd
from dataclasses import dataclass


@dataclass 
class PipeRow:
    lat: float
    lon: float
    l_tot: float
    # (i) Pipe:
    t_in: float 
    mdot: float
    qdot_loss: float 
    qdotnorm_loss: float 
    qdot_loss_tot: float
    v_fluid: float
    # (ii) Consumer:
    mdot_consumer: float
    qdot_consumer_abs: float 
    qdot_consumer_act: float
    # (iii) System:
    qdot_tot:float
    
    def convert_to_dict_pipe(self):
        return {
            "Latitude": self.lat,
            "Longitude": self.lon,
            "L tot [m]": self.l_tot,                                           # distance from the beginning of the pipeline // old: Lpos_sup
            # (i) Pipe:
            "T [°C]": self.t_in,                                               # water temperature at each junction // old: Touti_sup
            "mdot [kg/s]": self.mdot,                                          # mass flow at each junction // old: m_i_sup
            "Qdot loss [W]": self.qdot_loss,                                   # heat flow loss at each junction // old: Q_Li_sup
            "qdot loss [W/m]": self.qdotnorm_loss,                             # normalised heat flow loss at each junction (qdot loss = Qdot loss / element length) // old: qn_Li_sup
            "Qdot loss total [W]": self.qdot_loss_tot,                         # cumulative heat flow loss at each junction // old: Q_Ltot_sup
            "v [m/s]": self.v_fluid,                                           # flow velocity at each junction // old: v_sup
            # (ii) Consumer:
            "mdot consumer [kg/s]": self.mdot_consumer,                        # mass flow for each consumer--->from the supply line to the return line (the values are the same, but can have more or fewer values because of the difference in the number of elements of the supply and return lines)// old: mci_sup & mci_ret 
            "Qdot consumer absolute [W]": self.qdot_consumer_abs,              # heat flow for each consumer--->from the supply line===>total heat flow for each consumer // old: Qci_sup & Qci_ret
            "Qdot consumer actual [W]": self.qdot_consumer_act,                # heat flow for each consumer--->from the supply line===>useful heat flow (exergy) // old: Qciuse_sup & Qciuse_ret     
            # (iii) System:
            "Qdot tot [W]": self.qdot_tot                                      # absolute heat flow in the pipe section 
        }
    
pipe_columns_names_types = {
 # column name: variable type in the column 
    "Latitude": "float64",
    "Longitude": "float64",
    "L tot [m]": "float64",
    # (i) Pipe:
    "T [°C]": "float64",
    "mdot [kg/s]": "float64",
    "Qdot loss [W]": "float64",
    "qdot loss [W/m]": "float64",
    "Qdot loss total [W]": "float64",
    "v [m/s]": "float64",
    # (ii) Consumer:
    "mdot consumer [kg/s]": "float64",
    "Qdot consumer absolute [W]": "float64",
    "Qdot consumer actual [W]": "float64",
    # (iii) System:
    "Qdot tot [W]": "float64"
}

#df_supply_out = pd.DataFrame(columns = pipe_columns_names_types.keys())                                    # this doesn't enforce data types!
df_supply_out = pd.DataFrame({col: pd.Series(dtype=dt) for col, dt in pipe_columns_names_types.items()})    # to enforce data types!
df_return_out = pd.DataFrame({col: pd.Series(dtype=dt) for col, dt in pipe_columns_names_types.items()})


@dataclass 
class SystemRow:
    lat: float
    lon: float
    l_tot: float
    qdot_system: float 
    
    def convert_to_dict_system(self):
        return {
            "Latitude": self.lat,          # Fix: match column name
            "Longitude": self.lon,
            "L tot [m]": self.l_tot,
            "Qdot [W]": self.qdot_system
        }
    
system_columns_names_types = {
    "Latitude": "float64",
    "Longitude": "float64",
    "L tot [m]": "float64",
    "Qdot [W]": "float64"
    }

df_system_out = pd.DataFrame({col: pd.Series(dtype=dt) for col, dt in system_columns_names_types.items()})

from dataclasses import dataclass
from enum import Enum


@dataclass 
class ThermalCoeff:
    # Convective heat transfer coefficients (e.g. solid-fluid)
    h_water_w_per_m2k: float = 3000.0                                          # Internal pipe – water to pipe wall [W/m²K] 
    h_surface_w_per_m2k: float = 200.0                                         # To ambient air [W/m²K] 
    h_channel_w_per_m2k: float = 100.0                                         # To channel wall [W/m²K]
    h_soil_w_per_m2k: float = 3.0                                              # To surrounding soil [W/m²K]
    # Conductivity coefficients (e.g. conduction through the materials)
    k_pipe_w_per_mk: float = 43.0                                              # Thermal conductivity of the pipe material [W/mK]
    k_ins_w_per_mk: float = 0.03                                               # Normal insulation [W/mK]
    k_ins_damaged_w_per_mk: float = 0.03                                       # Damaged insulation (same value for now) [W/mK]


class PipeSectionLocation(Enum):
    loc1 = "channel"
    loc2 = "surface"
    loc3 = "soil"


    
"""
PIPE SECTION PROPERTIES

Physical properties of the pipeline materials and environment.

Sources:
    - Water-to-steel convection: Engineers Edge
    - Steel conductivity: Engineering Toolbox
    - Polyurethane insulation conductivity: Engineering Toolbox

── Water-to-pipe convection ─────────────────────────────────────────────────
h_water_w_per_m2k = 3000                    # internal water-side heat transfer coefficient [W/m²K]
k_pipe_w_per_mk = 43                        # thermal conductivity of steel pipe [W/mK]

── Insulation ───────────────────────────────────────────────────────────────
k_ins_w_per_mk = 0.03                       # thermal conductivity of new insulation (PUR) [W/mK]
k_ins_damaged_w_per_mk = 0.03               # thermal conductivity of damaged insulation (same) [W/mK]

── External convection coefficients ─────────────────────────────────────────
h_ambent_w_per_m2k = 200                    # external air-side heat transfer coefficient (outdoor) [W/m²K]
h_channel_w_per_m2k = 100                   # in-channel natural convection estimate [W/m²K]
h_soil_w_per_m2k = 3                        # buried pipes, rough guess for soil convection [W/m²K]
"""



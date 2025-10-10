import matplotlib.pyplot as plt
from matplotlib import cm, colors

import plotly.graph_objects as go                                              
import plotly.io as pio
import sys

if 'ipykernel' in sys.modules:
    pio.renderers.default = 'notebook'                                         # for jupyter notebooks
else:
    pio.renderers.default = 'browser'                                          # automatically opens the plot in a browser
                                           

import numpy as np
import data_output
import data_input


### (1) INTERACTIVE PLOTTING - Plotly
def plot_branch(direction:str) -> None:
    if data_input.df_supply_in.empty:
        print("Input DataFrame is empty. No data is available for plotting.")
        return
    
    if len(data_input.df_supply_in) < 2:
        raise ValueError("Dataframe must have at least 2 rows to plot line segments.")
        return
    
    lons_supply = data_input.df_supply_in["Longitude"].values
    lats_supply = data_input.df_supply_in["Latitude"].values
    
    lons_return = data_input.df_return_in["Longitude"].values
    lats_return = data_input.df_return_in["Latitude"].values

    # Trace for lines - supply
    line_trace_supply = go.Scattermapbox(
        lon = lons_supply,
        lat = lats_supply,
        mode = 'lines',
        line = dict(color = 'red', width = 7),
        name = 'Supply',
        showlegend = True
    )
    # Trace for lines - return
    line_trace_return = go.Scattermapbox(
        lon = lons_return,
        lat = lats_return,
        mode = 'lines',
        line = dict(color = 'blue', width = 7),
        name = 'Return',
        showlegend = True
    )
    # Trace for nodes - supply
    node_trace_supply = go.Scattermapbox(
        lon = lons_supply,
        lat = lats_supply,
        mode = 'markers',
        marker = dict(size = 15, color='red'),
        #name = 'Nodes - supply',
        showlegend = False
    )
    # Trace for nodes - return
    node_trace_return = go.Scattermapbox(
        lon = lons_return,
        lat = lats_return,
        mode = 'markers',
        marker = dict(size = 15, color='blue'),
        #name = 'Nodes - return',
        showlegend = False
    )
    
    # Centering the map
    centre_lat = np.mean(lats_supply)
    centre_lon = np.mean(lons_supply)
    
    # Selects the direction of the flow
    if direction.lower() == "supply":
        fig = go.Figure(data=[line_trace_supply, node_trace_supply])
        map_title = "Configuration of the branch - supply"
    elif direction.lower() == "return":
        fig = go.Figure(data=[line_trace_return, node_trace_return])
        map_title = "Configuration of the branch - return"
    elif direction.lower() == "all":
        fig = go.Figure(data=[line_trace_supply, line_trace_return, node_trace_supply, node_trace_return])   # Inserting data into the Figure 
        map_title = "Configuration of the branch - supply and return"
    else:
        raise ValueError(f"Input ({direction}) not valid. Available options are 'supply', 'return', or 'all'.")
    
    fig.update_layout(
        mapbox = dict(
            style = 'open-street-map',                                         # Selects Open Street Map application as the source for the background map
            center = dict(lat = centre_lat, lon = centre_lon),
            zoom = 15
        ),
        margin = dict(l = 0, r = 0, t = 25, b = 0),
        title = map_title
    )
    fig.show()


def plot_insulation(direction:str) -> None:  
    if data_input.df_supply_in.empty:
        print("Input DataFrame is empty. No data is available for plotting.")
        return
    
    if direction.lower() == "supply":
        df = data_input.df_supply_in.copy()
        title_ins = "Original insulation thickness - supply"
    elif direction.lower() == "return":
        df = data_input.df_return_in.copy()
        title_ins = "Original insulation thickness - return"
    else:
        raise ValueError("Direction must be either 'supply' or 'return'.")
        return
        
    lons = df["Longitude"].values
    lats = df["Latitude"].values
    thickness = df["Insulation"].astype(float).values   

    # Check values are in valid range - Must be in [0, 1]
    if not np.all((0 <= thickness) & (thickness <= 1)):
        raise ValueError("Insulation thickness values must be between 0 and 1.")
        
    # Get color from Turbo colormap
    cmap = cm.get_cmap('turbo')
    #cmap = cm.get_cmap('hot')
    hex_colors = [colors.to_hex(cmap(t)) for t in thickness]
    # Create line segments with manually assigned colors
    line_traces = []
    for i in range(len(df) - 1):
        segment = go.Scattermapbox(
            lon = [lons[i], lons[i + 1]],
            lat = [lats[i], lats[i + 1]],
            mode = "lines",
            line = dict(
                color = hex_colors[i],
                width = 7
            ),
            hovertemplate = f"Insulation: {thickness[i]:.2f}<extra></extra>",
            showlegend = False
        )
        line_traces.append(segment)
    # Add black node markers
    node_trace = go.Scattermapbox(
        lon = lons,
        lat = lats,
        mode = 'markers',
        marker = dict(size = 8, color = 'black'),
        name= 'Nodes',
        showlegend = False,
        hoverinfo = 'skip'
    )
    # Calculate map center (before using it in the colorbar trace)
    centre_lat = np.mean(lats)
    centre_lon = np.mean(lons)
    
    # Dummy trace for colorbar
    colorbar_trace = go.Scattermapbox(
        lon = [centre_lon],
        lat = [centre_lat],
        mode = 'markers',
        marker = dict(
            size = 0,
            opacity = 0,
            color = [0],
            colorscale = 'turbo',
            cmin = 0,
            cmax = 1,
            colorbar = dict(
                title = 'Thickness [%]',
                tickvals = [0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1],
                ticktext = ["0", "10", "20", "30", "40", "50", "60", "70", "80", "90", "100"],
                len = 0.75
            )
        ),
        showlegend = False,
        hoverinfo = 'none'
    )
    
    # Build and show figure
    fig = go.Figure(data = line_traces + [node_trace, colorbar_trace])
    fig.update_layout(
        mapbox = dict(
            style = 'open-street-map',
            center = dict(lat = centre_lat, lon = centre_lon),
            zoom = 15
        ),
        margin = dict(l = 0, r = 0, t = 25, b = 0),
        title = title_ins
    )
    fig.show()


def plot_output_heatmap(direction:str, value_column:str) -> None:
    """
    Plot line segments on a map using a single DataFrame that contains
    longitude, latitude, and a value column for coloring.

    Parameters
    ----------
    direction : str
        Pipeline direction flow - 'supply' or 'return'.
    value_column : str
        Column in the dataframe to use for coloring the segments.
    Returns
    -------
    None
    """
    if direction.lower() == "supply":
        data_df = data_output.df_supply_out
        title_graph = value_column + " - supply"
    elif direction.lower() == "return":
        data_df = data_output.df_return_out
        title_graph = value_column + " - return"
    else:
        raise ValueError("Direction must be either 'supply' or 'return'.")
    
    if data_df.empty:
        print("Output DataFrame is empty. No data is available for plotting.")
        return
    
    if len(data_df) < 2:
        raise ValueError("Dataframe must have at least 2 rows to plot line segments.")
        return

    # Extract coordinates and values
    lons = data_df["Longitude"].values
    lats = data_df["Latitude"].values
    values = data_df[value_column].astype(float).values

    # Use values at the *end* of each segment for colouring
    #values_for_segments = values[1:]
    values_for_segments = values[0:]

    # Normalize for colormap
    vmin, vmax = values_for_segments.min(), values_for_segments.max()
    norm_values = (values_for_segments - vmin) / (vmax - vmin + 1e-12)

    # Get colours (colour scale)
    cmap = cm.get_cmap("turbo")
    #cmap = cm.get_cmap("hot")
    hex_colors = [colors.to_hex(cmap(v)) for v in norm_values]

    # Create line segments between consecutive points
    line_traces = []
    for i in range(len(data_df) - 1):
        trace = go.Scattermapbox(
            lon = [lons[i], lons[i + 1]],
            lat = [lats[i], lats[i + 1]],
            mode = "lines",
            line = dict(
                color = hex_colors[i],
                width = 6
            ),
            hovertemplate = f"{value_column}: {values_for_segments[i]:.2f}<extra></extra>",
            showlegend = False
        )
        line_traces.append(trace)

    # Optional node markers
    node_trace = go.Scattermapbox(
        lon = lons,
        lat = lats,
        mode = 'markers',
        marker = dict(size = 7, color = 'black'),
        #name = 'Node',
        showlegend = False,
        hoverinfo = 'skip'
    )

    # Dummy trace for colorbar
    colorbar_trace = go.Scattermapbox(
        lon = [None],
        lat = [None],
        mode = 'markers',
        marker = dict(
            size = 0.1,
            color = np.linspace(vmin, vmax, 100),
            colorscale = 'turbo',
            #colorscale = 'hot',
            cmin = vmin,
            cmax = vmax,
            colorbar = dict(
                title = value_column,
                len = 0.75
            )
        ),
        showlegend = False,
        hoverinfo = 'none'
    )

    # Centre of the map
    centre_lat = np.mean(lats)
    centre_lon = np.mean(lons)

    # Build the figure
    fig = go.Figure(data = line_traces + [node_trace, colorbar_trace])
    fig.update_layout(
        mapbox = dict(
            style = 'open-street-map',
            center = dict(lat = centre_lat, lon = centre_lon),
            zoom = 15
        ),
        margin = dict(l = 0, r = 0, t = 25, b = 0),
        title = title_graph
    )
    fig.show()


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
### STATIC PLOTTING - matplotlib 
def plot_temperature(direction:str) -> None:
    if direction.lower() == "supply":
        df_out = data_output.df_supply_out
        title = "Supply temperature"
    elif direction.lower() == "return":
        df_out = data_output.df_return_out
        title = "Return temperature"
    else:
        raise ValueError("Direction must be either 'supply' or 'return'.")
    
    if df_out.empty:
        print("Output DataFrame is empty. No data is available for plotting.")
        return
        
    plt.plot(df_out["L tot [m]"], df_out["T [°C]"], marker='.')
    plt.xlabel("L [m]")
    plt.ylabel("T [°C]")
    plt.title(title)
    plt.minorticks_on()  
    plt.grid(which='major', linestyle='-', linewidth=0.75, alpha=0.7)
    plt.grid(which='minor', linestyle=':', linewidth=0.5, alpha=0.4)
    plt.tight_layout()
    plt.show()


def plot_heat_flow_loss(direction:str) -> None:
    if direction.lower() == "supply":
        df_out = data_output.df_supply_out
        title = "Heat flow loss - supply"
    elif direction.lower() == "return":
        df_out = data_output.df_return_out
        title = "Heat flow loss - return"
    else:
        raise ValueError("Direction must be either 'supply' or 'return'.") 
    
    if df_out.empty:
        print("Output DataFrame is empty. No data is available for plotting.")
        return
    
    plt.plot(df_out["L tot [m]"], df_out["Qdot loss [W]"], marker='.')
    plt.xlabel("L [m]")
    plt.ylabel(r"$\dot{Q}_{LOSS}$ [W]")
    plt.title(title)
    plt.minorticks_on()  
    plt.grid(which='major', linestyle='-', linewidth=0.75, alpha=0.7)
    plt.grid(which='minor', linestyle=':', linewidth=0.5, alpha=0.4)
    plt.tight_layout()
    plt.show()
    
  
def plot_normalised_heat_flow_loss(direction:str) -> None:
    if direction.lower() == "supply":
        df_out = data_output.df_supply_out
        title = "Normalised heat flow loss - supply"
    elif direction.lower() == "return":
        df_out = data_output.df_return_out
        title = "Normalised heat flow loss - return"
    else:
        raise ValueError("Direction must be either 'supply' or 'return'.") 
    
    if df_out.empty:
        print("Output DataFrame is empty. No data is available for plotting.")
        return
    
    plt.plot(df_out["L tot [m]"], df_out["qdot loss [W/m]"], marker='.')
    plt.xlabel("L [m]")
    plt.ylabel(r"$\dot{q}_{LOSS}$ [W/m]")
    plt.title(title)
    plt.minorticks_on()  
    plt.grid(which='major', linestyle='-', linewidth=0.75, alpha=0.7)
    plt.grid(which='minor', linestyle=':', linewidth=0.5, alpha=0.4)
    plt.tight_layout()
    plt.show()
    

def plot_total_heat_flow_loss(direction:str) -> None:
    if direction.lower() == "supply":
        df_out = data_output.df_supply_out
        title = "Total heat flow loss - supply"
    elif direction.lower() == "return":
        df_out = data_output.df_return_out
        title = "Total heat flow loss - return"
    else:
        raise ValueError("Direction must be either 'supply' or 'return'.") 
    
    if df_out.empty:
        print("Output DataFrame is empty. No data is available for plotting.")
        return
    
    plt.plot(df_out["L tot [m]"], df_out["Qdot loss total [W]"], marker='.')
    plt.xlabel("L [m]")
    plt.ylabel(r"$\dot{q}_{LOSS}$ [W/m]")
    plt.title(title)
    plt.minorticks_on()  
    plt.grid(which='major', linestyle='-', linewidth=0.75, alpha=0.7)
    plt.grid(which='minor', linestyle=':', linewidth=0.5, alpha=0.4)
    plt.tight_layout()
    plt.show()
    

def plot_mass_flow(direction:str) -> None:
    if direction.lower() == "supply":
        df_out = data_output.df_supply_out
        title = "Mass flow - supply"
    elif direction.lower() == "return":
        df_out = data_output.df_return_out
        title = "Mass flow - return"
    else:
        raise ValueError("Direction must be either 'supply' or 'return'.") 
    
    if df_out.empty:
        print("Output DataFrame is empty. No data is available for plotting.")
        return
    
    plt.plot(df_out["L tot [m]"], df_out["mdot [kg/s]"], marker='.')
    plt.xlabel("L [m]")
    plt.ylabel(r"$\dot{q}_{LOSS}$ [W/m]")
    plt.title(title)
    plt.minorticks_on()  
    plt.grid(which='major', linestyle='-', linewidth=0.75, alpha=0.7)
    plt.grid(which='minor', linestyle=':', linewidth=0.5, alpha=0.4)
    plt.tight_layout()
    plt.show()
    

def plot_heat_flow_loss_nodes(direction:str) -> None:
    if direction.lower() == "supply":
        df_out = data_output.df_supply_out
        title = "Heat flow loss (nodes) - supply"
    elif direction.lower() == "return":
        df_out = data_output.df_return_out
        title = "Heat flow loss (nodes) - return"
    else:
        raise ValueError("Direction must be either 'supply' or 'return'.") 
    
    if df_out.empty:
        print("Output DataFrame is empty. No data is available for plotting.")
        return
    
    colorQ = df_out["Qdot loss [W]"]
    # # Create scatter plot
    # plt.figure(figsize=(8, 6))
    scatter = plt.scatter(
         df_out["Longitude"],
         df_out["Latitude"],
         c = colorQ,
         cmap = plt.cm.get_cmap("turbo")
         #cmap=plt.cm.get_cmap("hot")
    )
    # Add vertical colourbar
    cbar = plt.colorbar(
         scatter,
         orientation = "vertical",
         pad = 0.1,
         shrink = 0.8,
         format = "%.0f",
         label = r"$\dot{Q}_{LOSS}$ [W]"
    )
    # # # Add label manually above the colorbar
    # # cbar.ax.text(
    # #     0.5, 1.05,  # (x, y) position in axes coordinates
    # #     r'$\dot{Q}_{\mathrm{LOSS}}$ [W]',
    # #     ha='center',
    # #     va='bottom',
    # #     transform=cbar.ax.transAxes
    # # )
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(title)
    plt.minorticks_on()  
    plt.grid(which='major', linestyle='-', linewidth=0.75, alpha=0.7)
    plt.grid(which='minor', linestyle=':', linewidth=0.5, alpha=0.4)
    plt.tight_layout()
    plt.show()

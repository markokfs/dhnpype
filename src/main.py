import branch
import data_input
import data_output


def plot_config() -> None:
    """
    Calls the plot_branch() function in plots.py and plots the supply and return pipelines on a map. It also plots insulation thicknesses of supply and return line from the plot_insulation() function. 

    Returns
    -------
        None
    """
    from plots import plot_branch, plot_insulation, plot_mass_flow
    plot_branch("all")                                                         # Plots the configuration of the pipeline
    plot_insulation("supply")                                                  # Plots the thickness of the supply pipeline insulation
    plot_insulation("return")                                                  # Plots the thickness of the return pipeline insulation
    plot_mass_flow("supply")                                                   # Plots the mass flow values for each node
    plot_mass_flow("return")                                                   # Plots the mass flow values for each node


def plot_branch_dir() -> None:
    """
    Calls the plot_branch() function in plots.py and plots the supply and return configuration of the network separately. 

    Returns
    -------
        None
    """
    from plots import plot_branch
    plot_branch("supply")
    plot_branch("return")

    
def plot_temperature() -> None:
    """
    Calls the plot_supply_temperature() function in plots.py and plots the supply and return temperatures. 

    Returns
    -------
        None
    """
    from plots import plot_temperature
    plot_temperature("supply")
    plot_temperature("return")
    

def plot_losses() -> None:
    """
    Calls the functions to plot heat flow losses in a static plot:
        - plot_heat_flow_loss(): for absolute heat flow losses
        - plot_normalised_heat_flow_loss(): shows losses that have been normalised with respect to the length of the pipeline section
    
    Also calls the plot_output_heatmap() function in plots.py to plot interactive heatmaps of results in the supply and return line superimposed on the map. 
        
    Returns
    -------
        None
    """
    from plots import plot_heat_flow_loss, plot_normalised_heat_flow_loss, plot_total_heat_flow_loss, plot_output_heatmap
    plot_heat_flow_loss("supply")
    plot_heat_flow_loss("return")
    plot_normalised_heat_flow_loss("supply")
    plot_normalised_heat_flow_loss("return")
    plot_total_heat_flow_loss("supply")
    plot_total_heat_flow_loss("return")
    
    # Heatmap:
    plot_output_heatmap("supply", "Qdot loss [W]")
    plot_output_heatmap("supply", "qdot loss [W/m]")
    plot_output_heatmap("supply", "Qdot loss total [W]")
    plot_output_heatmap("supply", "mdot [kg/s]")
    plot_output_heatmap("return", "Qdot loss [W]")
    plot_output_heatmap("return", "qdot loss [W/m]")
    plot_output_heatmap("return", "Qdot loss total [W]")
    plot_output_heatmap("return", "mdot [kg/s]")
   
    
def main():
    """
    Runs the analysis in a Python environment.
    
    Returns
    -------
        None
    """
    # RUN THE CALCULATIONS
    network = branch.Branch()
    network.calculate_supply()
    network.calculate_return()
    network.calculate_system_heat_flow()
    
    # PLOT RESULTS
    plot_config()
    #plot_branch_dir()
    plot_temperature()
    plot_losses()
    
    

if __name__ == '__main__':
    main()
    

    
    
    
    
import os
import re
import ast
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick 
import seaborn as sns

def extract_metrics_from_file(file_contents):
    metrics = {
        'fuel_consumption': r'average fuel consumption for .*? scenario.*? \(in mg\):\s*([\d\.]+)',
        'waiting_time': r'average waiting time for .*? scenario.*? \(in s\):\s*([\d\.]+)',
        'time_loss': r'average time loss for .*? scenario.*? \(in s\):\s*([\d\.]+)',
        'queue_length': r'average queue length for .*? scenario.*? \(in m\):\s*([\d\.]+)',
        'pedestrian_time_loss': r'average pedestrian time loss for .*? scenario.*? \(in s\):\s*([\d\.]+)',
        'right_turn_conflicts': r'number of right-turn conflicts between vehicles and pedestrians:\s*(\d+)',
        'cavs_passing': r'number of CAVs passing through the specific intersection.*?scenario:\s*(\d+)',
        'pedestrians_passing': r'number of pedestrians passing through the specific intersection.*?scenario:\s*(\d+)',
        'simulation_termination_time': r'The time of simulation termination.*?scenario:\s*([\d\.]+)',
        'phase_lengths': r'average phase lengths:\s*({.*?})',
        'phase_occurrences': r'number of times each phase happened:\s*({.*?})',
    }
    
    extracted_metrics = {}
    
    for metric, pattern in metrics.items():
        match = re.search(pattern, file_contents)
        if match:
            extracted_metrics[metric] = match.group(1)
        else:
            extracted_metrics[metric] = None
    
    # Convert phase_lengths and phase_occurrences from strings to dictionaries
    for key in ['phase_lengths', 'phase_occurrences']:
        if extracted_metrics[key]:
            try:
                extracted_metrics[key] = ast.literal_eval(extracted_metrics[key])
            except (ValueError, SyntaxError):
                extracted_metrics[key] = None  # Handle invalid dictionary strings
    
    return extracted_metrics

def read_results_files(directory_path='Results'):
    directory_path = directory_path

    pattern = r'Metrics_(?P<ped_phasing>.*?)_Results_(?P<time>.*?)_penetration_(?P<penetration_value>[\d\.]+)\.txt'

    data = []

    for filename in os.listdir(directory_path):
        match = re.match(pattern, filename)
    
        if match:
            ped_phasing = match.group('ped_phasing')
            control_type = match.group('time')
            penetration = match.group('penetration_value')

            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, 'r') as file:
                    file_contents = file.read()

                    metrics = extract_metrics_from_file(file_contents)
                
                    data.append({
                        'ped_phasing': ped_phasing,
                        'control_type': control_type,
                        'penetration': penetration,
                        **metrics
                    })
            except Exception as e:
                print(f"Could not read file {filename}: {e}")

    df = pd.DataFrame(data)

    cols_list = [
        'penetration',
        'fuel_consumption',
        'waiting_time',
        'time_loss',
        'queue_length',
        'pedestrian_time_loss',
        'right_turn_conflicts',
        'cavs_passing',
        'pedestrians_passing',
        'simulation_termination_time',
    ]
    df[cols_list] = df[cols_list].apply(pd.to_numeric, errors='coerce')
    return df

def norm_by_fixed_time(df, cols_list, grp_cols):
    norm_df = df.copy()
    grped = df.groupby(grp_cols)
    for col in cols_list:
        for grp, grp_data in grped:
            fixed_time_values = grp_data[grp_data.control_type=='fixed_time'][col]
            norm_df.loc[grp_data.index, col] /= fixed_time_values.values
    return norm_df

def rel_percent_by_fixed_time(df, cols_list, grp_cols):
    """
    Calculate the relative percentage of specified columns based on 'fixed_time' control_type values within groups.

    Parameters:
    - df: DataFrame, the input data.
    - cols_list: list, columns to calculate relative percentage for.
    - grp_cols: list, columns to group by.

    Returns:
    - DataFrame, the DataFrame with relative percentages.
    """
    relative_df = df.copy()
    
    # Group by the specified columns
    grped = df.groupby(grp_cols)
    
    for col in cols_list:
        # Calculate relative percentage within each group
        relative_df[col] = grped[col].transform(
            lambda x: ((x - x[df.loc[x.index, 'control_type'] == 'fixed_time'].values[0]) / 
                       x[df.loc[x.index, 'control_type'] == 'fixed_time'].values[0])
        )
    
    return relative_df

def plot_selected_columns(df, x, y, kind='line', marker='o', **kwargs):
    """
    Plots selected columns x and y from a DataFrame using seaborn.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        x (str): The column name for the x-axis.
        y (str): The column name for the y-axis.
        kind (str): Type of plot to create. Options: 'line', 'scatter', 'bar'.
        marker (str): Marker style for data points (e.g., 'o', 's', 'D', etc.).
        **kwargs: Additional keyword arguments to pass to the seaborn plotting function.
    """
    # Set the style of seaborn
    sns.set(style="whitegrid")
    
    # Create the plot based on the kind specified
    if kind == 'line':
        sns.lineplot(data=df, x=x, y=y, marker=marker, **kwargs)
    elif kind == 'scatter':
        sns.scatterplot(data=df, x=x, y=y, **kwargs)
    elif kind == 'bar':
        sns.barplot(data=df, x=x, y=y, **kwargs)
    else:
        raise ValueError(f"Unsupported plot kind: {kind}. Use 'line', 'scatter', or 'bar'.")
    
    # Add labels and title
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(f'{kind.capitalize()} plot of {x} vs {y}')
    
    # Show the plot
    plt.show()

def plot_matrix(df, selected_columns, x, kind='line', marker='o', export=False, filename='matrix_plot.png', percentage=False, column_labels=None, **kwargs):
    """
    Creates a 2x3 matrix plot where:
    - Rows represent 'ped_phasing'.
    - Columns represent selected columns (y-axis values).
    - Hue represents 'control_type'.
    - Y-labels indicate 'Concurrent' and 'Exclusive'.
    - Column labels (e.g., 'waiting time') are added above each column or titles are removed.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        selected_columns (list): List of column names to plot (must be 3 columns for a 2x3 grid).
        x (str): The column name for the x-axis.
        kind (str): Type of plot to create. Options: 'line', 'scatter', 'bar'.
        marker (str): Marker style for data points (e.g., 'o', 's', 'D', etc.).
        export (bool): Whether to export the plot to a file. Default is False.
        filename (str): Name of the file to save the plot. Default is 'matrix_plot.png'.
        percentage (bool): Whether to display y-axis values as percentages. Default is False.
        column_labels (list): List of labels for each column (e.g., ['waiting time', 'speed', 'distance']).
                              If None, subplot titles are removed.
        **kwargs: Additional keyword arguments to pass to the seaborn plotting function.
    """
    # Set the style of seaborn
    sns.set(style="whitegrid")
    
    # Define the hue variable
    hue_var = 'control_type'
    
    # Define the fixed order for control_type
    control_type_order = ['fixed_time', 'actuated', 'multi_scale']
    
    # Define the ped_phasing types
    ped_phasing_types = df['ped_phasing'].unique()  # ['Concurrent', 'Exclusive']
    
    # Ensure exactly 3 columns are selected for a 2x3 grid
    if len(selected_columns) != 3:
        raise ValueError("Please provide exactly 3 columns for the 2x3 grid.")
    
    # Create a 2x3 grid of subplots
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(18, 12))
    # fig.suptitle(f'{kind.capitalize()} Plots by Ped Phasing and Selected Columns', fontsize=16)
    
    # Add column labels above each column if provided
    if column_labels:
        for ax, col_label in zip(axes[0], column_labels):
            ax.set_title(col_label, fontsize=14, pad=20)  # Add label above each column
    
    # Iterate through each combination and plot
    for i, ped_phasing in enumerate(ped_phasing_types):
        for j, column in enumerate(selected_columns):
            # Filter the data for the current ped_phasing
            subset = df[df['ped_phasing'] == ped_phasing]
            
            # Select the current subplot
            ax = axes[i, j]
            
            # Plot based on the kind specified
            if kind == 'line':
                sns.lineplot(data=subset, x=x, y=column, hue=hue_var, hue_order=control_type_order, marker=marker, ax=ax, **kwargs)
            elif kind == 'scatter':
                sns.scatterplot(data=subset, x=x, y=column, hue=hue_var, hue_order=control_type_order, ax=ax, **kwargs)
            elif kind == 'bar':
                sns.barplot(data=subset, x=x, y=column, hue=hue_var, hue_order=control_type_order, ax=ax, **kwargs)
            else:
                raise ValueError(f"Unsupported plot kind: {kind}. Use 'line', 'scatter', or 'bar'.")
            
            if i==0:
                ax.set_title(f'{column.replace("_", " ")}')

            # Set x and y labels (remove underscores)
            ax.set_xlabel(f'{x.replace("_", " ")}')
            if j==0:            
                ax.set_ylabel(f'{ped_phasing.replace("_", " ")}')  # Add ped_phasing to y-label
            else:
                ax.set_ylabel('')
            
            # Format y-axis as percentages if percentage=True
            if percentage:
                ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))  # Assumes values are in [0, 1]
    
    # Adjust layout
    plt.tight_layout()
    
    # Export the plot if requested
    if export:
        # Define the path to the 'Results' folder
        results_folder = os.path.join('Results')
        
        # Create 'Results' folder if it doesn't exist
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
        
        # Save the plot to the 'Results' folder
        filepath = os.path.join(results_folder, filename)
        plt.savefig(filepath, bbox_inches='tight')  # Save the plot to a file
        print(f"Matrix plot saved as {filepath}")
    
    # Show the plot
    plt.show()

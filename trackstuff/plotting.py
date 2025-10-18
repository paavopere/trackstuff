"""Plotting functionality for trackers."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def make_title(x: str, y: str, name: str | None = None) -> str:
    """
    Create a title for the plot.
    """
    if isinstance(name, str):
        return f"{name}: {y}({x})"
    else:
        return f"{y}({x})"


def plot_to_file(df: pd.DataFrame, x: str, y: str, path: Path, name: str | None = None) -> None:
    """
    Create a plot from a DataFrame and save it to the specified path.
    
    Args:
        df: DataFrame with the data to plot
        x: Column name for x-axis (will be parsed as dates)
        y: Column name for y-axis
        path: Path where to save the PNG file
        name: Optional name for the plot title
    """
    title = make_title(x, y, name)
    
    # Make a copy and parse dates
    plot_df = df.copy()
    plot_df[x] = pd.to_datetime(plot_df[x])
    plot_df.set_index(x, inplace=True)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_df[y].plot(ax=ax, marker='o', linestyle='-', markersize=4)
    ax.set_title(title)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(path)
    plt.close(fig)


def plot_to_terminal(df: pd.DataFrame, x: str, y: str, name: str | None = None) -> None:
    """
    Plot data in the terminal using plotext.
    
    Args:
        df: DataFrame with the data to plot
        x: Column name for x-axis (will be parsed as dates)
        y: Column name for y-axis
        name: Optional name for the plot title
    """
    import plotext as plt_term
    
    title = make_title(x, y, name)
    
    # Make a copy and parse dates
    plot_df = df.copy()
    plot_df[x] = pd.to_datetime(plot_df[x])
    
    # For plotting with plotext, we need numerical x-values
    # Convert dates to integer indices for plotting
    values = plot_df[y].values
    indices = list(range(len(values)))
    dates_str = plot_df[x].dt.strftime('%Y-%m-%d').tolist()
    
    # Draw the plot
    plt_term.scatter(indices, values)
    plt_term.plot(indices, values, marker="dot", color="green")
    
    # Set custom tick labels on x-axis with actual dates
    # Only show a subset of dates to avoid overcrowding
    step = max(1, len(dates_str) // 10)  # Show approximately 10 dates
    plt_term.xticks(indices[::step], dates_str[::step])
    
    plt_term.title(title)
    plt_term.xlabel(x)
    plt_term.ylabel(y)
    plt_term.theme("clear")
    plt_term.plotsize(100, 30)
    plt_term.grid(True)

    plt_term.show()


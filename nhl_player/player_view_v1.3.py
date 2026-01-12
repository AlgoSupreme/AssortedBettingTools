import tkinter as tk
from tkinter import ttk
import json
import os
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import scipy.stats as stats
import matplotlib.ticker as ticker

# ---------------------------------------------------------
# 1. THE DATA
# ---------------------------------------------------------

file_path = os.path.join("data_dump", "player_analysis2026-01-11.json")

# Fallback for local testing
if not os.path.exists(file_path):
    file_path = "player_analysis2026-01-11.json"

if os.path.exists(file_path):
    with open(file_path, "r") as f:
        raw_data = json.load(f)
else:
    raw_data = {}

# ---------------------------------------------------------
# 2. DATA PROCESSING
# ---------------------------------------------------------

player_data = {}
sorted_names = []

for pid, data in raw_data.items():
    name = data.get("Name", "Unknown")
    
    # Extract the raw game-by-game arrays
    goals_arr = data.get("goals", [])
    assists_arr = data.get("assists", [])
    shots_arr = data.get("shots", [])
    
    # Calculate Points per game (Goals + Assists)
    points_arr = []
    length = min(len(goals_arr), len(assists_arr)) 
    for i in range(length):
        points_arr.append(goals_arr[i] + assists_arr[i])
        
    player_data[name] = {
        "Goals": np.array(goals_arr),
        "Assists": np.array(assists_arr),
        "Points": np.array(points_arr),
        "Shots": np.array(shots_arr)
    }
    sorted_names.append(name)

sorted_names.sort()

# ---------------------------------------------------------
# 3. TKINTER GUI SETUP
# ---------------------------------------------------------

class PlayerGameAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Player Performance Analyzer")
        self.root.geometry("1100x950")

        # Top Frame for Controls
        top_frame = tk.Frame(root, pady=10, bg="#f0f0f0")
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # 1. Player Selection
        tk.Label(top_frame, text="Select Player:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(15, 5))
        self.combo_player = ttk.Combobox(top_frame, values=sorted_names, state="readonly", width=20)
        self.combo_player.pack(side=tk.LEFT, padx=5)
        self.combo_player.bind("<<ComboboxSelected>>", self.update_plot)
        if sorted_names:
            self.combo_player.current(0)

        # 2. Metric Selection
        tk.Label(top_frame, text="Metric:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(15, 5))
        self.metrics = ["Points", "Goals", "Assists", "Shots"]
        self.combo_metric = ttk.Combobox(top_frame, values=self.metrics, state="readonly", width=10)
        self.combo_metric.pack(side=tk.LEFT, padx=5)
        self.combo_metric.current(0) 
        self.combo_metric.bind("<<ComboboxSelected>>", self.update_plot)

        # 3. User Input for Comparison (New Feature)
        tk.Label(top_frame, text="Compare Value:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(20, 5))
        
        self.entry_ref_val = tk.Entry(top_frame, width=8)
        self.entry_ref_val.pack(side=tk.LEFT, padx=5)
        self.entry_ref_val.bind("<Return>", self.update_plot) # Update on Enter key

        self.btn_update = tk.Button(top_frame, text="Update Graph", command=self.update_plot, bg="#dddddd")
        self.btn_update.pack(side=tk.LEFT, padx=10)

        # Main Plot Area
        self.figure = Figure(figsize=(9, 7), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Initial Plot
        self.update_plot()

    def update_plot(self, event=None):
        player_name = self.combo_player.get()
        selected_metric = self.combo_metric.get()

        if not player_name or player_name not in player_data:
            return

        # Clear Axes
        self.ax.clear()

        # Get Data
        game_values = player_data[player_name][selected_metric]
        
        if len(game_values) == 0:
            self.ax.text(0.5, 0.5, "No data available.", ha='center', va='center')
            self.canvas.draw()
            return

        # Calculate Stats
        mu = np.mean(game_values)
        sigma = np.std(game_values)
        
        # Determine X-Axis Range
        min_val = min(game_values)
        max_val = max(game_values)
        
        # Extend range slightly for the bell curve
        x_start = min_val - 2
        x_end = max_val + 3
        if sigma > 0:
            x_start = mu - 4*sigma
            x_end = mu + 4*sigma
        
        x_range = np.linspace(x_start, x_end, 1000)

        # -----------------------------------------------------
        # 1. PLOT HISTOGRAM (Actuals)
        # -----------------------------------------------------
        bins = np.arange(np.floor(x_start), np.ceil(x_end) + 1) - 0.5
        self.ax.hist(game_values, bins=bins, density=True, alpha=0.2, color='orange', edgecolor='black', label='Actual Game Frequency')

        # -----------------------------------------------------
        # 2. PLOT NORMAL DISTRIBUTION (Standard Distribution)
        # -----------------------------------------------------
        line_height = 0
        
        if sigma > 0:
            y_pdf = stats.norm.pdf(x_range, mu, sigma)
            self.ax.plot(x_range, y_pdf, color='#007acc', linewidth=3, label='Standard Distribution')
            self.ax.fill_between(x_range, y_pdf, color='#007acc', alpha=0.1)
            line_height = np.max(y_pdf) * 1.1
        else:
            line_height = 1.0
            self.ax.axvline(mu, color='#007acc', linewidth=3, linestyle='--', label='Constant Performance')

        self.ax.set_ylim(0, line_height)

        # -----------------------------------------------------
        # 3. PLOT STANDARD DEVIATION LINES
        # -----------------------------------------------------
        # Mean Line
        self.ax.vlines(mu, 0, line_height, color='black', linestyle='dashed', alpha=0.8, label='Mean')
        
        # Sigma Lines
        if sigma > 0:
            styles = {1: (':', 0.6), 2: (':', 0.3)}
            for s in [1, 2]:
                linestyle, alpha = styles[s]
                # Positive Sigma
                val_pos = mu + (s * sigma)
                self.ax.vlines(val_pos, 0, line_height * 0.9, color='gray', linestyle=linestyle, alpha=alpha)
                # Negative Sigma
                val_neg = mu - (s * sigma)
                self.ax.vlines(val_neg, 0, line_height * 0.9, color='gray', linestyle=linestyle, alpha=alpha)

        # -----------------------------------------------------
        # 4. PLOT USER REFERENCE VALUE
        # -----------------------------------------------------
        user_val_str = self.entry_ref_val.get()
        if user_val_str and sigma > 0:
            try:
                ref_val = float(user_val_str)
                
                # Draw the User's Line
                self.ax.vlines(ref_val, 0, line_height, color='magenta', linewidth=3, label=f'Ref: {ref_val}')
                
                # Calculate Probabilities (Using Normal Distribution CDF)
                pct_below = stats.norm.cdf(ref_val, mu, sigma) * 100
                pct_above = 100 - pct_below
                
                # Annotate Plot with Percentages
                # Text for "Above" (Right side of line)
                self.ax.text(ref_val, line_height * 0.85, 
                             f"  ABOVE: {pct_above:.1f}%\n  (Likelihood > {ref_val})", 
                             color='magenta', fontweight='bold', ha='left', va='center')
                
                # Text for "Below" (Left side of line)
                self.ax.text(ref_val, line_height * 0.85, 
                             f"BELOW: {pct_below:.1f}%  \n(Likelihood < {ref_val})  ", 
                             color='magenta', fontweight='bold', ha='right', va='center')

            except ValueError:
                pass # User entered text instead of number

        # -----------------------------------------------------
        # COSMETICS & STATS
        # -----------------------------------------------------
        self.ax.set_title(f"{player_name}: {selected_metric} per Game Distribution", fontsize=14, fontweight='bold', pad=15)
        self.ax.set_xlabel(f"{selected_metric} Count", fontsize=11)
        self.ax.set_ylabel("Probability Density", fontsize=11)
        
        self.ax.legend(loc='upper right', frameon=True)
        self.ax.grid(True, linestyle='--', alpha=0.4)
        
        # Stats Box
        stats_text = (f"Mean: {mu:.2f}\n"
                      f"Std Dev: {sigma:.2f}\n"
                      f"Games: {len(game_values)}")
        
        self.ax.text(0.02, 0.95, stats_text, transform=self.ax.transAxes, 
                     fontsize=10, verticalalignment='top', 
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

        self.canvas.draw()

# ---------------------------------------------------------
# 4. MAIN EXECUTION
# ---------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = PlayerGameAnalysisApp(root)
    root.mainloop()
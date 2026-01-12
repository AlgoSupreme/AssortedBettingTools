import tkinter as tk
from tkinter import ttk
import json
import os
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------------------------------------------
# 1. THE DATA
# ---------------------------------------------------------

file_path = os.path.join("data_dump", "goalie_analysis_sog_sv_gl2026-01-11.json")

if os.path.exists(file_path):
    with open(file_path, "r") as f:
        goalie_data = json.load(f)
else:
    goalie_data = {}

# ---------------------------------------------------------
# 2. DATA PROCESSING
# ---------------------------------------------------------

name_to_id = {}
sorted_names = []

for gid, data in goalie_data.items():
    name = data.get("Name", "Unknown")
    name_to_id[name] = gid
    sorted_names.append(name)

sorted_names.sort()

# ---------------------------------------------------------
# 3. TKINTER GUI SETUP
# ---------------------------------------------------------

class GoalieApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Goalie Performance Viewer")
        self.root.geometry("1000x950")

        # Top Frame for Controls
        top_frame = tk.Frame(root, pady=10, bg="#f0f0f0")
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # 1. Goalie Selection
        tk.Label(top_frame, text="Select Goalie:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(15, 5))
        self.combo_goalie = ttk.Combobox(top_frame, values=sorted_names, state="readonly", width=20)
        self.combo_goalie.pack(side=tk.LEFT, padx=5)
        self.combo_goalie.bind("<<ComboboxSelected>>", self.update_plot)

        # 2. Chart Style Selection
        tk.Label(top_frame, text="Style:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(15, 5))
        self.chart_styles = ["Trend (Combined)", "Trend (Separate)", "Gaussian Distribution"]
        self.combo_style = ttk.Combobox(top_frame, values=self.chart_styles, state="readonly", width=18)
        self.combo_style.current(0)
        self.combo_style.pack(side=tk.LEFT, padx=5)
        self.combo_style.bind("<<ComboboxSelected>>", self.update_plot)

        # 3. Reference Value Input (New)
        tk.Label(top_frame, text="Ref Value (Median):", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(15, 5))
        
        self.entry_ref = tk.Entry(top_frame, width=8)
        self.entry_ref.pack(side=tk.LEFT, padx=5)
        self.entry_ref.bind("<Return>", self.update_plot) # Update on Enter key

        btn_apply = tk.Button(top_frame, text="Apply", command=lambda: self.update_plot(None), bg="#e1e1e1")
        btn_apply.pack(side=tk.LEFT, padx=5)

        # Graph Area
        self.figure = Figure(figsize=(8, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Default Selection
        if sorted_names:
            self.combo_goalie.set(sorted_names[0])
            self.update_plot(None)

    def update_plot(self, event):
        selected_name = self.combo_goalie.get()
        selected_style = self.combo_style.get()
        
        # Get Reference Value
        ref_val = None
        raw_ref = self.entry_ref.get().strip()
        if raw_ref:
            try:
                ref_val = float(raw_ref)
            except ValueError:
                pass # Ignore invalid input

        if not selected_name:
            return

        gid = name_to_id[selected_name]
        data = goalie_data[gid]

        shots = data.get("shotsAgainst", [])
        saves = data.get("saves", [])
        goals = data.get("goalsAgainst", [])
        games = list(range(1, len(shots) + 1))

        self.figure.clf()

        if selected_style == "Trend (Combined)":
            self.draw_trend_combined(games, shots, saves, goals, selected_name)
        elif selected_style == "Trend (Separate)":
            self.draw_trend_separate(games, shots, saves, goals, selected_name)
        elif selected_style == "Gaussian Distribution":
            self.draw_gaussian(shots, saves, goals, selected_name, ref_val)

        self.canvas.draw()

    # ---------------------------------------------------------
    # PLOTTING HELPERS
    # ---------------------------------------------------------

    def draw_trend_combined(self, games, shots, saves, goals, name):
        ax = self.figure.add_subplot(111)
        ax.plot(games, shots, marker='o', linestyle='-', label='Shots', color='blue')
        ax.plot(games, saves, marker='x', linestyle='--', label='Saves', color='green')
        ax.plot(games, goals, marker='s', linestyle='-', label='Goals', color='red')
        ax.set_title(f"Performance Stats (Combined): {name}")
        ax.set_xlabel("Game Number")
        ax.set_ylabel("Count")
        ax.legend()
        ax.grid(True)

    def draw_trend_separate(self, games, shots, saves, goals, name):
        ax1 = self.figure.add_subplot(311)
        ax2 = self.figure.add_subplot(312)
        ax3 = self.figure.add_subplot(313)

        ax1.plot(games, shots, marker='o', color='blue')
        ax1.set_title(f"Shots Trend: {name}")
        ax1.grid(True)

        ax2.plot(games, saves, marker='x', color='green')
        ax2.set_title("Saves Trend")
        ax2.grid(True)

        ax3.plot(games, goals, marker='s', color='red')
        ax3.set_title("Goals Trend")
        ax3.set_xlabel("Game Number")
        ax3.grid(True)
        self.figure.tight_layout()

    def draw_gaussian(self, shots, saves, goals, name, ref_val):
        ax1 = self.figure.add_subplot(311)
        ax2 = self.figure.add_subplot(312)
        ax3 = self.figure.add_subplot(313)

        self.plot_single_gaussian(ax1, shots, "Shots Against", "blue", ref_val)
        self.plot_single_gaussian(ax2, saves, "Saves", "green", ref_val)
        self.plot_single_gaussian(ax3, goals, "Goals Against", "red", ref_val)
        
        ax3.set_xlabel("Count per Game")
        self.figure.tight_layout()

    def plot_single_gaussian(self, ax, data, metric_name, color, ref_val):
        if not data or len(data) < 2:
            ax.text(0.5, 0.5, "Insufficient Data", ha='center', va='center')
            ax.set_title(metric_name)
            return

        x_data = np.array(data)
        mu = np.mean(x_data)
        sigma = np.std(x_data)
        
        # Plot Histogram
        ax.hist(x_data, bins='auto', density=True, alpha=0.4, color=color, edgecolor='black', label='Freq')

        # Plot Bell Curve
        xmin, xmax = ax.get_xlim()
        # Extend range if ref_val is outside current view
        if ref_val is not None:
            xmin = min(xmin, ref_val - 2)
            xmax = max(xmax, ref_val + 2)
            
        x = np.linspace(xmin, xmax, 100)
        p = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma)**2)
        ax.plot(x, p, 'k', linewidth=2, label=f'$\\mu={mu:.1f}$')

        # Determine Height for lines
        line_height = max(p) * 1.1

        # --- Standard Deviation Lines ---
        ax.vlines(mu, 0, line_height, color='black', linestyle='dashed', alpha=0.5)
        for s in [-2, -1, 1, 2]:
            ax.vlines(mu + (s * sigma), 0, line_height, color='gray', linestyle=':', alpha=0.5)

        # --- Reference Value (Median/Cutoff) ---
        if ref_val is not None:
            # 1. Draw the reference line
            ax.vlines(ref_val, 0, line_height, color='magenta', linestyle='-', linewidth=2, label=f'Ref: {ref_val}')
            
            # 2. Calculate Percentages (Empirical)
            pct_below = np.mean(x_data < ref_val) * 100
            pct_above = np.mean(x_data > ref_val) * 100
            
            # 3. Add Labels to chart
            # Position text slightly left/right of the magenta line
            ax.text(ref_val, line_height * 0.9, f" Below\n {pct_below:.1f}% ", 
                    ha='right', va='top', color='magenta', fontweight='bold', fontsize=9)
            ax.text(ref_val, line_height * 0.9, f" Above\n {pct_above:.1f}% ", 
                    ha='left', va='top', color='magenta', fontweight='bold', fontsize=9)

        ax.set_title(f"{metric_name}")
        ax.legend(loc='upper right', fontsize='x-small')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, line_height * 1.15)

if __name__ == "__main__":
    root = tk.Tk()
    app = GoalieApp(root)
    root.mainloop()
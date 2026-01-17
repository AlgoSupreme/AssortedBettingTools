import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HockeyAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NHL Goal Probability Analyzer")
        self.root.geometry("1400x800")

        # Data storage
        self.raw_data = {}
        self.teams_list = []

        # --- GUI Layout ---
        
        # 1. Top Control Panel
        control_frame = tk.Frame(root, pady=10, padx=10, bg="#f0f0f0")
        control_frame.pack(fill="x")

        # Load Button
        self.btn_load = tk.Button(control_frame, text="Load JSON File", command=self.load_file, bg="#ddd")
        self.btn_load.pack(side="left", padx=10)

        # Team Selector Label
        tk.Label(control_frame, text="Select Team:", bg="#f0f0f0").pack(side="left", padx=5)

        # Team Dropdown
        self.team_var = tk.StringVar()
        self.team_combo = ttk.Combobox(control_frame, textvariable=self.team_var, state="disabled")
        self.team_combo.pack(side="left", padx=5)
        self.team_combo.bind("<<ComboboxSelected>>", self.on_team_select)

        # 2. Visualization Area (Matplotlib Canvas)
        self.plot_frame = tk.Frame(root, bg="white")
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize empty figures - 1 row, 3 columns
        self.fig, self.axs = plt.subplots(1, 3, figsize=(15, 5)) 
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Attempt to auto-load if file exists locally
        self.auto_load_default()

    def auto_load_default(self):
        """Tries to load the specific file uploaded by the user automatically."""
        default_file = "team_analysis_goalBreakdown2026-01-15.json"
        try:
            with open(default_file, 'r', encoding='utf-8') as f:
                self.process_json(json.load(f))
                print(f"Auto-loaded {default_file}")
        except FileNotFoundError:
            pass # Fail silently, user can use the button

    def load_file(self):
        """Opens file dialog to load JSON."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.process_json(data)
        except Exception as e:
            messagebox.showerror("Error", f"Could not parse file:\n{e}")

    def process_json(self, data):
        """Parses the JSON and populates the dropdown."""
        self.raw_data = data
        self.teams_list = sorted(list(data.keys()))
        
        # Update Dropdown
        self.team_combo['values'] = self.teams_list
        self.team_combo['state'] = "readonly"
        
        if self.teams_list:
            self.team_combo.current(0)
            self.on_team_select(None)

    def on_team_select(self, event):
        """Triggered when a team is selected. Calculations happen here."""
        team = self.team_var.get()
        if not team or team not in self.raw_data:
            return

        # 1. Extract List of Games
        team_data = self.raw_data[team].get("date-data", [])
        if not team_data:
            messagebox.showinfo("Info", f"No game data found for {team}")
            return

        # 2. Create DataFrame
        df = pd.DataFrame(team_data)

        # 3. Calculate Matrices/Distributions
        
        # --- Chart 1 Data: Period 1 "Over X.5" Probabilities ---
        # Find max goals to determine how many thresholds to create
        max_p1 = df['period1Goals'].max()
        if pd.isna(max_p1): max_p1 = 0
        
        # Create thresholds: 0.5, 1.5, 2.5 ... up to max
        thresholds = [x + 0.5 for x in range(int(max_p1) + 1)]
        
        # Calculate percentage of games where goals > threshold
        over_probs_list = []
        for t in thresholds:
            prob = (df['period1Goals'] > t).mean() * 100
            over_probs_list.append(prob)
            
        p1_probs = pd.Series(over_probs_list, index=thresholds)

        # --- Chart 2 Data: Matrix P1 -> P2 ---
        p1_p2 = pd.crosstab(
            index=df['period1Goals'], 
            columns=df['period2Goals'], 
            normalize='index'
        ) * 100

        # --- Chart 3 Data: Matrix (P1+P2) -> P3 ---
        df['goals_entering_3rd'] = df['period1Goals'] + df['period2Goals']
        p1p2_p3 = pd.crosstab(
            index=df['goals_entering_3rd'], 
            columns=df['period3Goals'], 
            normalize='index'
        ) * 100

        # 4. Draw Charts
        self.draw_charts(team, p1_probs, p1_p2, p1p2_p3)

    def draw_charts(self, team_name, p1_probs, matrix1, matrix2):
        """Renders the plots onto the Tkinter canvas."""
        # Clear previous plots
        self.axs[0].clear()
        self.axs[1].clear()
        self.axs[2].clear()

        # --- Chart 1: Period 1 Over X.5 Probability (Bar Chart) ---
        sns.barplot(x=p1_probs.index, y=p1_probs.values, ax=self.axs[0], color="skyblue")
        self.axs[0].set_title(f"{team_name}: Probability > X Goals (Period 1)")
        self.axs[0].set_ylabel("Probability (%)")
        self.axs[0].set_xlabel("Goal Threshold")
        
        # Add text labels on top of bars
        for i, v in enumerate(p1_probs.values):
            self.axs[0].text(i, v + 1, f"{v:.1f}%", ha='center', color='black', fontsize=9)

        # --- Chart 2: P1 -> P2 (Heatmap) ---
        sns.heatmap(matrix1, annot=True, fmt=".0f", cmap="Blues", ax=self.axs[1], cbar=False)
        self.axs[1].set_title(f"P1 Goals vs P2 Goals (%)")
        self.axs[1].set_ylabel("Goals Scored in Period 1")
        self.axs[1].set_xlabel("Goals Scored in Period 2")

        # --- Chart 3: Total -> P3 (Heatmap) ---
        sns.heatmap(matrix2, annot=True, fmt=".0f", cmap="Greens", ax=self.axs[2], cbar=False)
        self.axs[2].set_title(f"Entering 3rd vs P3 Goals (%)")
        self.axs[2].set_ylabel("Total Goals (P1 + P2)")
        self.axs[2].set_xlabel("Goals Scored in Period 3")

        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = HockeyAnalyzerApp(root)
    root.mainloop()
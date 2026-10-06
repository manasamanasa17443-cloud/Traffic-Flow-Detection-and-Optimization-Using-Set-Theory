import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import time

class TrafficSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("🚦 SMART TRAFFIC CONTROL SYSTEM")
        self.root.geometry("1300x750")
        self.root.configure(bg="#0a0e1a")
        self.root.resizable(False, False)
        
        # Traffic data
        self.traffic = {"North": 0, "South": 0, "East": 0, "West": 0}
        self.waiting = {"North": 0, "South": 0, "East": 0, "West": 0}
        self.processed = {"North": 0, "South": 0, "East": 0, "West": 0}
        self.signal_times = {"North": 20, "South": 20, "East": 20, "West": 20}
        self.current_signal = None
        self.signal_state = "RED"
        self.time_remaining = 0
        self.simulation_running = False
        self.paused = False
        self.score = 100
        self.total_processed = 0
        self.total_vehicles = 0
        self.efficiency = 0
        self.congestion_level = "LOW"
        self.game_status = "Excellent"
        self.cycle_count = 0
        self.timer_counter = 0
        self.spawn_counter = 0
        self.max_vehicles_per_road = 15
        self.yellow_phase = False
        
        # Set theory data
        self.low_set = set()
        self.medium_set = set()
        self.high_set = set()
        self.universal_set = {"North", "South", "East", "West"}
        
        # Road order
        self.road_order = ["North", "South", "East", "West"]
        self.current_road_index = 0
        
        # Vehicle objects
        self.vehicle_objects = []
        self.vehicle_data = []
        self.animation_id = None
        self.road_width = 140
        self.road_start = 0
        
        # Vehicle colors
        self.car_colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", 
                          "#1abc9c", "#e67e22", "#2980b9", "#c0392b", "#27ae60"]
        
        # Setup UI
        self.setup_ui()
        self.create_intersection()
        self.update_statistics()
        self.update_set_display()
        
        # Create initial vehicles
        self.get_input_data()
        self.create_traffic_sets()
        
    def setup_ui(self):
        # Main container
        main_container = tk.Frame(self.root, bg="#0a0e1a")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Top header
        header_frame = tk.Frame(main_container, bg="#0f1a2e", height=45, relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(3, 6), padx=8)
        header_frame.pack_propagate(False)
        
        header_canvas = tk.Canvas(header_frame, height=45, bg="#0f1a2e", highlightthickness=0)
        header_canvas.pack(fill=tk.BOTH, expand=True)
        
        for i in range(45):
            color = f"#{int(15 + i*0.5):02x}{int(26 + i*0.5):02x}{int(46 + i*0.7):02x}"
            header_canvas.create_rectangle(0, i, 1300, i+2, fill=color, outline="")
        
        header_canvas.create_text(650, 15, text="🚦 SMART TRAFFIC CONTROL SYSTEM", 
                                  font=("Arial", 15, "bold"), fill="#4fc3f7")
        header_canvas.create_text(650, 32, text="Traffic Flow Detection and Optimization Using Set Theory", 
                                  font=("Arial", 8), fill="#8899aa")
        
        # Content area
        content_frame = tk.Frame(main_container, bg="#0a0e1a")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        # LEFT PANEL43
        left_panel = tk.Frame(content_frame, bg="#111927", width=200, relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left_panel.pack_propagate(False)
        
        panel_title = tk.Frame(left_panel, bg="#1a2744", height=24)
        panel_title.pack(fill=tk.X, padx=2, pady=2)
        panel_title.pack_propagate(False)
        tk.Label(panel_title, text="📊 TRAFFIC INPUT", font=("Arial", 8, "bold"),
                fg="#4fc3f7", bg="#1a2744").pack(pady=3)
        
        input_container = tk.Frame(left_panel, bg="#111927")
        input_container.pack(pady=4, padx=6, fill=tk.X)
        
        self.entries = {}
        roads = ["North", "South", "East", "West"]
        default_values = [25, 40, 15, 60]
        icons = ["⬆️", "⬇️", "➡️", "⬅️"]
        
        for i, road in enumerate(roads):
            frame = tk.Frame(input_container, bg="#111927")
            frame.pack(fill=tk.X, pady=1)
            
            label_frame = tk.Frame(frame, bg="#1a2744", width=55, height=20, relief=tk.FLAT)
            label_frame.pack(side=tk.LEFT, padx=(0, 3))
            label_frame.pack_propagate(False)
            tk.Label(label_frame, text=f"{icons[i]} {road}", font=("Arial", 7, "bold"),
                    fg="#aabbcc", bg="#1a2744").pack(pady=2)
            
            entry_frame = tk.Frame(frame, bg="#0a0e1a", relief=tk.RAISED, bd=1)
            entry_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            entry = tk.Entry(entry_frame, width=5, font=("Arial", 8, "bold"), 
                           bg="#0d1b2a", fg="#4fc3f7", insertbackground="#4fc3f7",
                           relief=tk.FLAT, justify=tk.CENTER)
            entry.insert(0, str(default_values[i]))
            entry.pack(padx=2, pady=2, fill=tk.X)
            self.entries[road] = entry
        
        btn_container = tk.Frame(left_panel, bg="#111927")
        btn_container.pack(pady=4, padx=6, fill=tk.X)
        
        self.start_btn = tk.Button(btn_container, text="▶ START", 
                                  font=("Arial", 7, "bold"), bg="#4fc3f7", 
                                  fg="#0d1b2a", command=self.start_simulation,
                                  relief=tk.RAISED, bd=2, cursor="hand2")
        self.start_btn.pack(fill=tk.X, pady=1)
        
        self.pause_btn = tk.Button(btn_container, text="⏸ PAUSE", 
                                  font=("Arial", 7, "bold"), bg="#ffa726", 
                                  fg="#0d1b2a", command=self.toggle_pause,
                                  relief=tk.RAISED, bd=2, cursor="hand2")
        self.pause_btn.pack(fill=tk.X, pady=1)
        
        self.reset_btn = tk.Button(btn_container, text="🔄 RESET", 
                                  font=("Arial", 7, "bold"), bg="#ef5350", 
                                  fg="white", command=self.reset_simulation,
                                  relief=tk.RAISED, bd=2, cursor="hand2")
        self.reset_btn.pack(fill=tk.X, pady=1)
        
        self.new_traffic_btn = tk.Button(btn_container, text="🎲 NEW", 
                                        font=("Arial", 7, "bold"), bg="#66bb6a", 
                                        fg="#0d1b2a", command=self.generate_new_traffic,
                                        relief=tk.RAISED, bd=2, cursor="hand2")
        self.new_traffic_btn.pack(fill=tk.X, pady=1)
        
        self.report_btn = tk.Button(btn_container, text="📄 REPORT", 
                                   font=("Arial", 7, "bold"), bg="#ab47bc", 
                                   fg="white", command=self.generate_report,
                                   relief=tk.RAISED, bd=2, cursor="hand2")
        self.report_btn.pack(fill=tk.X, pady=1)
        
        set_frame = tk.LabelFrame(left_panel, text="📐 SET THEORY", 
                                 font=("Arial", 7, "bold"), 
                                 bg="#111927", fg="#4fc3f7", relief=tk.RIDGE, bd=2)
        set_frame.pack(pady=4, padx=6, fill=tk.X)
        
        self.set_text = tk.Text(set_frame, height=5, width=16, bg="#0d1b2a", 
                               fg="#aabbcc", font=("Courier", 7), wrap=tk.WORD,
                               relief=tk.FLAT)
        self.set_text.pack(padx=2, pady=2)
        self.set_text.config(state=tk.DISABLED)
        
        # CENTER - Canvas (smaller)
        canvas_container = tk.Frame(content_frame, bg="#0a0e1a", relief=tk.RAISED, bd=3)
        canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        
        self.canvas = tk.Canvas(canvas_container, width=680, height=680, 
                               bg="#0d1b2a", highlightthickness=0)
        self.canvas.pack(pady=6, padx=6)
        
        # RIGHT PANEL (smaller)
        right_panel = tk.Frame(content_frame, bg="#111927", width=250, relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        right_panel.pack_propagate(False)
        
        stats_title = tk.Frame(right_panel, bg="#1a2744", height=24)
        stats_title.pack(fill=tk.X, padx=2, pady=2)
        stats_title.pack_propagate(False)
        tk.Label(stats_title, text="📈 LIVE STATISTICS", font=("Arial", 8, "bold"),
                fg="#4fc3f7", bg="#1a2744").pack(pady=3)
        
        stats_container = tk.Frame(right_panel, bg="#0d1b2a", relief=tk.RIDGE, bd=2)
        stats_container.pack(padx=5, pady=3, fill=tk.BOTH, expand=True)
        
        self.stats_text = tk.Text(stats_container, height=10, width=24, bg="#0d1b2a", 
                                 fg="#aabbcc", font=("Courier", 7), wrap=tk.WORD,
                                 relief=tk.FLAT)
        self.stats_text.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        
        opt_title = tk.Frame(right_panel, bg="#1a2744", height=24)
        opt_title.pack(fill=tk.X, padx=2, pady=(4, 2))
        opt_title.pack_propagate(False)
        tk.Label(opt_title, text="🎯 OPTIMIZATION", font=("Arial", 8, "bold"),
                fg="#ffa726", bg="#1a2744").pack(pady=3)
        
        self.opt_frame = tk.Frame(right_panel, bg="#0d1b2a", relief=tk.RIDGE, bd=2)
        self.opt_frame.pack(padx=5, pady=3, fill=tk.X)
        
        self.opt_text = tk.Text(self.opt_frame, height=4, width=24, bg="#0d1b2a", 
                               fg="#aabbcc", font=("Arial", 7), wrap=tk.WORD,
                               relief=tk.FLAT)
        self.opt_text.pack(padx=2, pady=2)
        
        score_frame = tk.Frame(right_panel, bg="#111927", relief=tk.RIDGE, bd=2)
        score_frame.pack(pady=4, padx=5, fill=tk.X)
        
        tk.Label(score_frame, text="🏆 SCORE", 
                font=("Arial", 7, "bold"), fg="#4fc3f7", bg="#111927").pack(pady=2)
        
        score_inner = tk.Frame(score_frame, bg="#0d1b2a")
        score_inner.pack(pady=2, padx=5, fill=tk.X)
        
        self.score_label = tk.Label(score_inner, text="100 / 100", 
                                   font=("Arial", 11, "bold"), fg="#4fc3f7", bg="#0d1b2a")
        self.score_label.pack()
        
        self.status_label = tk.Label(score_inner, text="✅ Excellent", 
                                    font=("Arial", 8, "bold"), fg="#66bb6a", bg="#0d1b2a")
        self.status_label.pack(pady=1)
        
        self.score_bar = tk.Canvas(score_frame, height=4, bg="#0d1b2a", highlightthickness=0)
        self.score_bar.pack(fill=tk.X, padx=5, pady=2)
        self.score_bar.create_rectangle(0, 0, 0, 4, fill="#4fc3f7", tags="bar")
    
    def create_intersection(self):
        c = self.canvas
        c.delete("all")
        
        # Background
        for i in range(680):
            color = f"#{int(13 + i*0.007):02x}{int(27 + i*0.01):02x}{int(42 + i*0.012):02x}"
            c.create_rectangle(0, i, 680, i+2, fill=color, outline="")
        
        # Road dimensions
        self.road_width = 130
        self.road_start = (680 - self.road_width) // 2
        lane_center = self.road_start + self.road_width // 2
        
        # Vertical road
        c.create_rectangle(self.road_start, 0, self.road_start + self.road_width, 275, 
                          fill="#2c3e50", outline="#3d566e", width=2)
        c.create_rectangle(self.road_start, 405, self.road_start + self.road_width, 680, 
                          fill="#2c3e50", outline="#3d566e", width=2)
        
        # Horizontal road
        c.create_rectangle(0, self.road_start, 275, self.road_start + self.road_width, 
                          fill="#2c3e50", outline="#3d566e", width=2)
        c.create_rectangle(405, self.road_start, 680, self.road_start + self.road_width, 
                          fill="#2c3e50", outline="#3d566e", width=2)
        
        # Road edge lines
        c.create_line(self.road_start, 0, self.road_start, 275, fill="#7f8c8d", width=1)
        c.create_line(self.road_start + self.road_width, 0, self.road_start + self.road_width, 275, fill="#7f8c8d", width=1)
        c.create_line(self.road_start, 405, self.road_start, 680, fill="#7f8c8d", width=1)
        c.create_line(self.road_start + self.road_width, 405, self.road_start + self.road_width, 680, fill="#7f8c8d", width=1)
        c.create_line(0, self.road_start, 275, self.road_start, fill="#7f8c8d", width=1)
        c.create_line(0, self.road_start + self.road_width, 275, self.road_start + self.road_width, fill="#7f8c8d", width=1)
        c.create_line(405, self.road_start, 680, self.road_start, fill="#7f8c8d", width=1)
        c.create_line(405, self.road_start + self.road_width, 680, self.road_start + self.road_width, fill="#7f8c8d", width=1)
        
        # Lane dividers
        for i in range(0, 275, 25):
            c.create_line(lane_center, i, lane_center, i+15, fill="#ecf0f1", width=1, dash=(4,4))
            c.create_line(lane_center, i+405, lane_center, i+420, fill="#ecf0f1", width=1, dash=(4,4))
        
        for i in range(0, 275, 25):
            c.create_line(i, lane_center, i+15, lane_center, fill="#ecf0f1", width=1, dash=(4,4))
            c.create_line(i+405, lane_center, i+420, lane_center, fill="#ecf0f1", width=1, dash=(4,4))
        
        # Left and right lane markings
        left_lane = self.road_start + 25
        right_lane = self.road_start + self.road_width - 25
        
        # Vertical lane markings (for incoming and outgoing)
        for i in range(0, 275, 35):
            c.create_line(left_lane, i, left_lane, i+12, fill="#bdc3c7", width=1, dash=(2,4))
            c.create_line(right_lane, i, right_lane, i+12, fill="#bdc3c7", width=1, dash=(2,4))
            c.create_line(left_lane, i+405, left_lane, i+417, fill="#bdc3c7", width=1, dash=(2,4))
            c.create_line(right_lane, i+405, right_lane, i+417, fill="#bdc3c7", width=1, dash=(2,4))
        
        # Horizontal lane markings
        for i in range(0, 275, 35):
            c.create_line(i, left_lane, i+12, left_lane, fill="#bdc3c7", width=1, dash=(2,4))
            c.create_line(i, right_lane, i+12, right_lane, fill="#bdc3c7", width=1, dash=(2,4))
            c.create_line(i+405, left_lane, i+417, left_lane, fill="#bdc3c7", width=1, dash=(2,4))
            c.create_line(i+405, right_lane, i+417, right_lane, fill="#bdc3c7", width=1, dash=(2,4))
        
        # Intersection
        c.create_rectangle(self.road_start, self.road_start, 
                          self.road_start + self.road_width, self.road_start + self.road_width, 
                          fill="#34495e", outline="#5d7a9a", width=2)
        c.create_rectangle(self.road_start + 4, self.road_start + 4, 
                          self.road_start + self.road_width - 4, self.road_start + self.road_width - 4, 
                          fill="#2c3e50", outline="")
        
        # Intersection center
        c.create_oval(lane_center-6, lane_center-6, lane_center+6, lane_center+6, 
                     fill="#4a6a8a", outline="#6a8aaa", width=1)
        c.create_line(lane_center-15, lane_center, lane_center+15, lane_center, fill="#4a6a8a", width=1)
        c.create_line(lane_center, lane_center-15, lane_center, lane_center+15, fill="#4a6a8a", width=1)
        
        # Direction labels
        labels = [
            ("⬆ NORTH", lane_center, 18, "#4fc3f7"),
            ("⬇ SOUTH", lane_center, 665, "#4fc3f7"),
            ("⬅ WEST", 18, lane_center, "#4fc3f7"),
            ("➡ EAST", 665, lane_center, "#4fc3f7")
        ]
        for text, x, y, color in labels:
            c.create_text(x, y, text=text, fill=color, font=("Arial", 8, "bold"))
        
        # Zebra crossings
        for i in range(5):
            # North
            c.create_rectangle(self.road_start-6, 175+i*7, self.road_start-1, 179+i*7, fill="#ecf0f1", outline="")
            c.create_rectangle(self.road_start+self.road_width+1, 175+i*7, 
                              self.road_start+self.road_width+6, 179+i*7, fill="#ecf0f1", outline="")
            # South
            c.create_rectangle(self.road_start-6, 500+i*7, self.road_start-1, 504+i*7, fill="#ecf0f1", outline="")
            c.create_rectangle(self.road_start+self.road_width+1, 500+i*7, 
                              self.road_start+self.road_width+6, 504+i*7, fill="#ecf0f1", outline="")
            # East
            c.create_rectangle(175+i*7, self.road_start-6, 179+i*7, self.road_start-1, fill="#ecf0f1", outline="")
            c.create_rectangle(175+i*7, self.road_start+self.road_width+1, 
                              179+i*7, self.road_start+self.road_width+6, fill="#ecf0f1", outline="")
            # West
            c.create_rectangle(500+i*7, self.road_start-6, 504+i*7, self.road_start-1, fill="#ecf0f1", outline="")
            c.create_rectangle(500+i*7, self.road_start+self.road_width+1, 
                              504+i*7, self.road_start+self.road_width+6, fill="#ecf0f1", outline="")
        
        # Traffic signals with timers
        self.signal_lights = {}
        self.signal_timer_labels = {}
        
        signal_positions = {
            "North": {"x": lane_center, "y": 110, "orient": "v"},
            "South": {"x": lane_center, "y": 575, "orient": "v"},
            "East": {"x": 575, "y": lane_center, "orient": "h"},
            "West": {"x": 110, "y": lane_center, "orient": "h"}
        }
        
        for road, pos in signal_positions.items():
            x, y = pos["x"], pos["y"]
            lights = {}
            
            # Signal pole
            c.create_rectangle(x-2, y-35, x+2, y+35, fill="#5d6d7e", outline="#7d8d9e", width=1)
            
            if pos["orient"] == "v":
                hx, hy = x + 35, y
                c.create_rectangle(hx-14, hy-30, hx+14, hy+30, fill="#1a1a2e", outline="#4a5a6a", width=2)
                lights["red"] = c.create_oval(hx-7, hy-20, hx+7, hy-7, fill="#333", outline="#555")
                lights["yellow"] = c.create_oval(hx-7, hy-5, hx+7, hy+7, fill="#333", outline="#555")
                lights["green"] = c.create_oval(hx-7, hy+9, hx+7, hy+22, fill="#333", outline="#555")
                timer = c.create_text(hx, hy+42, text="0s", fill="#f44336", font=("Arial", 9, "bold"))
            else:
                hx, hy = x, y + 35
                c.create_rectangle(hx-30, hy-14, hx+30, hy+14, fill="#1a1a2e", outline="#4a5a6a", width=2)
                lights["red"] = c.create_oval(hx-20, hy-7, hx-7, hy+7, fill="#333", outline="#555")
                lights["yellow"] = c.create_oval(hx-5, hy-7, hx+7, hy+7, fill="#333", outline="#555")
                lights["green"] = c.create_oval(hx+9, hy-7, hx+22, hy+7, fill="#333", outline="#555")
                timer = c.create_text(hx, hy+26, text="0s", fill="#f44336", font=("Arial", 9, "bold"))
            
            self.signal_lights[road] = lights
            self.signal_timer_labels[road] = timer
        
        # Store road positions - ONE LANE INCOMING, ONE LANE OUTGOING
        self.road_positions = {
            "North": {
                "start": (lane_center - 15, 620), 
                "end": (lane_center - 15, 320), 
                "direction": (0, -1)
            },
            "South": {
                "start": (lane_center + 15, 60), 
                "end": (lane_center + 15, 360), 
                "direction": (0, 1)
            },
            "East": {
                "start": (60, lane_center - 15), 
                "end": (360, lane_center - 15), 
                "direction": (1, 0)
            },
            "West": {
                "start": (620, lane_center + 15), 
                "end": (320, lane_center + 15), 
                "direction": (-1, 0)
            }
        }
        
        # Initialize all signals to RED
        for road in self.signal_lights:
            lights = self.signal_lights[road]
            c.itemconfig(lights["red"], fill="#f44336", outline="#ef5350")
            c.itemconfig(lights["yellow"], fill="#333", outline="#555")
            c.itemconfig(lights["green"], fill="#333", outline="#555")
            c.itemconfig(self.signal_timer_labels[road], text="0s", fill="#f44336")
        
        # Road labels
        c.create_text(self.road_start-15, lane_center, text="LANE", fill="#667788", font=("Arial", 6))
        c.create_text(self.road_start+self.road_width+15, lane_center, text="LANE", fill="#667788", font=("Arial", 6))
    
    def create_vehicle(self, x, y, road, progress=0):
        c = self.canvas
        color = random.choice(self.car_colors)
        
        # Random vehicle type
        vehicle_type = random.choice(["car", "car", "car", "truck", "bike"])
        
        if vehicle_type == "bike":
            width, height = 8, 5
            body = c.create_oval(x-width, y-height, x+width, y+height, fill=color, outline="#222", width=1)
            hl = c.create_oval(x+width-1, y-1, x+width+2, y+1, fill="#ffeb3b", outline="")
            w1 = c.create_oval(x-5, y-3, x-2, y-1, fill="#111", outline="#444")
            w2 = c.create_oval(x+2, y-3, x+5, y-1, fill="#111", outline="#444")
            w3 = c.create_oval(x-5, y+1, x-2, y+3, fill="#111", outline="#444")
            w4 = c.create_oval(x+2, y+1, x+5, y+3, fill="#111", outline="#444")
            objects = [body, hl, w1, w2, w3, w4]
            
        elif vehicle_type == "truck":
            width, height = 16, 10
            body = c.create_rectangle(x-width, y-height, x+width, y+height, fill=color, outline="#222", width=1)
            cargo = c.create_rectangle(x-width+2, y-height-2, x+width-2, y+2, fill="#34495e", outline="#222")
            if road in ["North", "South"]:
                cab = c.create_rectangle(x-4, y+2, x+4, y+height, fill="#2c3e50", outline="#222")
            else:
                cab = c.create_rectangle(x+2, y-4, x+width, y+4, fill="#2c3e50", outline="#222")
            hl1 = c.create_oval(x+width-2, y-3, x+width+1, y, fill="#ffeb3b", outline="")
            hl2 = c.create_oval(x+width-2, y+1, x+width+1, y+4, fill="#ffeb3b", outline="")
            w1 = c.create_oval(x-width+2, y-height+1, x-width+5, y-height+4, fill="#111", outline="#444")
            w2 = c.create_oval(x+width-5, y-height+1, x+width-2, y-height+4, fill="#111", outline="#444")
            w3 = c.create_oval(x-width+2, y+height-4, x-width+5, y+height-1, fill="#111", outline="#444")
            w4 = c.create_oval(x+width-5, y+height-4, x+width-2, y+height-1, fill="#111", outline="#444")
            objects = [body, cargo, cab, hl1, hl2, w1, w2, w3, w4]
            
        else:  # Car
            width, height = 12, 7
            body = c.create_rectangle(x-width, y-height, x+width, y+height, fill=color, outline="#222", width=1)
            if road in ["North", "South"]:
                ws1 = c.create_rectangle(x-5, y-height+1, x-2, y+height-1, fill="#333", outline="")
                ws2 = c.create_rectangle(x+2, y-height+1, x+5, y+height-1, fill="#333", outline="")
            else:
                ws1 = c.create_rectangle(x-width+1, y-5, x+width-1, y-2, fill="#333", outline="")
                ws2 = c.create_rectangle(x-width+1, y+2, x+width-1, y+5, fill="#333", outline="")
            
            if road == "North":
                hl1 = c.create_oval(x-4, y-height-1, x-1, y-height+1, fill="#ffeb3b", outline="")
                hl2 = c.create_oval(x+1, y-height-1, x+4, y-height+1, fill="#ffeb3b", outline="")
            elif road == "South":
                hl1 = c.create_oval(x-4, y+height-1, x-1, y+height+1, fill="#ffeb3b", outline="")
                hl2 = c.create_oval(x+1, y+height-1, x+4, y+height+1, fill="#ffeb3b", outline="")
            elif road == "East":
                hl1 = c.create_oval(x+width-1, y-4, x+width+1, y-1, fill="#ffeb3b", outline="")
                hl2 = c.create_oval(x+width-1, y+1, x+width+1, y+4, fill="#ffeb3b", outline="")
            else:
                hl1 = c.create_oval(x-width-1, y-4, x-width+1, y-1, fill="#ffeb3b", outline="")
                hl2 = c.create_oval(x-width-1, y+1, x-width+1, y+4, fill="#ffeb3b", outline="")
            
            w1 = c.create_oval(x-7, y-5, x-4, y-2, fill="#111", outline="#444")
            w2 = c.create_oval(x+4, y-5, x+7, y-2, fill="#111", outline="#444")
            w3 = c.create_oval(x-7, y+2, x-4, y+5, fill="#111", outline="#444")
            w4 = c.create_oval(x+4, y+2, x+7, y+5, fill="#111", outline="#444")
            objects = [body, ws1, ws2, hl1, hl2, w1, w2, w3, w4]
        
        # Speed based on type
        speed = 0.6 + random.random() * 0.4
        if vehicle_type == "bike":
            speed = 1.0 + random.random() * 0.3
        elif vehicle_type == "truck":
            speed = 0.3 + random.random() * 0.2
        
        self.vehicle_data.append({
            "road": road,
            "objects": objects,
            "x": x,
            "y": y,
            "progress": progress,
            "speed": speed * 0.015,
            "active": True,
            "type": vehicle_type,
            "size": (width, height)
        })
        self.vehicle_objects.extend(objects)
    
    def count_vehicles_on_road(self, road):
        count = 0
        for v in self.vehicle_data:
            if v["road"] == road and v["active"]:
                count += 1
        return count
    
    def spawn_vehicles_continuously(self):
        if not self.simulation_running or self.paused:
            return
        
        for road in self.road_order:
            current_count = self.count_vehicles_on_road(road)
            max_allowed = min(self.traffic.get(road, 15), self.max_vehicles_per_road)
            
            if current_count < max_allowed and current_count < self.traffic.get(road, 15):
                positions = self.road_positions[road]
                start_x, start_y = positions["start"]
                dx, dy = positions["direction"]
                
                # Spawn at start position with slight random offset
                if road in ["North", "South"]:
                    x = start_x + random.randint(-3, 3)
                    y = start_y
                    # Check if position is clear
                    occupied = False
                    for v in self.vehicle_data:
                        if v["road"] == road and abs(v["y"] - y) < 25:
                            occupied = True
                            break
                    if not occupied:
                        self.create_vehicle(x, y, road, 0)
                else:
                    x = start_x
                    y = start_y + random.randint(-3, 3)
                    occupied = False
                    for v in self.vehicle_data:
                        if v["road"] == road and abs(v["x"] - x) < 25:
                            occupied = True
                            break
                    if not occupied:
                        self.create_vehicle(x, y, road, 0)
    
    def get_input_data(self):
        try:
            for road, entry in self.entries.items():
                value = entry.get().strip()
                if value == "":
                    raise ValueError("Empty input")
                num = int(value)
                if num < 0:
                    raise ValueError("Negative value")
                if num > 80:
                    num = 80
                    entry.delete(0, tk.END)
                    entry.insert(0, str(num))
                self.traffic[road] = num
                self.waiting[road] = num
                self.processed[road] = 0
            return True
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid non-negative vehicle counts (0-80).")
            return False
    
    def create_traffic_sets(self):
        self.low_set = set()
        self.medium_set = set()
        self.high_set = set()
        
        for road, count in self.traffic.items():
            if count < 20:
                self.low_set.add(road)
            elif 20 <= count <= 50:
                self.medium_set.add(road)
            else:
                self.high_set.add(road)
        
        self.update_set_display()
    
    def calculate_signal_time(self, count):
        if count < 20:
            return 10
        elif 20 <= count <= 50:
            return 20
        else:
            return 30
    
    def find_priority_road(self):
        if not self.traffic or all(v == 0 for v in self.traffic.values()):
            return ["None"]
        max_count = max(self.traffic.values())
        priority_roads = [road for road, count in self.traffic.items() if count == max_count]
        return priority_roads if priority_roads else ["None"]
    
    def start_simulation(self):
        if self.simulation_running:
            return
        
        if not self.get_input_data():
            return
        
        # Clear existing vehicles
        for obj in self.vehicle_objects:
            self.canvas.delete(obj)
        self.vehicle_objects = []
        self.vehicle_data = []
        
        self.total_vehicles = sum(self.traffic.values())
        self.total_processed = 0
        self.score = 100
        self.simulation_running = True
        self.paused = False
        self.pause_btn.config(text="⏸ PAUSE")
        self.cycle_count = 0
        self.timer_counter = 0
        self.spawn_counter = 0
        self.yellow_phase = False
        
        # Calculate signal times
        for road in self.traffic:
            self.signal_times[road] = self.calculate_signal_time(self.traffic[road])
        
        self.create_traffic_sets()
        
        sorted_roads = sorted(self.traffic.items(), key=lambda x: x[1], reverse=True)
        self.road_order = [road for road, _ in sorted_roads if self.traffic[road] > 0]
        if not self.road_order:
            self.road_order = ["North", "South", "East", "West"]
        self.current_road_index = 0
        
        self.current_signal = self.road_order[0]
        self.signal_state = "GREEN"
        self.time_remaining = self.signal_times[self.current_signal]
        
        self.update_all_signals()
        self.update_simulation()
        self.update_statistics()
        self.update_optimization()
        self.update_score()
    
    def update_all_signals(self):
        for road, lights in self.signal_lights.items():
            if road == self.current_signal:
                if self.signal_state == "GREEN":
                    self.canvas.itemconfig(lights["red"], fill="#333", outline="#555")
                    self.canvas.itemconfig(lights["yellow"], fill="#333", outline="#555")
                    self.canvas.itemconfig(lights["green"], fill="#4caf50", outline="#66bb6a")
                    self.canvas.itemconfig(self.signal_timer_labels[road], 
                                         text=f"{self.time_remaining}s", fill="#4caf50")
                elif self.signal_state == "YELLOW":
                    self.canvas.itemconfig(lights["red"], fill="#333", outline="#555")
                    self.canvas.itemconfig(lights["yellow"], fill="#ffeb3b", outline="#ffd600")
                    self.canvas.itemconfig(lights["green"], fill="#333", outline="#555")
                    self.canvas.itemconfig(self.signal_timer_labels[road], 
                                         text=f"{self.time_remaining}s", fill="#ffeb3b")
                else:
                    self.canvas.itemconfig(lights["red"], fill="#f44336", outline="#ef5350")
                    self.canvas.itemconfig(lights["yellow"], fill="#333", outline="#555")
                    self.canvas.itemconfig(lights["green"], fill="#333", outline="#555")
                    self.canvas.itemconfig(self.signal_timer_labels[road], 
                                         text="0s", fill="#f44336")
            else:
                self.canvas.itemconfig(lights["red"], fill="#f44336", outline="#ef5350")
                self.canvas.itemconfig(lights["yellow"], fill="#333", outline="#555")
                self.canvas.itemconfig(lights["green"], fill="#333", outline="#555")
                if self.simulation_running and road in self.signal_times:
                    wait_time = self.signal_times[road]
                    self.canvas.itemconfig(self.signal_timer_labels[road], 
                                         text=f"{wait_time}s", fill="#f44336")
    
    def update_simulation(self):
        if not self.simulation_running or self.paused:
            self.animation_id = self.root.after(100, self.update_simulation)
            return
        
        # Update countdown
        self.timer_counter += 1
        if self.timer_counter >= 10:
            self.timer_counter = 0
            self.time_remaining -= 1
        
        # Update timer display
        if self.current_signal:
            if self.signal_state == "GREEN":
                self.canvas.itemconfig(self.signal_timer_labels[self.current_signal], 
                                     text=f"{self.time_remaining}s", fill="#4caf50")
            elif self.signal_state == "YELLOW":
                self.canvas.itemconfig(self.signal_timer_labels[self.current_signal], 
                                     text=f"{self.time_remaining}s", fill="#ffeb3b")
        
        if self.time_remaining <= 0:
            self.change_signal()
        
        # Spawn new vehicles
        self.spawn_counter += 1
        if self.spawn_counter >= 4:
            self.spawn_counter = 0
            self.spawn_vehicles_continuously()
        
        # Move vehicles
        self.move_vehicles()
        
        # Update statistics
        self.update_statistics()
        self.update_optimization()
        self.update_score()
        
        # Continue animation
        self.animation_id = self.root.after(100, self.update_simulation)
    
    def change_signal(self):
        if self.signal_state == "GREEN":
            self.signal_state = "YELLOW"
            self.time_remaining = 3
            self.yellow_phase = True
            self.update_all_signals()
            return
        
        elif self.signal_state == "YELLOW":
            self.signal_state = "RED"
            self.time_remaining = 0
            self.yellow_phase = False
            
            # Move to next road
            found_next = False
            attempts = 0
            while not found_next and attempts < len(self.road_order):
                self.current_road_index = (self.current_road_index + 1) % len(self.road_order)
                next_road = self.road_order[self.current_road_index]
                if self.traffic.get(next_road, 0) > 0:
                    found_next = True
                attempts += 1
            
            if not found_next:
                self.current_road_index = 0
            
            self.current_signal = self.road_order[self.current_road_index]
            self.signal_state = "GREEN"
            self.time_remaining = self.signal_times[self.current_signal]
            self.cycle_count += 1
            self.update_all_signals()
            return
    
    def move_vehicles(self):
        if self.current_signal is None:
            return
        
        vehicles_to_remove = []
        
        for idx, vehicle in enumerate(self.vehicle_data):
            if not vehicle.get("active", True):
                continue
            
            road = vehicle["road"]
            positions = self.road_positions[road]
            
            # Check if vehicle should move
            can_move = False
            if road == self.current_signal:
                if self.signal_state == "GREEN":
                    can_move = True
                elif self.signal_state == "YELLOW":
                    # Slow down during yellow (reduce speed)
                    if vehicle["progress"] < 0.7:
                        can_move = True
                        vehicle["speed"] = vehicle["speed"] * 0.5
            
            if can_move:
                dx, dy = positions["direction"]
                vehicle["progress"] += vehicle["speed"]
                
                if vehicle["progress"] >= 1.0:
                    vehicles_to_remove.append(idx)
                    self.total_processed += 1
                    if self.waiting.get(road, 0) > 0:
                        self.waiting[road] = max(0, self.waiting[road] - 1)
                    continue
                
                start_x, start_y = positions["start"]
                end_x, end_y = positions["end"]
                new_x = start_x + (end_x - start_x) * vehicle["progress"]
                new_y = start_y + (end_y - start_y) * vehicle["progress"]
                
                dx_move = new_x - vehicle["x"]
                dy_move = new_y - vehicle["y"]
                
                for obj in vehicle["objects"]:
                    self.canvas.move(obj, dx_move, dy_move)
                
                vehicle["x"], vehicle["y"] = new_x, new_y
        
        # Remove vehicles that passed through
        for idx in sorted(vehicles_to_remove, reverse=True):
            if idx < len(self.vehicle_data):
                for obj in self.vehicle_data[idx]["objects"]:
                    self.canvas.delete(obj)
                    if obj in self.vehicle_objects:
                        self.vehicle_objects.remove(obj)
                del self.vehicle_data[idx]
    
    def toggle_pause(self):
        if not self.simulation_running:
            return
        
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="▶ RESUME")
        else:
            self.pause_btn.config(text="⏸ PAUSE")
    
    def reset_simulation(self):
        self.simulation_running = False
        self.paused = False
        self.pause_btn.config(text="⏸ PAUSE")
        
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        
        for obj in self.vehicle_objects:
            self.canvas.delete(obj)
        self.vehicle_objects = []
        self.vehicle_data = []
        
        for road, lights in self.signal_lights.items():
            self.canvas.itemconfig(lights["red"], fill="#f44336", outline="#ef5350")
            self.canvas.itemconfig(lights["yellow"], fill="#333", outline="#555")
            self.canvas.itemconfig(lights["green"], fill="#333", outline="#555")
            self.canvas.itemconfig(self.signal_timer_labels[road], text="0s", fill="#f44336")
        
        self.current_signal = None
        self.signal_state = "RED"
        self.time_remaining = 0
        self.score = 100
        self.total_processed = 0
        self.efficiency = 0
        self.cycle_count = 0
        self.timer_counter = 0
        self.spawn_counter = 0
        self.yellow_phase = False
        
        for road in self.waiting:
            self.waiting[road] = self.traffic.get(road, 0)
        
        self.update_statistics()
        self.update_optimization()
        self.update_score()
        self.update_set_display()
    
    def generate_new_traffic(self):
        if self.simulation_running:
            self.reset_simulation()
        
        for road, entry in self.entries.items():
            value = random.randint(5, 70)
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
        
        self.get_input_data()
        self.create_traffic_sets()
        self.update_statistics()
    
    def update_set_display(self):
        self.set_text.config(state=tk.NORMAL)
        self.set_text.delete(1.0, tk.END)
        
        self.set_text.insert(tk.END, f"U = {self.universal_set}\n\n")
        self.set_text.insert(tk.END, f"L = {self.low_set or '∅'}\n")
        self.set_text.insert(tk.END, f"M = {self.medium_set or '∅'}\n")
        self.set_text.insert(tk.END, f"H = {self.high_set or '∅'}\n\n")
        self.set_text.insert(tk.END, f"U = L ∪ M ∪ H")
        
        self.set_text.config(state=tk.DISABLED)
    
    def update_statistics(self):
        self.stats_text.delete(1.0, tk.END)
        
        total = sum(self.traffic.values())
        avg = total / 4 if total > 0 else 0
        max_count = max(self.traffic.values()) if self.traffic else 0
        min_count = min(self.traffic.values()) if self.traffic else 0
        
        priority_roads = self.find_priority_road()
        priority_str = ", ".join(priority_roads)
        
        waiting_total = sum(self.waiting.values())
        if waiting_total <= 30:
            self.congestion_level = "LOW"
        elif waiting_total <= 70:
            self.congestion_level = "MEDIUM"
        else:
            self.congestion_level = "HIGH"
        
        if total > 0:
            self.efficiency = (self.total_processed / total) * 100
        else:
            self.efficiency = 0
        
        active_vehicles = len(self.vehicle_data)
        
        stats = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 TRAFFIC STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Veh    : {total:>4}
Average      : {avg:>4.1f}
Highest      : {max_count:>4}
Lowest       : {min_count:>4}
Priority     : {priority_str:>4}
Active       : {active_vehicles:>4}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚦 SIGNAL
Current      : {self.current_signal or 'None':>4}
State        : {self.signal_state:>4}
Time Left    : {self.time_remaining:>3}s
Cycle        : {self.cycle_count:>4}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 PERFORMANCE
Congestion   : {self.congestion_level:>4}
Efficiency   : {self.efficiency:>4.1f}%
Waiting Total: {waiting_total:>4}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WAITING:
N:{self.waiting['North']:>2} S:{self.waiting['South']:>2}
E:{self.waiting['East']:>2} W:{self.waiting['West']:>2}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        self.stats_text.insert(tk.END, stats)
    
    def update_optimization(self):
        self.opt_text.delete(1.0, tk.END)
        
        priority_roads = self.find_priority_road()
        priority_str = ", ".join(priority_roads)
        
        if priority_roads and priority_roads != ["None"]:
            main_road = priority_roads[0]
            count = self.traffic.get(main_road, 0)
            level = "LOW" if count < 20 else "MEDIUM" if count <= 50 else "HIGH"
            time = self.signal_times.get(main_road, 20)
            
            opt_text = f"""━━━━━━━━━━━━━━━━━━━━━━━━
🎯 OPTIMIZATION
━━━━━━━━━━━━━━━━━━━━━━━━
Priority   : {priority_str}
Traffic    : {count} veh
Level      : {level}
Green Time : {time}s
Status     : ✅ OPTIMIZED
━━━━━━━━━━━━━━━━━━━━━━━━
💡 Give longer green
time to {priority_str}
to reduce congestion.
━━━━━━━━━━━━━━━━━━━━━━━━"""
        else:
            opt_text = """━━━━━━━━━━━━━━━━━━━━━━━━
🎯 OPTIMIZATION
━━━━━━━━━━━━━━━━━━━━━━━━
No traffic data available.
Enter vehicle counts and
start the simulation.
━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        self.opt_text.insert(tk.END, opt_text)
    
    def update_score(self):
        if self.congestion_level == "LOW":
            self.score = min(100, self.score + 1.0)
        elif self.congestion_level == "MEDIUM":
            self.score = max(0, self.score - 0.5)
        else:
            self.score = max(0, self.score - 2)
        
        if self.efficiency > 80:
            self.score = min(100, self.score + 0.5)
        elif self.efficiency > 50:
            self.score = min(100, self.score + 0.2)
        
        self.score = max(0, min(100, self.score))
        
        if self.score >= 80:
            self.game_status = "✅ Excellent"
            status_color = "#66bb6a"
            bar_color = "#4caf50"
        elif self.score >= 60:
            self.game_status = "⚠️ Good"
            status_color = "#ffa726"
            bar_color = "#ffa726"
        elif self.score >= 40:
            self.game_status = "⚠️ Warning"
            status_color = "#ef5350"
            bar_color = "#ef5350"
        else:
            self.game_status = "🚨 Critical"
            status_color = "#d32f2f"
            bar_color = "#d32f2f"
        
        self.score_label.config(text=f"{int(self.score)} / 100")
        self.status_label.config(text=self.game_status, fg=status_color)
        
        self.score_bar.delete("bar")
        width = int((self.score / 100) * 210)
        self.score_bar.create_rectangle(0, 0, width, 4, fill=bar_color, tags="bar")
    
    def generate_report(self):
        if not any(self.traffic.values()):
            messagebox.showinfo("No Data", "Please enter traffic data first.")
            return
        
        report_window = tk.Toplevel(self.root)
        report_window.title("📄 Traffic Flow Analysis Report")
        report_window.geometry("600x500")
        report_window.configure(bg="#0a0e1a")
        
        title_frame = tk.Frame(report_window, bg="#0f1a2e", height=35)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="📄 TRAFFIC FLOW ANALYSIS REPORT", 
                font=("Arial", 12, "bold"), fg="#4fc3f7", bg="#0f1a2e").pack(pady=7)
        
        text_frame = tk.Frame(report_window, bg="#0a0e1a")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        
        text_area = scrolledtext.ScrolledText(text_frame, width=65, height=20,
                                             font=("Courier", 8), bg="#0d1b2a",
                                             fg="#aabbcc", wrap=tk.WORD,
                                             relief=tk.FLAT)
        text_area.pack(fill=tk.BOTH, expand=True)
        
        priority_roads = self.find_priority_road()
        priority_str = ", ".join(priority_roads)
        
        vehicle_types = {}
        for v in self.vehicle_data:
            t = v.get("type", "car")
            vehicle_types[t] = vehicle_types.get(t, 0) + 1
        
        report = f"""
╔═══════════════════════════════════════════════════════════════════╗
║              TRAFFIC FLOW ANALYSIS REPORT                       ║
║     Traffic Flow Detection and Optimization Using Set Theory    ║
╚═══════════════════════════════════════════════════════════════════╝

📊 INPUT DATA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  North : {self.traffic['North']:>3}  South : {self.traffic['South']:>3}
  East  : {self.traffic['East']:>3}  West  : {self.traffic['West']:>3}
  Total : {sum(self.traffic.values()):>3}

📐 SET THEORY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  U = {self.universal_set}
  L = {self.low_set or '∅'}  M = {self.medium_set or '∅'}  H = {self.high_set or '∅'}

🚦 SIGNAL TIMES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  North: {self.signal_times['North']:>2}s  South: {self.signal_times['South']:>2}s
  East : {self.signal_times['East']:>2}s  West : {self.signal_times['West']:>2}s

🏆 OPTIMIZATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Priority     : {priority_str}
  Efficiency   : {self.efficiency:.1f}%
  Congestion   : {self.congestion_level}
  Score        : {int(self.score)}/100
  Status       : {self.game_status}

🚗 VEHICLES: {', '.join([f"{k}:{v}" for k, v in vehicle_types.items()]) if vehicle_types else 'None'}

💡 RECOMMENDATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Give priority to {priority_str} with highest traffic volume.

═══════════════════════════════════════════════════════════════════
  Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════════════════"""
        
        text_area.insert(tk.END, report)
        text_area.config(state=tk.DISABLED)
        
        close_btn = tk.Button(report_window, text="✖ CLOSE", font=("Arial", 9, "bold"),
                             bg="#ef5350", fg="white", command=report_window.destroy,
                             relief=tk.RAISED, bd=2, cursor="hand2")
        close_btn.pack(pady=6)

def main():
    root = tk.Tk()
    app = TrafficSimulation(root)
    root.mainloop()

if __name__ == "__main__":
    main()

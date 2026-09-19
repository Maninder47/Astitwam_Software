import customtkinter as ctk
from tkinter import ttk, filedialog
import tkinter.messagebox as messagebox
import pandas as pd
from datetime import datetime
import requests
import json
from PIL import Image

# --- 1. RENDER CLOUD API CONNECTION ---
class Database:
    def __init__(self):
        # 🚨 PASTE YOUR RENDER URL HERE (No trailing slash) 🚨
        self.api_url = "https://astitwam.onrender.com"

    def verify_login(self, username, password):
        try:
            res = requests.post(f"{self.api_url}/login", json={"username": username, "password": password})
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == "success": return data.get("role")
            return None
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server.\n{e}")
            return None

    # --- EMPLOYEES CRUD ---
    def add_employee(self, name, emp_id, email, mobile, course, role, doj):
        payload = {"name": name, "emp_id": emp_id, "email": email, "mobile": mobile, "course": course, "role": role, "doj": doj}
        try: requests.post(f"{self.api_url}/employees", json=payload)
        except Exception as e: messagebox.showerror("Error", f"Failed to save.\n{e}")

    def fetch_employees(self):
        try:
            res = requests.get(f"{self.api_url}/employees")
            if res.status_code == 200:
                records = res.json().get("data", [])
                padded = []
                for idx, row in enumerate(records):
                    while len(row) < 7: row.append("")
                    padded.append([idx + 2] + row)
                return padded
        except: pass
        return []

    def update_employee(self, row_id, name, emp_id, email, mobile, course, role, doj):
        payload = {"name": name, "emp_id": emp_id, "email": email, "mobile": mobile, "course": course, "role": role, "doj": doj}
        try: requests.put(f"{self.api_url}/employees/{row_id}", json=payload)
        except Exception as e: messagebox.showerror("Error", f"Failed to update.\n{e}")

    def delete_employee(self, row_id):
        try: requests.delete(f"{self.api_url}/employees/{row_id}")
        except Exception as e: messagebox.showerror("Error", f"Failed to delete.\n{e}")

    def add_employees_bulk(self, employee_list):
        payload = {"employees": employee_list}
        try:
            res = requests.post(f"{self.api_url}/employees/bulk", json=payload)
            return res.status_code == 200
        except Exception as e:
            messagebox.showerror("Bulk Error", f"Bulk backend transmission failed.\n{e}")
            return False

    # --- EVENTS CRUD ---
    def add_event(self, name, e_type, date, desc, team):
        payload = {"name": name, "e_type": e_type, "date": date, "desc": desc, "team": team}
        try: requests.post(f"{self.api_url}/events", json=payload)
        except Exception as e: messagebox.showerror("Error", f"Failed to save.\n{e}")

    def fetch_events(self):
        try:
            res = requests.get(f"{self.api_url}/events")
            if res.status_code == 200:
                records = res.json().get("data", [])
                return [[idx + 2] + row for idx, row in enumerate(records)]
        except: pass
        return []

    def update_event(self, row_id, name, e_type, date, desc, team):
        payload = {"name": name, "e_type": e_type, "date": date, "desc": desc, "team": team}
        try: requests.put(f"{self.api_url}/events/{row_id}", json=payload)
        except Exception as e: messagebox.showerror("Error", f"Failed to update.\n{e}")

    def delete_event(self, row_id):
        try: requests.delete(f"{self.api_url}/events/{row_id}")
        except Exception as e: messagebox.showerror("Error", f"Failed to delete.\n{e}")

    # --- MEETINGS CRUD ---
    def add_meeting(self, date, target_role, present_str, absent_str):
        payload = {"date": date, "target_role": target_role, "present_str": present_str, "absent_str": absent_str}
        try: requests.post(f"{self.api_url}/meetings", json=payload)
        except Exception as e: messagebox.showerror("Error", f"Failed to save.\n{e}")

    def fetch_meetings(self):
        try:
            res = requests.get(f"{self.api_url}/meetings")
            if res.status_code == 200:
                records = res.json().get("data", [])
                return [[idx + 2] + row for idx, row in enumerate(records)]
        except: pass
        return []

# --- 2. MAIN ENTERPRISE APPLICATION ---
class AstitwamApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = Database()
        
        # Wake up Render Server instantly
        try: requests.get(self.db.api_url, timeout=2) 
        except: pass

        self.title("Astitwam WorkSpace")
        self.geometry("1400x850") 
        
        self.bg_dark = "#040811"
        self.sidebar_color = "#0A1121"
        self.card_color = "#121C33"
        self.blue_accent = "#005BFF"
        self.text_color = "#E0E6ED"
        self.text_muted = "#8898AA"
        
        self.PERMISSION_MAP = {
            "ceo": ["home", "events", "dls", "employees"], 
            "coo": ["home", "events", "dls"],
            "cmo": ["home", "events", "dls"],
            "pr":  ["home", "events", "dls"],
            "hr":  ["home", "employees", "attendance"],
            "admin": ["home", "events", "meetings", "employees", "attendance", "dls"]
        }
        
        self.astitwam_roles = [
            "Brand / Campus Ambassador", "Social Media Manager", "Content Writer & Creator",
            "Graphic Designer", "Sponsorship & Partnerships Manager", "Public Relations (Industry)",
            "Public Relations (Institute)", "Public Speaker / Anchor", "Event Planner & Manager",
            "Event Safety Coordinator", "Event Usability Tester", "Logistics & Operations Manager",
            "Hospitality & Guest Relations", "Set Design & Decor", "Finance & Accounts Manager",
            "Internal Audit & Compliance", "Human Resource (HR) Manager", "Resume & Portfolio Mentor",
            "Photographer & Videographer", "Video Editor", "Script Writer / Emcee",
            "Tech - Web Developer", "Tech - UI/UX Designer", "Tech - AV & Sound Engineer",
            "Research & Data Analyst", "Legal & Compliance Officer", "Operations & Strategy Manager",
            "Community Manager", "Vendor Manager", "Sustainability & CSR Coordinator",
            "Executive Communications Officer", "Mentorship Lead", "Other"
        ]

        self.logo_large = None
        self.logo_small = None
        try:
            img = Image.open("1000403119.png")
            self.logo_large = ctk.CTkImage(light_image=img, dark_image=img, size=(160, 160))
            self.logo_small = ctk.CTkImage(light_image=img, dark_image=img, size=(70, 70))
        except: pass
        
        self.configure(fg_color=self.bg_dark)
        self.current_frame = None
        self.cached_employees = []
        self.cached_events = []
        self.cached_meetings = []
        
        self.show_login_screen()

    def clear_screen(self):
        for widget in self.winfo_children(): widget.destroy()

    def clear_content(self):
        for widget in self.content_area.winfo_children(): widget.destroy()

    def apply_navy_table_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=self.sidebar_color, foreground=self.text_color, fieldbackground=self.sidebar_color, borderwidth=0, font=("Arial", 12), rowheight=35)
        style.configure("Treeview.Heading", background=self.card_color, foreground=self.blue_accent, font=("Arial", 13, "bold"), borderwidth=0)
        style.map('Treeview', background=[('selected', self.blue_accent)])

    # --- 3. LOGIN SCREEN ---
    def show_login_screen(self):
        self.clear_screen()
        login_container = ctk.CTkFrame(self, fg_color="transparent")
        login_container.pack(expand=True, fill="both")
        
        card = ctk.CTkFrame(login_container, fg_color=self.sidebar_color, corner_radius=20, border_width=1, border_color=self.blue_accent)
        card.pack(pady=150, padx=400, fill="both", expand=True)
        
        if self.logo_large: ctk.CTkLabel(card, image=self.logo_large, text="").pack(pady=(40, 10))
        else: ctk.CTkLabel(card, text="ASTITWAM", font=("Arial Black", 38, "bold"), text_color=self.blue_accent).pack(pady=(50, 5))
            
        ctk.CTkLabel(card, text="WORKSPACE", font=("Arial", 14, "bold"), text_color="#556B8D").pack(pady=(0, 30))
        
        self.user_entry = ctk.CTkEntry(card, placeholder_text="Username", width=320, height=50, font=("Arial", 16), fg_color=self.bg_dark, border_color=self.blue_accent)
        self.user_entry.pack(pady=10)
        self.pass_entry = ctk.CTkEntry(card, placeholder_text="Password", width=320, height=50, font=("Arial", 16), fg_color=self.bg_dark, border_color=self.blue_accent, show="*")
        self.pass_entry.pack(pady=10)
        
        ctk.CTkButton(card, text="AUTHENTICATE", font=("Arial", 16, "bold"), fg_color=self.blue_accent, hover_color="#0046CC", width=320, height=50, command=self.attempt_login).pack(pady=30)

    def attempt_login(self):
        role = self.db.verify_login(self.user_entry.get().strip(), self.pass_entry.get().strip())
        if role: 
            self.role = role
            self.username = self.user_entry.get().strip()
            self.show_main_workspace()
        else: messagebox.showerror("Access Denied", "Invalid username or password.")

    # --- 4. MAIN WORKSPACE ---
    def show_main_workspace(self):
        self.clear_screen()
        self.cached_employees = self.db.fetch_employees()
        self.cached_events = self.db.fetch_events()
        self.cached_meetings = self.db.fetch_meetings()

        self.sidebar = ctk.CTkFrame(self, width=280, fg_color=self.sidebar_color, corner_radius=0)
        self.sidebar.pack(side="left", fill="y"); self.sidebar.pack_propagate(False)

        if self.logo_small:
            lf = ctk.CTkFrame(self.sidebar, fg_color="transparent"); lf.pack(pady=(40, 20))
            ctk.CTkLabel(lf, image=self.logo_small, text="").pack(side="left", padx=10)
            ctk.CTkLabel(lf, text="ASTITWAM", font=("Arial Black", 22, "bold"), text_color=self.blue_accent).pack(side="left")
        else:
            ctk.CTkLabel(self.sidebar, text="ASTITWAM", font=("Arial Black", 28, "bold"), text_color=self.blue_accent).pack(pady=(40, 5))
            
        ctk.CTkLabel(self.sidebar, text="OPERATIONS", font=("Arial", 12, "bold"), text_color="#556B8D").pack(pady=(0, 40))

        all_nav_items = [("Home Dashboard", self.load_home), ("Event Management", self.load_events),
                         ("Meetings & Syncs", self.load_meetings), ("Employee Directory", self.load_employees),
                         ("Attendance & DLs", self.load_attendance)]
        
        for text, command in all_nav_items:
            ctk.CTkButton(self.sidebar, text=text, font=("Arial", 16, "bold"), fg_color="transparent", text_color=self.text_color, hover_color=self.card_color, anchor="w", height=45, command=command).pack(fill="x", padx=20, pady=5)

        user_frame = ctk.CTkFrame(self.sidebar, fg_color=self.card_color, corner_radius=10)
        user_frame.pack(side="bottom", fill="x", padx=15, pady=20)
        ctk.CTkLabel(user_frame, text=self.username.upper(), font=("Arial", 16, "bold"), text_color=self.blue_accent).pack(pady=(15,0))
        ctk.CTkLabel(user_frame, text=f"Role: {self.role.capitalize()}", font=("Arial", 13), text_color=self.text_muted).pack(pady=(0,15))
        ctk.CTkButton(user_frame, text="Log Out", fg_color="#D32F2F", font=("Arial", 14, "bold"), width=180, height=40, command=self.show_login_screen).pack(pady=(0, 15))

        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.pack(side="right", fill="both", expand=True)
        self.load_home()

    # --- 5. HOME DASHBOARD ---
    def load_home(self):
        self.clear_content()
        header = ctk.CTkFrame(self.content_area, fg_color="transparent"); header.pack(fill="x", padx=40, pady=(40, 20))
        ctk.CTkLabel(header, text="Command Center", font=("Arial", 32, "bold"), text_color=self.text_color).pack(side="left")
        
        metrics = ctk.CTkFrame(self.content_area, fg_color="transparent"); metrics.pack(fill="x", padx=40, pady=10)
        
        card1 = ctk.CTkFrame(metrics, fg_color=self.card_color, corner_radius=15, width=300, height=140); card1.pack(side="left", padx=(0, 20), expand=True, fill="both")
        ctk.CTkLabel(card1, text="Active Members", font=("Arial", 16), text_color=self.text_muted).pack(pady=(25, 5))
        ctk.CTkLabel(card1, text=str(len(self.cached_employees)), font=("Arial Black", 42), text_color=self.blue_accent).pack()

        card2 = ctk.CTkFrame(metrics, fg_color=self.card_color, corner_radius=15, width=300, height=140); card2.pack(side="left", padx=20, expand=True, fill="both")
        ctk.CTkLabel(card2, text="Events Logged", font=("Arial", 16), text_color=self.text_muted).pack(pady=(25, 5))
        ctk.CTkLabel(card2, text=str(len(self.cached_events)), font=("Arial Black", 42), text_color="#00E676").pack()
        
        ctk.CTkLabel(self.content_area, text="Recent & Upcoming Events", font=("Arial", 20, "bold"), text_color=self.text_color).pack(anchor="w", padx=40, pady=(40, 10))
        list_frame = ctk.CTkFrame(self.content_area, fg_color=self.sidebar_color, corner_radius=10); list_frame.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        for ev in self.cached_events[-5:]:
            row = ctk.CTkFrame(list_frame, fg_color="transparent"); row.pack(fill="x", padx=20, pady=15)
            ctk.CTkLabel(row, text=f"📅 {ev[3]}", font=("Arial", 14, "bold"), text_color=self.blue_accent, width=140, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=ev[1], font=("Arial", 16, "bold"), text_color=self.text_color).pack(side="left", padx=20)
            ctk.CTkLabel(row, text=f"Type: {ev[2]}", font=("Arial", 14), text_color=self.text_muted).pack(side="right")

    # --- 6. EVENT MANAGEMENT ---
    def load_events(self):
        self.clear_content()
        header = ctk.CTkFrame(self.content_area, fg_color="transparent"); header.pack(fill="x", padx=40, pady=(30, 5))
        ctk.CTkLabel(header, text="Event Management", font=("Arial", 32, "bold"), text_color=self.text_color).pack(side="left")
        
        controls = ctk.CTkFrame(self.content_area, fg_color="transparent"); controls.pack(fill="x", padx=40, pady=5)
        
        self.ev_search = ctk.StringVar()
        self.ev_search.trace("w", lambda *args: self.populate_event_table([ev for ev in self.cached_events if any(self.ev_search.get().lower() in str(i).lower() for i in ev)]))
        ctk.CTkEntry(controls, textvariable=self.ev_search, placeholder_text="🔍 Search events...", font=("Arial", 14), width=350, height=45, fg_color=self.sidebar_color, border_color=self.blue_accent).pack(side="left")

        if self.role.lower() in ["admin", "ceo", "coo", "cmo", "pr"]:
            ctk.CTkButton(controls, text="+ Add Event", font=("Arial", 14, "bold"), height=40, fg_color=self.blue_accent, command=lambda: self.open_event_modal(mode="add")).pack(side="right", padx=5)
            ctk.CTkButton(controls, text="Edit Event", font=("Arial", 14, "bold"), height=40, fg_color="#1E88E5", hover_color="#1565C0", command=lambda: self.open_event_modal(mode="edit")).pack(side="right", padx=5)
            ctk.CTkButton(controls, text="Delete", font=("Arial", 14, "bold"), height=40, fg_color="#D32F2F", command=self.delete_selected_event).pack(side="right", padx=5)
            
        ctk.CTkButton(controls, text="View Team", font=("Arial", 14, "bold"), height=40, fg_color="#F57C00", hover_color="#E65100", command=self.view_event_team).pack(side="right", padx=5)
        ctk.CTkButton(controls, text="Refresh DB", font=("Arial", 14, "bold"), height=40, fg_color="#4CAF50", command=self.hard_refresh_events).pack(side="right", padx=20)

        tree_f = ctk.CTkFrame(self.content_area, fg_color=self.card_color); tree_f.pack(fill="both", expand=True, padx=40, pady=(10, 10))
        self.apply_navy_table_style()

        cols = ("DB_ID", "Event Name", "Event Type", "Event Date", "Description", "Assigned Team Roles")
        self.ev_tree = ttk.Treeview(tree_f, columns=cols, show="headings")
        self.ev_tree.column("DB_ID", width=0, stretch=False)
        for col in cols[1:]: self.ev_tree.heading(col, text=col); self.ev_tree.column(col, width=150, anchor="w")
        self.ev_tree.column("Description", width=250); self.ev_tree.column("Assigned Team Roles", width=200)
        self.ev_tree.pack(fill="both", expand=True, padx=2, pady=2)
        
        pane_f = ctk.CTkFrame(self.content_area, fg_color="transparent"); pane_f.pack(fill="x", padx=40, pady=(0, 20))
        ctk.CTkLabel(pane_f, text="Event Description Details:", font=("Arial", 14, "bold"), text_color=self.blue_accent).pack(anchor="w")
        self.desc_viewer = ctk.CTkTextbox(pane_f, font=("Arial", 14), height=100, fg_color=self.sidebar_color, text_color=self.text_color, wrap="word", border_width=1, border_color=self.card_color)
        self.desc_viewer.pack(fill="x", pady=5)
        self.desc_viewer.insert("0.0", "Click on any event in the table above to read the full description here...")
        self.desc_viewer.configure(state="disabled")
        self.ev_tree.bind("<<TreeviewSelect>>", self.display_full_description)
        self.populate_event_table(self.cached_events)

    def populate_event_table(self, data):
        for row in self.ev_tree.get_children(): self.ev_tree.delete(row)
        for ev in data:
            display_ev = list(ev)
            raw_desc = str(display_ev[4])
            if len(raw_desc) > 35: display_ev[4] = raw_desc[:35] + "..."
            team_str = str(display_ev[5])
            display_ev[5] = f"{len(team_str.split(', '))} Members Assigned" if team_str and team_str.strip() and team_str != "nan" else "No Team"
            self.ev_tree.insert("", "end", values=display_ev)

    def display_full_description(self, event):
        selected = self.ev_tree.selection()
        if selected:
            db_id = self.ev_tree.item(selected)["values"][0]
            raw_ev = next((e for e in self.cached_events if str(e[0]) == str(db_id)), None)
            if raw_ev:
                self.desc_viewer.configure(state="normal")
                self.desc_viewer.delete("0.0", "end")
                self.desc_viewer.insert("0.0", str(raw_ev[4]))
                self.desc_viewer.configure(state="disabled")

    def hard_refresh_events(self):
        self.cached_events = self.db.fetch_events()
        self.populate_event_table(self.cached_events)

    def delete_selected_event(self):
        sel = self.ev_tree.selection()
        if sel: 
            self.db.delete_event(self.ev_tree.item(sel)["values"][0])
            self.hard_refresh_events()

    def view_event_team(self):
        selected = self.ev_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please click on an event first to view its team.")
            return
        db_id = self.ev_tree.item(selected)["values"][0]
        raw_ev = next((e for e in self.cached_events if str(e[0]) == str(db_id)), None)
        if not raw_ev: return

        event_name = raw_ev[1]
        team_str = str(raw_ev[5])

        modal = ctk.CTkToplevel(self)
        modal.title("Team Roster"); modal.geometry("450x500"); modal.configure(fg_color=self.card_color); modal.attributes("-topmost", True)
        ctk.CTkLabel(modal, text=f"Team: {event_name}", font=("Arial", 22, "bold"), text_color=self.blue_accent).pack(pady=15)
        scroll = ctk.CTkScrollableFrame(modal, fg_color=self.bg_dark); scroll.pack(fill="both", expand=True, padx=20, pady=10)

        if not team_str or team_str == "nan" or not team_str.strip():
            ctk.CTkLabel(scroll, text="No team members assigned yet.", font=("Arial", 14), text_color=self.text_muted).pack(pady=20)
        else:
            for part in team_str.split(", "):
                row = ctk.CTkFrame(scroll, fg_color="transparent"); row.pack(fill="x", pady=5)
                if " (" in part and part.endswith(")"): n, r = part.split(" ("); r = r[:-1]
                else: n, r = part, "Member"
                ctk.CTkLabel(row, text=n, font=("Arial", 15, "bold"), text_color=self.text_color, anchor="w", width=200).pack(side="left")
                ctk.CTkLabel(row, text=r, font=("Arial", 14, "bold"), text_color="#00E676", anchor="w").pack(side="left")
        ctk.CTkButton(modal, text="Close", font=("Arial", 14, "bold"), height=40, fg_color=self.sidebar_color, hover_color=self.bg_dark, command=modal.destroy).pack(pady=15)

    def open_event_modal(self, mode="add"):
        db_id = None
        current_vals = ["", "", "", "", "", ""]
        self.current_team_dict = {}

        if mode == "edit":
            selected = self.ev_tree.selection()
            if not selected:
                messagebox.showwarning("Selection Error", "Please click on an event first to edit.")
                return
            db_id = self.ev_tree.item(selected)["values"][0]
            raw_ev = next((e for e in self.cached_events if str(e[0]) == str(db_id)), None)
            if not raw_ev: return
            current_vals = raw_ev
            team_str = str(current_vals[5])
            if team_str and team_str != "nan":
                for part in team_str.split(", "):
                    if " (" in part and part.endswith(")"): n, r = part.split(" ("); self.current_team_dict[n] = r[:-1]
                    else: self.current_team_dict[part] = "Member"

        modal = ctk.CTkToplevel(self)
        modal.title(f"{'Edit' if mode=='edit' else 'Create'} Event"); modal.geometry("700x650"); modal.configure(fg_color=self.card_color); modal.attributes("-topmost", True)
        ctk.CTkLabel(modal, text=f"{'Edit' if mode=='edit' else 'New'} Event Details", font=("Arial", 22, "bold"), text_color=self.blue_accent).pack(pady=20)
        
        form = ctk.CTkFrame(modal, fg_color="transparent"); form.pack(fill="both", expand=True, padx=40)
        ev_name = ctk.CTkEntry(form, placeholder_text="Event Name", font=("Arial", 14), width=450, height=45, fg_color=self.bg_dark, border_color=self.blue_accent)
        if current_vals[1]: ev_name.insert(0, str(current_vals[1]))
        ev_name.pack(pady=10)
        ev_type_var = ctk.StringVar(value=current_vals[2] if current_vals[2] else "Select Type")
        ctk.CTkOptionMenu(form, variable=ev_type_var, font=("Arial", 14), values=["CTF", "Hackathon", "Workshop", "Other"], width=450, height=45, fg_color=self.bg_dark, button_color=self.blue_accent).pack(pady=10)
        ev_date = ctk.CTkEntry(form, placeholder_text="Date (DD/MM/YYYY)", font=("Arial", 14), width=450, height=45, fg_color=self.bg_dark, border_color=self.blue_accent)
        if current_vals[3]: ev_date.insert(0, str(current_vals[3]))
        ev_date.pack(pady=10)
        ev_desc = ctk.CTkTextbox(form, font=("Arial", 14), width=450, height=100, fg_color=self.bg_dark, border_color=self.blue_accent, border_width=1)
        ev_desc.insert("0.0", str(current_vals[4]) if current_vals[4] else "Event Description...")
        ev_desc.pack(pady=10)

        team_frame = ctk.CTkFrame(form, fg_color="transparent"); team_frame.pack(pady=15, fill="x")
        self.team_status_label = ctk.CTkLabel(team_frame, text=f"{len(self.current_team_dict)} Members Assigned", font=("Arial", 14, "bold"), text_color="#00E676")
        self.team_status_label.pack(side="left", padx=10)
        
        def open_team_roles_modal():
            modal.attributes("-topmost", False) 
            role_modal = ctk.CTkToplevel(self)
            role_modal.title("Assign Roles"); role_modal.geometry("500x600"); role_modal.configure(fg_color=self.card_color); role_modal.attributes("-topmost", True); role_modal.focus(); role_modal.grab_set() 
            ctk.CTkLabel(role_modal, text="Assign Team Roles", font=("Arial", 20, "bold"), text_color=self.blue_accent).pack(pady=15)
            scroll = ctk.CTkScrollableFrame(role_modal, fg_color=self.bg_dark); scroll.pack(fill="both", expand=True, padx=20, pady=10)
            hf = ctk.CTkFrame(scroll, fg_color="transparent"); hf.pack(fill="x", pady=5)
            ctk.CTkLabel(hf, text="Employee", font=("Arial", 12, "bold"), width=200, anchor="w").pack(side="left")
            ctk.CTkLabel(hf, text="Event Role", font=("Arial", 12, "bold"), width=150, anchor="w").pack(side="left")
            
            control_dict = {} 
            for emp in self.cached_employees:
                emp_name = emp[1]
                row = ctk.CTkFrame(scroll, fg_color="transparent"); row.pack(fill="x", pady=5)
                check_var = ctk.StringVar(value=emp_name if emp_name in self.current_team_dict else "off")
                cb = ctk.CTkCheckBox(row, text=emp_name, variable=check_var, onvalue=emp_name, offvalue="off", font=("Arial", 14), width=200, fg_color=self.blue_accent); cb.pack(side="left")
                role_entry = ctk.CTkEntry(row, placeholder_text="e.g. Organizer", font=("Arial", 13), width=150, height=30, fg_color=self.card_color, border_width=0)
                if emp_name in self.current_team_dict: role_entry.insert(0, self.current_team_dict[emp_name])
                role_entry.pack(side="left", padx=10)
                control_dict[emp_name] = {"check": check_var, "role_input": role_entry}
                
            def save_team():
                self.current_team_dict.clear()
                for name, controls in control_dict.items():
                    if controls["check"].get() != "off":
                        r_text = controls["role_input"].get().strip()
                        self.current_team_dict[name] = r_text if r_text else "Member"
                self.team_status_label.configure(text=f"{len(self.current_team_dict)} Members Assigned")
                modal.attributes("-topmost", True); role_modal.destroy()
                
            ctk.CTkButton(role_modal, text="Confirm Roles", font=("Arial", 14, "bold"), height=40, fg_color="#F57C00", hover_color="#E65100", command=save_team).pack(pady=20)
            def on_closing(): modal.attributes("-topmost", True); role_modal.destroy()
            role_modal.protocol("WM_DELETE_WINDOW", on_closing)

        ctk.CTkButton(team_frame, text="Configure Team", font=("Arial", 14, "bold"), height=40, fg_color="#F57C00", hover_color="#E65100", command=open_team_roles_modal).pack(side="right", padx=10)

        def submit_event():
            t = ev_type_var.get()
            team_str = ", ".join([f"{name} ({role})" for name, role in self.current_team_dict.items()])
            if mode == "add":
                self.db.add_event(ev_name.get(), t, ev_date.get(), ev_desc.get("0.0", "end").strip(), team_str)
            else:
                self.db.update_event(db_id, ev_name.get(), t, ev_date.get(), ev_desc.get("0.0", "end").strip(), team_str)
            self.hard_refresh_events(); modal.destroy()
            
        ctk.CTkButton(modal, text=f"{'Save' if mode=='add' else 'Update'} Event Data", font=("Arial", 16, "bold"), height=50, width=450, fg_color=self.blue_accent, command=submit_event).pack(pady=20)

    # --- 7. MEETINGS & SYNCS ---
    def load_meetings(self):
        self.clear_content()
        header = ctk.CTkFrame(self.content_area, fg_color="transparent"); header.pack(fill="x", padx=40, pady=(40, 10))
        ctk.CTkLabel(header, text="Meetings & Syncs", font=("Arial", 32, "bold"), text_color=self.text_color).pack(side="left")
        controls = ctk.CTkFrame(self.content_area, fg_color="transparent"); controls.pack(fill="x", padx=40, pady=10)

        if self.role.lower() in ["admin", "hr"]:
            ctk.CTkButton(controls, text="+ New Meeting", font=("Arial", 14, "bold"), height=45, fg_color=self.blue_accent, command=self.open_new_meeting_modal).pack(side="left")
            
        ctk.CTkButton(controls, text="View Attendance", font=("Arial", 14, "bold"), height=45, fg_color="#F57C00", hover_color="#E65100", command=self.view_meeting_attendance).pack(side="left", padx=10)
        ctk.CTkButton(controls, text="Refresh DB", font=("Arial", 14, "bold"), height=45, fg_color="#4CAF50", command=self.hard_refresh_meetings).pack(side="right", padx=10)

        tree_f = ctk.CTkFrame(self.content_area, fg_color=self.card_color); tree_f.pack(fill="both", expand=True, padx=40, pady=(10, 40))
        self.apply_navy_table_style()
        cols = ("DB_ID", "Date", "Target Role", "Present Members", "Absent Members")
        self.mtg_tree = ttk.Treeview(tree_f, columns=cols, show="headings")
        self.mtg_tree.column("DB_ID", width=0, stretch=False)
        for col in cols[1:]: self.mtg_tree.heading(col, text=col); self.mtg_tree.column(col, width=120 if col == "Date" else 200, anchor="w")
        self.mtg_tree.pack(fill="both", expand=True, padx=2, pady=2)
        self.populate_meetings_table()

    def populate_meetings_table(self):
        for row in self.mtg_tree.get_children(): self.mtg_tree.delete(row)
        for mtg in self.cached_meetings:
            display_mtg = list(mtg)
            present_str = str(display_mtg[3])
            display_mtg[3] = f"{len(present_str.split(', '))} Present" if present_str and present_str != "nan" else "0 Present"
            absent_str = str(display_mtg[4])
            display_mtg[4] = f"{len(absent_str.split(', '))} Absent" if absent_str and absent_str != "nan" and absent_str.strip() else "0 Absent"
            self.mtg_tree.insert("", "end", values=display_mtg)

    def hard_refresh_meetings(self):
        self.cached_meetings = self.db.fetch_meetings()
        self.populate_meetings_table()

    def view_meeting_attendance(self):
        selected = self.mtg_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please click on a meeting first to view attendance.")
            return
        db_id = self.mtg_tree.item(selected)["values"][0]
        raw_mtg = next((m for m in self.cached_meetings if str(m[0]) == str(db_id)), None)
        if not raw_mtg: return

        mtg_date = raw_mtg[1]; mtg_role = raw_mtg[2]; present_str = str(raw_mtg[3]); absent_str = str(raw_mtg[4])
        modal = ctk.CTkToplevel(self)
        modal.title("Attendance Record"); modal.geometry("500x600"); modal.configure(fg_color=self.card_color); modal.attributes("-topmost", True)
        ctk.CTkLabel(modal, text=f"{mtg_role} Sync - {mtg_date}", font=("Arial", 22, "bold"), text_color=self.blue_accent).pack(pady=15)
        scroll = ctk.CTkScrollableFrame(modal, fg_color=self.bg_dark); scroll.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(scroll, text="✅ PRESENT", font=("Arial", 16, "bold"), text_color="#00E676").pack(anchor="w", pady=(10, 5))
        if present_str and present_str != "nan" and present_str.strip():
            for name in present_str.split(", "): ctk.CTkLabel(scroll, text=name, font=("Arial", 14), text_color=self.text_color).pack(anchor="w", padx=20, pady=2)
        else: ctk.CTkLabel(scroll, text="No attendees recorded.", font=("Arial", 14, "italic"), text_color=self.text_muted).pack(anchor="w", padx=20, pady=2)

        ctk.CTkLabel(scroll, text="❌ ABSENT", font=("Arial", 16, "bold"), text_color="#D32F2F").pack(anchor="w", pady=(20, 5))
        if absent_str and absent_str != "nan" and absent_str.strip():
            for name in absent_str.split(", "): ctk.CTkLabel(scroll, text=name, font=("Arial", 14), text_color=self.text_color).pack(anchor="w", padx=20, pady=2)
        else: ctk.CTkLabel(scroll, text="No absentees recorded.", font=("Arial", 14, "italic"), text_color=self.text_muted).pack(anchor="w", padx=20, pady=2)
        ctk.CTkButton(modal, text="Close", font=("Arial", 14, "bold"), height=40, fg_color=self.sidebar_color, hover_color=self.bg_dark, command=modal.destroy).pack(pady=15)

    def open_new_meeting_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Record Meeting Attendance"); modal.geometry("600x750"); modal.configure(fg_color=self.card_color); modal.attributes("-topmost", True)
        ctk.CTkLabel(modal, text="Meeting Attendance", font=("Arial", 22, "bold"), text_color=self.blue_accent).pack(pady=(20, 5))
        
        filter_frame = ctk.CTkFrame(modal, fg_color="transparent"); filter_frame.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(filter_frame, text="Filter by Role:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 10))
        
        role_options = ["All"] + self.astitwam_roles
        self.meeting_role_var = ctk.StringVar(value="All")
        self.attendance_vars = {}

        self.att_scroll = ctk.CTkScrollableFrame(modal, fg_color=self.bg_dark); self.att_scroll.pack(fill="both", expand=True, padx=40, pady=10)

        def populate_roster(*args):
            for widget in self.att_scroll.winfo_children(): widget.destroy()
            self.attendance_vars.clear()
            selected_role = self.meeting_role_var.get()
            for emp in self.cached_employees:
                emp_name = emp[1]; emp_role = str(emp[6]).strip()
                if selected_role == "All" or selected_role.lower() == emp_role.lower():
                    row = ctk.CTkFrame(self.att_scroll, fg_color="transparent"); row.pack(fill="x", pady=5)
                    ctk.CTkLabel(row, text=emp_name, font=("Arial", 14, "bold"), width=180, anchor="w").pack(side="left")
                    ctk.CTkLabel(row, text=emp_role if emp_role else "No Role", font=("Arial", 12), text_color="#8898AA", width=150, anchor="w").pack(side="left")
                    att_var = ctk.StringVar(value="Present"); self.attendance_vars[emp_name] = att_var
                    ctk.CTkRadioButton(row, text="Present", variable=att_var, value="Present", fg_color="#00E676", text_color="#00E676", font=("Arial", 12, "bold")).pack(side="left", padx=10)
                    ctk.CTkRadioButton(row, text="Absent", variable=att_var, value="Absent", fg_color="#D32F2F", text_color="#D32F2F", font=("Arial", 12, "bold")).pack(side="left", padx=10)

        role_menu = ctk.CTkOptionMenu(filter_frame, variable=self.meeting_role_var, values=role_options, font=("Arial", 14), fg_color=self.bg_dark, button_color=self.blue_accent, command=populate_roster)
        role_menu.pack(side="left", fill="x", expand=True)
        populate_roster()

        def save_attendance():
            present_list, absent_list = [], []
            for name, var in self.attendance_vars.items():
                if var.get() == "Present": present_list.append(name)
                else: absent_list.append(name)
            today_date = datetime.now().strftime('%d/%m/%Y')
            target_role = self.meeting_role_var.get()
            self.db.add_meeting(today_date, target_role, ", ".join(present_list), ", ".join(absent_list))
            self.hard_refresh_meetings(); modal.destroy(); messagebox.showinfo("Success", "Meeting attendance saved to the cloud!")
        ctk.CTkButton(modal, text="Save Attendance", font=("Arial", 16, "bold"), height=50, fg_color=self.blue_accent, command=save_attendance).pack(pady=20, padx=40, fill="x")

    # --- 8. EMPLOYEE DIRECTORY ---
    def load_employees(self):
        self.clear_content()
        header = ctk.CTkFrame(self.content_area, fg_color="transparent"); header.pack(fill="x", padx=40, pady=(40, 10))
        ctk.CTkLabel(header, text="Employee Directory", font=("Arial", 32, "bold"), text_color=self.text_color).pack(side="left")
        
        controls = ctk.CTkFrame(self.content_area, fg_color="transparent"); controls.pack(fill="x", padx=40, pady=10)
        
        self.emp_search = ctk.StringVar()
        self.emp_search.trace("w", lambda *args: self.populate_emp_table([emp for emp in self.cached_employees if any(self.emp_search.get().lower() in str(i).lower() for i in emp)]))
        ctk.CTkEntry(controls, textvariable=self.emp_search, placeholder_text="🔍 Search Name, Role, Reg.No...", font=("Arial", 14), width=350, height=45, fg_color=self.sidebar_color, border_color=self.blue_accent).pack(side="left")

        authorized_edit_roles = ["admin", "hr", "ceo"]
        if self.role.lower() in authorized_edit_roles:
            ctk.CTkButton(controls, text="+ Add", font=("Arial", 12, "bold"), width=80, height=40, fg_color=self.blue_accent, command=self.open_add_emp_modal).pack(side="right", padx=5)
            ctk.CTkButton(controls, text="Edit", font=("Arial", 12, "bold"), width=80, height=40, fg_color="#1E88E5", hover_color="#1565C0", command=self.open_edit_emp_modal).pack(side="right", padx=5)
            ctk.CTkButton(controls, text="Delete", font=("Arial", 12, "bold"), width=80, height=40, fg_color="#D32F2F", command=self.delete_selected_emp).pack(side="right", padx=5)
            ctk.CTkButton(controls, text="Import", font=("Arial", 12, "bold"), width=80, height=40, fg_color="#F57C00", command=self.import_emp_from_excel).pack(side="right", padx=5)
            
        ctk.CTkButton(controls, text="Export", font=("Arial", 12, "bold"), width=80, height=40, fg_color="#F57C00", command=self.export_emp_to_excel).pack(side="right", padx=5)
        ctk.CTkButton(controls, text="Refresh", font=("Arial", 12, "bold"), width=80, height=40, fg_color="#4CAF50", command=self.hard_refresh_employees).pack(side="right", padx=20)

        tree_f = ctk.CTkFrame(self.content_area, fg_color=self.card_color); tree_f.pack(fill="both", expand=True, padx=40, pady=(10, 40))
        self.apply_navy_table_style()
        cols = ("DB_ID", "Name", "Reg.No (ID)", "E-mail ID", "Mobile No", "Course", "Role / Desig.", "Date of Joining")
        self.emp_tree = ttk.Treeview(tree_f, columns=cols, show="headings")
        self.emp_tree.column("DB_ID", width=0, stretch=False)
        for col in cols[1:]: self.emp_tree.heading(col, text=col); self.emp_tree.column(col, width=120, anchor="w")
        self.emp_tree.pack(fill="both", expand=True, padx=2, pady=2)
        self.populate_emp_table(self.cached_employees)

    def import_emp_from_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if not file_path: return
        
        try:
            df = pd.read_excel(file_path)
            employee_list = []
            
            for _, row in df.iterrows():
                # Ensure the row has at least 2 columns before processing
                if len(row) < 2: 
                    continue
                    
                # Read ONLY Name and Reg.No, auto-fill the rest with blanks or defaults
                employee_list.append({
                    "name": str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else "",
                    "emp_id": str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else "",
                    "email": "",         # Auto-blank
                    "mobile": "",        # Auto-blank
                    "course": "",        # Auto-blank
                    "role": "Member",    # Default role
                    "doj": datetime.now().strftime('%d/%m/%Y') # Today's date as default
                })
            
            if self.db.add_employees_bulk(employee_list):
                messagebox.showinfo("Success", f"Successfully imported {len(employee_list)} members.")
                self.hard_refresh_employees()
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to read file. Make sure column 1 is Name and column 2 is Reg.No.\n\nError: {e}")

    def open_edit_emp_modal(self):
        selected = self.emp_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please click on an employee first to edit them.")
            return
        
        values = self.emp_tree.item(selected)["values"]
        db_id = values[0]
        
        modal = ctk.CTkToplevel(self)
        modal.title("Edit Employee"); modal.geometry("500x750"); modal.configure(fg_color=self.card_color); modal.attributes("-topmost", True)
        ctk.CTkLabel(modal, text="Edit Member Details", font=("Arial", 22, "bold"), text_color=self.blue_accent).pack(pady=15)
        
        entries = {}
        fields_1 = [("Name", values[1], "Full Name"), ("EmpID", values[2], "Reg.No / Employee ID"), 
                    ("Email", values[3], "E-mail ID"), ("Mobile", values[4], "Mobile No"), ("Course", values[5], "Course")]
        for key, current_val, p in fields_1:
            e = ctk.CTkEntry(modal, width=400, height=45, font=("Arial", 14), placeholder_text=p, fg_color=self.bg_dark, border_color=self.blue_accent, text_color=self.text_color)
            if current_val and str(current_val).strip() not in ["", "nan"]: e.insert(0, str(current_val))
            e.pack(pady=8); entries[key] = e

        current_role = str(values[6]).strip() if values[6] and str(values[6]) != "nan" else ""
        role_other = ctk.CTkEntry(modal, placeholder_text="Specify Custom Role...", width=400, height=45, font=("Arial", 14), fg_color=self.bg_dark, border_color=self.blue_accent, text_color=self.text_color)
        
        def check_role(c):
            if c == "Other": role_other.pack(pady=8, after=role_menu)
            else: role_other.pack_forget()

        role_var = ctk.StringVar(value=current_role if current_role in self.astitwam_roles else ("Other" if current_role else "Select Role"))
        role_menu = ctk.CTkOptionMenu(modal, variable=role_var, values=self.astitwam_roles, width=400, height=45, font=("Arial", 14), fg_color=self.bg_dark, button_color=self.blue_accent, command=check_role)
        role_menu.pack(pady=8)
        
        if role_var.get() == "Other":
            role_other.insert(0, current_role); role_other.pack(pady=8, after=role_menu)

        e_doj = ctk.CTkEntry(modal, width=400, height=45, font=("Arial", 14), placeholder_text="Date of Joining (DD/MM/YYYY)", fg_color=self.bg_dark, border_color=self.blue_accent, text_color=self.text_color)
        if values[7] and str(values[7]) not in ["", "nan"]: e_doj.insert(0, str(values[7]))
        e_doj.pack(pady=8); entries["DOJ"] = e_doj

        def update_data():
            r = role_other.get().strip() if role_var.get() == "Other" else role_var.get()
            if r == "Select Role": r = ""
            self.db.update_employee(db_id, entries["Name"].get(), entries["EmpID"].get(), entries["Email"].get(), entries["Mobile"].get(), entries["Course"].get(), r, e_doj.get())
            self.hard_refresh_employees(); modal.destroy()
            
        ctk.CTkButton(modal, text="Update Database", fg_color="#1E88E5", hover_color="#1565C0", font=("Arial", 16, "bold"), height=50, width=400, command=update_data).pack(pady=20)

    def populate_emp_table(self, data):
        for row in self.emp_tree.get_children(): self.emp_tree.delete(row)
        for emp in data: self.emp_tree.insert("", "end", values=emp)

    def hard_refresh_employees(self):
        self.cached_employees = self.db.fetch_employees()
        self.populate_emp_table(self.cached_employees)

    def delete_selected_emp(self):
        sel = self.emp_tree.selection()
        if sel: 
            self.db.delete_employee(self.emp_tree.item(sel)["values"][0])
            self.hard_refresh_employees()

    def export_emp_to_excel(self):
        try:
            df = pd.DataFrame([e[1:] for e in self.cached_employees], columns=["Name", "Reg.No", "Email", "Mobile", "Course", "Role", "DOJ"])
            filename = f"Astitwam_Employees_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
            df.to_excel(filename, index=False)
            messagebox.showinfo("Success", f"Exported successfully to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to Excel.\nMake sure the file isn't already open.\n\nError: {e}")

    def open_add_emp_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Add New"); modal.geometry("500x750"); modal.configure(fg_color=self.card_color); modal.attributes("-topmost", True)
        ctk.CTkLabel(modal, text="New Member Details", font=("Arial", 22, "bold"), text_color=self.blue_accent).pack(pady=15)
        entries = {}
        for key, p in [("Name", "Full Name"), ("EmpID", "Reg.No / Employee ID"), ("Email", "E-mail ID"), 
                       ("Mobile", "Mobile No"), ("Course", "Course")]:
            e = ctk.CTkEntry(modal, placeholder_text=p, width=400, height=45, font=("Arial", 14), fg_color=self.bg_dark, border_color=self.blue_accent)
            e.pack(pady=8); entries[key] = e
        
        role_other = ctk.CTkEntry(modal, placeholder_text="Specify Custom Role...", width=400, height=45, font=("Arial", 14), fg_color=self.bg_dark, border_color=self.blue_accent)
        role_var = ctk.StringVar(value="Select Role")
        role_menu = ctk.CTkOptionMenu(modal, variable=role_var, values=self.astitwam_roles, width=400, height=45, font=("Arial", 14), fg_color=self.bg_dark, button_color=self.blue_accent, command=lambda c: role_other.pack(pady=8, after=role_menu) if c=="Other" else role_other.pack_forget())
        role_menu.pack(pady=8)
        
        e_doj = ctk.CTkEntry(modal, placeholder_text="Date of Joining (DD/MM/YYYY)", width=400, height=45, font=("Arial", 14), fg_color=self.bg_dark, border_color=self.blue_accent)
        e_doj.insert(0, datetime.now().strftime('%d/%m/%Y'))
        e_doj.pack(pady=8); entries["DOJ"] = e_doj

        def save():
            r = role_other.get().strip() if role_var.get() == "Other" else role_var.get()
            if r == "Select Role": r = ""
            self.db.add_employee(entries["Name"].get(), entries["EmpID"].get(), entries["Email"].get(), entries["Mobile"].get(), entries["Course"].get(), r, e_doj.get())
            self.hard_refresh_employees(); modal.destroy()
        ctk.CTkButton(modal, text="Save to Database", fg_color=self.blue_accent, font=("Arial", 16, "bold"), height=50, width=400, command=save).pack(pady=20)


    # --- 9. ATTENDANCE / DLS ---
    def load_attendance(self):
        self.clear_content()
        header = ctk.CTkFrame(self.content_area, fg_color="transparent"); header.pack(fill="x", padx=40, pady=(40, 10))
        ctk.CTkLabel(header, text="Duty Leave & Attendance", font=("Arial", 32, "bold"), text_color=self.text_color).pack(side="left")

        control = ctk.CTkFrame(self.content_area, fg_color="transparent"); control.pack(fill="x", padx=40, pady=10)
        
        if self.role.lower() in ["admin", "hr", "ceo", "coo", "cmo", "pr"]:
            ctk.CTkButton(control, text="+ Select Members", font=("Arial", 13, "bold"), width=140, fg_color=self.blue_accent, height=45, command=self.open_dl_modal).pack(side="left")
            self.global_date = ctk.CTkEntry(control, placeholder_text="Date", font=("Arial", 14), width=100, fg_color=self.bg_dark, height=45)
            self.global_date.pack(side="left", padx=(20,5))
            ctk.CTkButton(control, text="Set Date", font=("Arial", 12, "bold"), fg_color="#F57C00", hover_color="#E65100", width=80, height=45, command=self.apply_dl_date).pack(side="left", padx=5)
            self.global_start = ctk.CTkEntry(control, placeholder_text="Start", font=("Arial", 14), width=80, fg_color=self.bg_dark, height=45)
            self.global_start.pack(side="left", padx=(15,5))
            self.global_end = ctk.CTkEntry(control, placeholder_text="End", font=("Arial", 14), width=80, fg_color=self.bg_dark, height=45)
            self.global_end.pack(side="left", padx=5)
            ctk.CTkButton(control, text="Set Time", font=("Arial", 12, "bold"), fg_color="#F57C00", hover_color="#E65100", width=80, height=45, command=self.apply_dl_time).pack(side="left", padx=5)
            self.global_type = ctk.CTkOptionMenu(control, values=["P", "V"], font=("Arial", 14), width=70, fg_color=self.bg_dark, height=45, button_color="#F57C00")
            self.global_type.pack(side="left", padx=(15,5))
            ctk.CTkButton(control, text="Set Type", font=("Arial", 12, "bold"), fg_color="#F57C00", hover_color="#E65100", width=80, height=45, command=self.apply_dl_type).pack(side="left", padx=5)
        
        ctk.CTkButton(control, text="Export Excel", font=("Arial", 13, "bold"), fg_color="#1E88E5", width=120, height=45, command=self.export_dl).pack(side="right")

        h_frame = ctk.CTkFrame(self.content_area, fg_color=self.card_color, height=45); h_frame.pack(fill="x", padx=40, pady=(10, 0))
        for t, w in [("Name", 220), ("Reg.No", 140), ("Date", 130), ("Start", 110), ("End", 110), ("Type", 90), ("Signature", 150)]:
            ctk.CTkLabel(h_frame, text=t, font=("Arial", 13, "bold"), text_color=self.blue_accent, width=w, anchor="w").pack(side="left", padx=5)

        self.dl_grid = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent"); self.dl_grid.pack(fill="both", expand=True, padx=40, pady=5)
        self.dl_rows = []

    def open_dl_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Select"); modal.geometry("450x600"); modal.configure(fg_color=self.card_color); modal.attributes("-topmost", True)
        ctk.CTkLabel(modal, text="Check Members", font=("Arial", 22, "bold"), text_color=self.blue_accent).pack(pady=20)
        
        scroll = ctk.CTkScrollableFrame(modal, fg_color=self.bg_dark); scroll.pack(fill="both", expand=True, padx=20, pady=10)
        cbs = []
        for emp in self.cached_employees:
            v = ctk.StringVar(value="off")
            cb = ctk.CTkCheckBox(scroll, text=f"{emp[1]} | {emp[2]}", font=("Arial", 14), variable=v, onvalue=f"{emp[1]} | {emp[2]}", offvalue="off", fg_color=self.blue_accent)
            cb.pack(anchor="w", pady=8, padx=5); cbs.append(v)

        def add():
            for v in cbs:
                if v.get() != "off":
                    n, r = v.get().split(" | ")
                    rf = ctk.CTkFrame(self.dl_grid, fg_color=self.sidebar_color, corner_radius=5); rf.pack(fill="x", pady=3)
                    ctk.CTkLabel(rf, text=n, width=220, font=("Arial", 13), anchor="w").pack(side="left", padx=5)
                    ctk.CTkLabel(rf, text=r, width=140, font=("Arial", 13), anchor="w", text_color="#8898AA").pack(side="left", padx=5)
                    de = ctk.CTkEntry(rf, width=130, height=35, font=("Arial", 13), fg_color=self.bg_dark, border_width=0); de.pack(side="left", padx=5)
                    se = ctk.CTkEntry(rf, width=110, height=35, font=("Arial", 13), fg_color=self.bg_dark, border_width=0); se.pack(side="left", padx=5)
                    ee = ctk.CTkEntry(rf, width=110, height=35, font=("Arial", 13), fg_color=self.bg_dark, border_width=0); ee.pack(side="left", padx=5)
                    tv = ctk.StringVar(value="P")
                    tm = ctk.CTkOptionMenu(rf, variable=tv, values=["P", "V"], font=("Arial", 13), width=90, height=35, fg_color=self.bg_dark, button_color=self.blue_accent); tm.pack(side="left", padx=5)
                    ctk.CTkLabel(rf, text="_________________", width=150, anchor="w", text_color="#555").pack(side="left", padx=5)
                    def rem(rf=rf): rf.destroy(); self.dl_rows = [row for row in self.dl_rows if row["f"] != rf]
                    ctk.CTkButton(rf, text="X", width=35, height=35, font=("Arial", 12, "bold"), fg_color="#D32F2F", command=rem).pack(side="right", padx=5)
                    self.dl_rows.append({"f": rf, "n": n, "r": r, "d": de, "st": se, "et": ee, "t": tv})
            modal.destroy()
        ctk.CTkButton(modal, text="Add Selected", font=("Arial", 16, "bold"), height=50, fg_color=self.blue_accent, command=add).pack(pady=20)

    def apply_dl_date(self):
        d = self.global_date.get()
        for r in self.dl_rows:
            if d: r["d"].delete(0, 'end'); r["d"].insert(0, d)
    def apply_dl_time(self):
        s, e = self.global_start.get(), self.global_end.get()
        for r in self.dl_rows:
            if s: r["st"].delete(0, 'end'); r["st"].insert(0, s)
            if e: r["et"].delete(0, 'end'); r["et"].insert(0, e)
    def apply_dl_type(self):
        t = self.global_type.get()
        for r in self.dl_rows: r["t"].set(t)
        
    def export_dl(self):
        try:
            data = [{"Name": r["n"], "Reg.No": r["r"], "Date": r["d"].get(), "Start": r["st"].get(), "End": r["et"].get(), "Type": r["t"].get(), "Signature": ""} for r in self.dl_rows]
            filename = f"Astitwam_DL_Sheet_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
            pd.DataFrame(data).to_excel(filename, index=False)
            messagebox.showinfo("Success", f"DL Sheet exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to Excel.\nMake sure the file isn't already open.\n\nError: {e}")

if __name__ == "__main__":
    app = AstitwamApp()
    app.mainloop()
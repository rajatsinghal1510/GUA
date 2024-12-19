import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import os
import json
import bcrypt
from PIL import Image, ImageTk
import random

GRID_SIZE = 8  # Defines an 8x8 grid
DATA_FILE = "cued_click_points.json"  # file were cued click points are saved

class CuedClickPointsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cued Click Points System")

        self.selected_points = []  # Store the clicked points (row, col)
        self.max_points = 3  # Number of click points
        self.mode = None  # Current mode 'register' or 'login'
        self.username = None  # Username for the current session
        self.image_path = None  # Path to the currently loaded imageṇṇ

        # Load existing data
        self.load_data()

        # Create canvas for displaying the image
        self.canvas = tk.Canvas(root, width=500, height=500)
        self.canvas.pack()

        # Draw the grid on the image
        self.canvas.bind("<Button-1>", self.on_click)

        # Add buttons for registration and login
        self.button_frame = tk.Frame(root)
        self.button_frame.pack()
        self.register_button = tk.Button(self.button_frame, text="Register", command=self.register_mode)
        self.register_button.pack(side=tk.LEFT, padx=5)
        self.login_button = tk.Button(self.button_frame, text="Login", command=self.login_mode)
        self.login_button.pack(side=tk.LEFT, padx=5)
        self.upload_button = tk.Button(self.button_frame, text="Upload Image", command=self.upload_image)
        self.upload_button.pack(side=tk.LEFT, padx=5)

    def load_data(self):
        """Load registered points data from the JSON file."""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def save_data(self):
        """Save registered points data to the JSON file."""
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f)

    def upload_image(self):
        """Allow the user to upload a custom image."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png")]
        )
        if file_path:
            self.image_path = file_path
            self.reset()

    def load_image(self):
        """Load and display the image on the canvas."""
        if not self.image_path:
            messagebox.showerror("Error", "No image found , pls load an image")
            return
        try:
            image = Image.open(self.image_path)
            image = image.resize((500, 500), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.draw_grid()
        except FileNotFoundError:
            messagebox.showerror("Error", f"Image file not found: {self.image_path}")

    def draw_grid(self):
        """Draw an 8x8 grid over the image."""
        self.canvas.delete("grid")
        cell_width = 500 // GRID_SIZE
        cell_height = 500 // GRID_SIZE
        for i in range(1, GRID_SIZE):
            # Draw vertical lines
            self.canvas.create_line(i * cell_width, 0, i * cell_width, 500, fill="black", tags="grid")
            # Draw horizontal lines
            self.canvas.create_line(0, i * cell_height, 500, i * cell_height, fill="black", tags="grid")

    def on_click(self, event):
        """Handle mouse click events on the canvas."""
        if len(self.selected_points) < self.max_points:
            row = event.y // (500 // GRID_SIZE)
            col = event.x // (500 // GRID_SIZE)
            if (row, col) not in self.selected_points:
                self.selected_points.append((row, col))
                self.highlight_cell(row, col)

        if len(self.selected_points) == self.max_points:
            if self.mode == "register":
                self.save_points()
            elif self.mode == "login":
                self.verify_login()

    def highlight_cell(self, row, col):
        """Highlight the selected cell on the grid."""
        cell_width = 500 // GRID_SIZE
        cell_height = 500 // GRID_SIZE
        x1 = col * cell_width
        y1 = row * cell_height
        x2 = x1 + cell_width
        y2 = y1 + cell_height
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)

    def register_mode(self):
        """Enable registration mode."""
        self.mode = "register"
        self.reset()

        # Asks the user whether to upload an image or use a random one
        choice = messagebox.askyesno("Image Choice", "Do you want to upload an image? (Yes: image of your choice, No: random image)")
        if choice:
            self.upload_image()
        else:
            self.image_path = self.get_random_image()

        if not self.image_path:
            messagebox.showerror("Error", "image not available")
            self.mode = None
            return

        self.username = simpledialog.askstring("Input", "Enter a username:")
        if not self.username:
            messagebox.showerror("Error", "Username cannot be empty.")
            self.mode = None
            return

        if self.username in self.data:
            messagebox.showerror("Error", "Username already exists. Please choose another username.")
            self.mode = None
            return

        password = simpledialog.askstring("Input", "Enter a password:", show="*")
        if not password:
            messagebox.showerror("Error", "Password cannot be empty.")
            self.mode = None
            return

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Initialize user data
        self.data[self.username] = {"password": hashed_password, "points": [], "image_path": self.image_path}
        messagebox.showinfo("Info", "Now select 3 points on the image.")
        self.load_image()

    def get_random_image(self):
        """Fetch a random image from a predefined folder."""
        folder = "images"  # directs to the image folder where all the random images are stored
        if not os.path.exists(folder):
            os.makedirs(folder)
        image_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith((".jpg", ".jpeg", ".png"))]
        if image_files:
            return random.choice(image_files)
        return None

    def save_points(self):
        """Save the selected points for registration."""
        if self.mode != "register":
            return

        if len(self.selected_points) != self.max_points:
            messagebox.showerror("Error", "You must select exactly 3 points.")
            return

        self.data[self.username]["points"] = self.selected_points
        self.save_data()
        messagebox.showinfo("Success", "Registration complete!")
        self.reset()

    def login_mode(self):
        """Enable login mode."""
        self.mode = "login"
        self.reset()
        self.username = simpledialog.askstring("Input", "Enter your username:")
        if not self.username:
            messagebox.showerror("Error", "Username cannot be empty.")
            self.mode = None
            return

        if self.username not in self.data:
            messagebox.showerror("Error", "Username not found. Please register first.")
            self.mode = None
            return

        password = simpledialog.askstring("Input", "Enter your password:", show="*")
        if not self.verify_password(self.username, password):
            messagebox.showerror("Error", "Incorrect password.")
            self.mode = None
            return

        self.image_path = self.data[self.username].get("image_path")
        if not self.image_path or not os.path.exists(self.image_path):
            messagebox.showerror("Error", "Image used for registration is not found.")
            self.mode = None
            return

        self.load_image()
        messagebox.showinfo("Info", "Password verified. Now select 3 points on the image.")

    def verify_password(self, username, password):
        """Verify the entered password against the stored hash."""
        hashed_password = self.data[username]["password"]
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

    def verify_login(self):
        """Verify the selected points for login."""
        if self.username in self.data and self.selected_points == self.data[self.username]["points"]:
            messagebox.showinfo("Success", "Login successful!")
        else:
            messagebox.showerror("Error", "Invalid points. Login failed.")
        self.reset()

    def reset(self):
        """Reset the application state for a new registration or login."""
        self.selected_points = []
        self.canvas.delete("all")
        if self.image_path:
            self.load_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = CuedClickPointsApp(root)
    root.mainloop()

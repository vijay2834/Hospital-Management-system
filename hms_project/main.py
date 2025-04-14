import customtkinter as ctk
from custom.login import LoginWindow  # Import the login window to handle user authentication
from utils import connect_to_database  # Import the database connection utility
from tkinter import messagebox
from PIL import Image

# Function to create the required tables for the HMS system
def create_tables():
    """
    Creates the necessary tables for the Hospital Management System (HMS).
    Tables include users, prescriptions, medicines, and orders.
    """
    queries = {
        "users": """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT NOT NULL AUTO_INCREMENT,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                user_type ENUM('patient', 'admin', 'pharmacist') NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'inactive',
                date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id)
            );
        """,
        "prescriptions": """
            CREATE TABLE IF NOT EXISTS prescriptions (
                prescription_id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                prescription_details TEXT NOT NULL,
                date_prescribed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (prescription_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
        """,
        "medicines": """
            CREATE TABLE IF NOT EXISTS medicines (
                medicine_id INT NOT NULL AUTO_INCREMENT,
                medicine_name VARCHAR(100) NOT NULL,
                description TEXT,
                stock INT NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                PRIMARY KEY (medicine_id)
            );
        """,
        "orders": """
            CREATE TABLE IF NOT EXISTS orders (
                order_id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                prescription_id INT NOT NULL,
                medicine_id INT NOT NULL,
                quantity INT NOT NULL,
                total_price DECIMAL(10, 2) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                date_ordered TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (order_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id) ON DELETE CASCADE,
                FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id) ON DELETE CASCADE
            );
        """
    }

    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        for table_name, query in queries.items():
            cursor.execute(query)
        conn.commit()
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        conn.close()


# Function to center any window
def center_window(window, width=800, height=600):
    """Centers a given window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


# Initialize the CustomTkinter application with a landing page
class HospitalManagementApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Management System")
        self.geometry("800x600")
        center_window(self)  # Center the main application window

        # Start with the landing page
        self.show_landing_page()

    def show_landing_page(self):
        """Display the landing page."""
        self.clear_window()
        landing_page = LandingPage(master=self)
        landing_page.pack(expand=True, fill="both")

    def show_login_window(self):
        """Display the login window."""
        self.clear_window()
        login_window = LoginWindow(master=self)
        login_window.pack(expand=True, fill="both")

    def clear_window(self):
        """Clear all widgets from the window."""
        for widget in self.winfo_children():
            widget.destroy()


# Landing Page
class LandingPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(fg_color="white")

        # Background Image
        background_image_path = "static/icons/landing_page_bg.jpg"
        pil_image = Image.open(background_image_path).resize((800, 600))
        self.background_image = ctk.CTkImage(light_image=pil_image, size=(800, 600))
        
        # Background Label
        self.bg_label = ctk.CTkLabel(self, image=self.background_image, text="")
        self.bg_label.place(relwidth=1, relheight=1)
       
        # Get Started Button
        self.get_started_button = ctk.CTkButton(
            self,
            text="Get Started",
            command=self.open_login_window,
            width=200,
            height=50,
            corner_radius=10,
            fg_color="#a852b7",
            hover_color="#a892b9",
            bg_color='#d099da',
            font=("Arial", 14)
        )

        # Use exact coordinates for placement
        self.get_started_button.place(x=40, y=485)  

    def open_login_window(self):
        """Open the login window."""
        self.master.show_login_window()


# Main function to start the application
def main():
    # Create necessary tables
    create_tables()

    # Start the application
    app = HospitalManagementApp()
    app.mainloop()


if __name__ == "__main__":
    main()

import customtkinter as ctk
from tkinter import messagebox, filedialog
from custom.navigation_frame_pharmacist import NavigationFramePharmacist
from utils import connect_to_database
from datetime import datetime
from PIL import Image, ImageTk
import mysql.connector
import os

import tkinter.ttk as ttk

import tkinter as tk
from CTkMessagebox import CTkMessagebox

# Function to center any window on the screen
def center_window(window, width=900, height=600):
    """Centers a given window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


class PharmacistDashboard(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.title("Hospital Management System - Pharmacist Dashboard")
        self.geometry("900x600")
        center_window(self)  # Center the main dashboard window

        # Configure layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initialize navigation and frames, pass sign-out command to navigation frame
        self.navigation_frame = NavigationFramePharmacist(master=self, signout_command=self.sign_out)
        self.navigation_frame.grid(row=0, column=0, sticky="ns")

        self.home_frame = HomeFrame(master=self)
        self.manage_prescriptions_frame = ManagePrescriptionsFrame(master=self, user_id=user_id)
        self.view_orders_frame = ViewOrdersFrame(master=self, user_id=user_id)

        # Display the default frame (Home)
        self.show_frame("home")

    def show_frame(self, frame_name):
        """Display the selected frame using grid."""
        # Hide all frames
        self.home_frame.grid_forget()
        self.manage_prescriptions_frame.grid_forget()
        self.view_orders_frame.grid_forget()

        # Show the selected frame
        if frame_name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "manage_prescriptions":
            self.manage_prescriptions_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "view_orders":
            self.view_orders_frame.grid(row=0, column=1, sticky="nsew")

    def sign_out(self):
        """Handle the sign-out process and return to the login window."""
        confirm = messagebox.askyesno("Sign Out", "Are you sure you want to sign out?")
        if confirm:
            self.destroy()  # Close the dashboard window
            self.show_login_window()  # Show the login window

    def show_login_window(self):
        """Reopen the login window after signing out."""
        from custom.login import LoginWindow
        root = ctk.CTk()  # Create a new Tkinter root
        root.geometry("800x600") 
        center_window(root, width=800, height=600) 
        login_window = LoginWindow(root)
        login_window.pack(fill="both", expand=True)
        root.mainloop()


class HomeFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="lightgrey")

        # Create an inner frame for content organization
        self.inner_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=30, pady=20)

        # Title Section
        self.title_frame = ctk.CTkFrame(self.inner_frame, fg_color="#f1f1f1", corner_radius=15)
        self.title_frame.grid(row=0, column=0, columnspan=2, pady=(10, 20), padx=20, sticky="ew")
        self.title_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="Welcome to the Pharmacist Dashboard!",
            font=("Arial", 22, "bold"),
            text_color="#1a73e8",
            anchor="center"
        )
        self.title_label.grid(row=0, column=0, pady=15, padx=10)

        # Description Section
        self.description_frame = ctk.CTkFrame(self.inner_frame, fg_color="#ffffff", corner_radius=15)
        self.description_frame.grid(row=1, column=0, pady=(10, 20), padx=20, sticky="nsew")
        self.description_frame.grid_columnconfigure(0, weight=1)  # Center horizontally
        self.description_frame.grid_rowconfigure(0, weight=1)  # Center vertically

        self.description_label = ctk.CTkLabel(
            self.description_frame,
            text=(
                "Effortlessly manage your pharmacy operations:\n\n"
                "1. View and manage prescriptions to ensure accurate dispensing.\n"
                "2. Process and track orders efficiently.\n"
                "3. Maintain inventory levels with real-time updates.\n\n"
                "Use the navigation menu on the left to explore these features."
            ),
            font=("Arial", 14),
            justify="center",
            text_color="#444",
            wraplength=600
        )
        self.description_label.grid(row=0, column=0, pady=20, padx=20, sticky="nsew")

        # Adjust column and row weights for centering
        self.inner_frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_rowconfigure(1, weight=1)

        

class ManagePrescriptionsFrame(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.user_id = user_id
        self.configure(fg_color="lightgrey")

        # Inner frame for organization
        self.inner_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=30, pady=20)

        # Title
        self.title_label = ctk.CTkLabel(
            self.inner_frame,
            text="Manage Prescriptions",
            font=("Arial", 20, "bold"),
            text_color="#1a73e8"
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        # Patient Selection Dropdown
        self.user_dropdown_label = ctk.CTkLabel(
            self.inner_frame,
            text="Select a Patient:",
            font=("Arial", 14),
            text_color="#555"
        )
        self.user_dropdown_label.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="e")

        self.user_dropdown = ctk.CTkOptionMenu(
            self.inner_frame,
            values=[],
            command=self.load_user_prescriptions,
            width=200,
            fg_color="#4CAF50",
            button_color="#388E3C"
        )
        self.user_dropdown.grid(row=1, column=1, padx=(10, 20), pady=(10, 10), sticky="w")

        # Scrollable Frame for Prescriptions
        self.prescriptions_frame = ctk.CTkScrollableFrame(
            self.inner_frame,
            width=600,
            height=300,
            fg_color="white",
            corner_radius=15
        )
        self.prescriptions_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="nsew")

        # Grid configuration for responsiveness
        self.inner_frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_columnconfigure(1, weight=1)
        self.inner_frame.grid_rowconfigure(2, weight=1)

        # Load users into the dropdown
        self.load_users()

    def load_users(self):
        """Fetch users from the database and populate the dropdown."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, CONCAT(first_name, ' ', last_name) AS full_name "
                "FROM users WHERE user_type = 'patient'"
            )
            users = cursor.fetchall()
            cursor.close()
            conn.close()

            # Populate dropdown with user names
            user_names = [user[1] for user in users]
            self.user_dropdown.configure(values=user_names)

            # Map user names to IDs
            self.user_mapping = {user[1]: user[0] for user in users}

        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"An error occurred: {err}", icon="error")

    def load_user_prescriptions(self, selected_user):
        """Fetch and display prescriptions for the selected user."""
        user_id = self.user_mapping.get(selected_user)
        if not user_id:
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT prescription_id, prescription_details FROM prescriptions WHERE user_id = %s",
                (user_id,)
            )
            prescriptions = cursor.fetchall()
            cursor.close()
            conn.close()

            # Clear existing widgets in the scrollable frame
            for widget in self.prescriptions_frame.winfo_children():
                widget.destroy()

            # Display prescriptions
            if prescriptions:
                for prescription in prescriptions:
                    # Create a bordered frame for each prescription
                    prescription_frame = ctk.CTkFrame(
                        self.prescriptions_frame,
                        fg_color="#f9f9f9",
                        corner_radius=10
                    )
                    prescription_frame.pack(fill="x", padx=10, pady=5)

                    # Display prescription details
                    prescription_label = ctk.CTkLabel(
                        prescription_frame,
                        text=f"Prescription ID: {prescription['prescription_id']}",
                        font=("Arial", 14),
                        text_color="#333",
                        anchor="w"
                    )
                    prescription_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

                    # Add a "View" button
                    view_button = ctk.CTkButton(
                        prescription_frame,
                        text="View",
                        command=lambda p=prescription: self.view_prescription_image(p),
                        width=80,
                        fg_color="#0052cc",
                        hover_color="#003399"
                    )
                    view_button.grid(row=0, column=1, padx=10, pady=5, sticky="e")
            else:
                no_prescriptions_label = ctk.CTkLabel(
                    self.prescriptions_frame,
                    text="No prescriptions found for this patient.",
                    font=("Arial", 14),
                    text_color="#777"
                )
                no_prescriptions_label.pack(fill="both", expand=True)

        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"An error occurred: {err}", icon="error")

    def view_prescription_image(self, prescription):
        """Display the prescription image."""
        image_path = prescription["prescription_details"]
        if not os.path.exists(image_path):
            CTkMessagebox(title="Error", message="Prescription image not found.", icon="error")
        else:
            self.display_image(image_path)

    def display_image(self, image_path):
        """Show the prescription image in a new window."""
        image_window = ctk.CTkToplevel(self)
        image_window.title("Prescription Image")
        center_window(image_window, width=600, height=600)

        # Load and display the image
        image = Image.open(image_path)
        image.thumbnail((600, 600))
        img = ImageTk.PhotoImage(image)

        label = ctk.CTkLabel(image_window, image=img)
        label.image = img  # Keep a reference to avoid garbage collection
        label.pack(padx=20, pady=20)

        close_button = ctk.CTkButton(
            image_window,
            text="Close",
            command=image_window.destroy,
            width=100,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        close_button.pack(pady=20)



class ViewOrdersFrame(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.user_id = user_id
        self.configure(fg_color="lightgrey")

        # Inner frame for layout organization
        self.inner_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=30, pady=20)

        # Title
        self.title_label = ctk.CTkLabel(
            self.inner_frame,
            text="View and Update Orders",
            font=("Arial", 20, "bold"),
            text_color="#1a73e8"
        )
        self.title_label.grid(row=0, column=0, columnspan=5, pady=(20, 10), sticky="n")

        # Patient Selection Dropdown
        self.user_dropdown_label = ctk.CTkLabel(
            self.inner_frame,
            text="Select a Patient:",
            font=("Arial", 10),
            text_color="#555"
        )
        self.user_dropdown_label.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="e")

        self.user_dropdown = ctk.CTkOptionMenu(
            self.inner_frame,
            values=[],
            command=self.load_user_orders,
            width=200,
            fg_color="#4CAF50",
            button_color="#388E3C"
        )
        self.user_dropdown.grid(row=1, column=1, padx=(10, 20), pady=(10, 10), sticky="w")

        # Table Header
        headers = ["Order ID", "Medicine Name", "Quantity", "Date Ordered", "Status"]
        for col, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                self.inner_frame,
                text=header,
                font=("Arial", 11, "bold"),
                text_color="#333",
                anchor="center"
            )
            header_label.grid(row=2, column=col, padx=5, pady=(10, 5), sticky="ew")

        # Scrollable Frame for Orders
        self.orders_scroll_frame = ctk.CTkScrollableFrame(
            self.inner_frame,
            width=600,
            height=400,
            fg_color="white",
            corner_radius=15
        )
        self.orders_scroll_frame.grid(row=3, column=0, columnspan=5, padx=20, pady=(10, 20), sticky="nsew")

        # Confirm Changes Button
        self.confirm_button = ctk.CTkButton(
            self.inner_frame,
            text="Confirm Changes",
            command=self.confirm_status_changes,
            width=150,
            fg_color="#0052cc",
            hover_color="#003399"
        )
        self.confirm_button.grid(row=4, column=4, padx=(10, 20), pady=(10, 20), sticky="e")

        # Grid configuration for responsiveness
        self.inner_frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_columnconfigure(1, weight=1)
        self.inner_frame.grid_columnconfigure(2, weight=1)
        self.inner_frame.grid_columnconfigure(3, weight=1)
        self.inner_frame.grid_columnconfigure(4, weight=1)
        self.inner_frame.grid_rowconfigure(3, weight=1)

        # Load users into the dropdown
        self.load_users()

    def load_users(self):
        """Fetch users from the database and populate the dropdown."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, CONCAT(first_name, ' ', last_name) AS full_name "
                "FROM users WHERE user_type = 'patient'"
            )
            users = cursor.fetchall()
            cursor.close()
            conn.close()

            # Populate dropdown with user names
            user_names = [user[1] for user in users]
            self.user_dropdown.configure(values=user_names)

            # Map user names to IDs
            self.user_mapping = {user[1]: user[0] for user in users}

        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"An error occurred: {err}", icon="error")

    def load_user_orders(self, selected_user):
        """Fetch and display orders for the selected user."""
        user_id = self.user_mapping.get(selected_user)
        if not user_id:
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT o.order_id, m.medicine_name, o.quantity, o.date_ordered, o.status
                FROM orders o
                JOIN medicines m ON o.medicine_id = m.medicine_id
                WHERE o.user_id = %s
                ORDER BY o.date_ordered DESC
                """,
                (user_id,)
            )
            orders = cursor.fetchall()
            cursor.close()
            conn.close()

            # Clear existing widgets in the scrollable frame
            for widget in self.orders_scroll_frame.winfo_children():
                widget.destroy()

            # Display each order as a row in the table, excluding "Approved" status
            self.order_status_vars = {}  # Store status variables for each order

            has_pending_orders = False
            for row, order in enumerate(orders):
                if order["status"].lower() == "approved":
                    continue  # Skip approved orders

                has_pending_orders = True

                # Order ID
                order_id_label = ctk.CTkLabel(
                    self.orders_scroll_frame,
                    text=str(order["order_id"]),
                    font=("Arial", 12),
                    text_color="#333",
                    anchor="center"
                )
                order_id_label.grid(row=row, column=0, padx=10, pady=5, sticky="ew")

                # Medicine Name
                medicine_label = ctk.CTkLabel(
                    self.orders_scroll_frame,
                    text=order["medicine_name"],
                    font=("Arial", 12),
                    text_color="#333",
                    anchor="center"
                )
                medicine_label.grid(row=row, column=1, padx=10, pady=5, sticky="ew")

                # Quantity
                quantity_label = ctk.CTkLabel(
                    self.orders_scroll_frame,
                    text=str(order["quantity"]),
                    font=("Arial", 12),
                    text_color="#333",
                    anchor="center"
                )
                quantity_label.grid(row=row, column=2, padx=10, pady=5, sticky="ew")

                # Date Ordered
                date_label = ctk.CTkLabel(
                    self.orders_scroll_frame,
                    text=order["date_ordered"].strftime("%Y-%m-%d %H:%M:%S"),
                    font=("Arial", 12),
                    text_color="#333",
                    anchor="center"
                )
                date_label.grid(row=row, column=3, padx=10, pady=5, sticky="ew")

                # Status Dropdown
                status_var = ctk.StringVar(value=order["status"].capitalize())
                status_dropdown = ctk.CTkOptionMenu(
                    self.orders_scroll_frame,
                    variable=status_var,
                    values=["Pending", "Approved","Declined"],
                    width=120,
                    fg_color="#4CAF50",
                    button_color="#388E3C"
                )
                status_dropdown.grid(row=row, column=4, padx=10, pady=5, sticky="ew")

                # Store the status variable for updating later
                self.order_status_vars[order["order_id"]] = status_var

            if not has_pending_orders:
                no_orders_label = ctk.CTkLabel(
                    self.orders_scroll_frame,
                    text="No pending or declined orders found for this patient.",
                    font=("Arial", 14),
                    text_color="#777"
                )
                no_orders_label.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")

        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"An error occurred: {err}", icon="error")

    def confirm_status_changes(self):
        """Confirm and save updated statuses to the database."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            # Track if updates were made
            updates_made = False

            # Update statuses in the database
            for order_id, status_var in self.order_status_vars.items():
                new_status = status_var.get().lower()
                if new_status in ["approved", "declined"]:
                    cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s", (new_status, order_id))
                    updates_made = True

            if updates_made:
                conn.commit()

                # Show success message
                CTkMessagebox(title="Update Success", message="Order statuses have been updated successfully.", icon="info")

                # Refresh the table to show pending orders only
                selected_user = self.user_dropdown.get()
                if selected_user:
                    self.load_user_orders(selected_user)
            else:
                CTkMessagebox(title="No Updates", message="No statuses were changed.", icon="warning")

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"An error occurred: {err}", icon="error")

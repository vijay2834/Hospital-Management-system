import tkinter as tk
import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image
import mysql.connector
from CTkMessagebox import CTkMessagebox
import os
import re
import tkinter.ttk as ttk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils import connect_to_database
from custom.navigation_frame_admin import NavigationFrameAdmin
import plotly.graph_objects as go
import bcrypt  # Add this import for password hashing
# from tkinterhtml import HtmlFrame
# from navigation_frame_admin import NavigationFrameAdmin

def center_window(window, width=900, height=600):
    """Centers a given window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")



class AdminDashboard(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.title("Hospital Management System - Admin Dashboard")
        self.geometry("900x600")
        center_window(self) 

        # Configure layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initialize navigation and frames, pass sign-out command to navigation frame
        self.navigation_frame = NavigationFrameAdmin(master=self, signout_command=self.sign_out)
        self.navigation_frame.grid(row=0, column=0, sticky="ns")

        self.home_frame = HomeFrame(master=self)
        self.user_management_frame = UserManagementFrame(master=self)
        self.inventory_management_frame = InventoryManagementFrame(master=self)
        self.reports_frame = ReportsFrame(master=self)

        # Display the default frame (Home)
        self.show_frame("home")

    def show_frame(self, frame_name):
        """Display the selected frame using grid."""
        # Hide all frames
        self.home_frame.grid_forget()
        self.user_management_frame.grid_forget()
        self.inventory_management_frame.grid_forget()
        self.reports_frame.grid_forget()

        # Show the selected frame
        if frame_name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "user_management":
            self.user_management_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "inventory_management":
            self.inventory_management_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "reports":
            self.reports_frame.grid(row=0, column=1, sticky="nsew")

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

        # Inner frame for central alignment
        self.inner_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=30, pady=20)

        # Title Label
        self.title_label = ctk.CTkLabel(
            self.inner_frame,
            text="Welcome to the Admin Dashboard!",
            font=("Arial", 20, "bold"),
            text_color="#1a73e8"
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="n")

        # Description Label
        self.description_label = ctk.CTkLabel(
            self.inner_frame,
            text=(
                "Here, you can efficiently manage users, monitor inventory, "
                "and generate insightful reports to support operational decisions.\n\n"
                "Use the navigation menu to access features like:\n"
                "- User Management\n"
                "- Inventory Tracking\n"
                "- Activity Reports\n\n"
                "Streamline your operations and make data-driven decisions with ease."
            ),
            font=("Arial", 14),
            justify="center",
            text_color="#555",
            wraplength=600
        )
        self.description_label.grid(row=1, column=0, padx=30, pady=(10, 20), sticky="n")

        # Decorative Separator
        self.separator = ctk.CTkFrame(self.inner_frame, fg_color="#ddd", height=2)
        self.separator.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="ew")

        # Footer Note
        self.footer_label = ctk.CTkLabel(
            self.inner_frame,
            text="Navigate through the features using the left menu.\n"
                 "Stay updated, manage effectively, and lead with insights!",
            font=("Arial", 12, "italic"),
            text_color="#777",
            justify="center"
        )
        self.footer_label.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="s")

        # Configure grid for responsiveness
        self.inner_frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_rowconfigure(1, weight=1)


class UserManagementFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="lightgrey")

        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="User Management",
            font=("Arial", 20, "bold"),
            text_color="#333"
        )
        self.title_label.pack(pady=(20, 10))

        # Buttons for Adding and Deleting Users
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=(10, 10))

        self.add_user_button = ctk.CTkButton(
            self.button_frame,
            text="Add New User",
            command=self.open_add_user_window,
            width=150,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        self.add_user_button.pack(side="left", padx=10)

        self.delete_user_button = ctk.CTkButton(
            self.button_frame,
            text="Delete Selected User",
            command=self.delete_selected_user,
            width=150,
            fg_color="red",
            hover_color="#b22222"
        )
        self.delete_user_button.pack(side="left", padx=10)

        # Treeview for displaying users
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("ID", "First Name", "Last Name", "Email", "Role"),
            show="headings",
            height=15
        )
        self.tree.pack(side="left", fill="both", expand=True)

        # Define column headers
        self.tree.heading("ID", text="ID")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Last Name", text="Last Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Role", text="Role")

        # Adjust column widths
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("First Name", width=120, anchor="center")
        self.tree.column("Last Name", width=120, anchor="center")
        self.tree.column("Email", width=200, anchor="center")
        self.tree.column("Role", width=100, anchor="center")

        # Add a scrollbar
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        # Load users into the table
        self.load_users()

        # Right-click context menu for deleting users
        self.tree.bind("<Button-3>", self.open_context_menu)

    def load_users(self):
        """Fetch user data from the database and display it in the Treeview."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT user_id, first_name, last_name, email, user_type FROM users")
            users = cursor.fetchall()
            cursor.close()
            conn.close()

            # Clear existing rows in the Treeview
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Add users to the Treeview
            for user in users:
                self.tree.insert(
                    "",
                    "end",
                    values=(user["user_id"], user["first_name"], user["last_name"], user["email"], user["user_type"])
                )

        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error fetching users: {err}", icon="error")


    def open_add_user_window(self):
        """Open a new CTk window to add a user."""
        add_window = ctk.CTkToplevel(self)
        add_window.title("Add New User")
        add_window.geometry("400x500")
        center_window(add_window, width=400, height=500) 

        ctk.CTkLabel(add_window, text="First Name:", font=("Arial", 12)).pack(pady=5)
        first_name_entry = ctk.CTkEntry(add_window)
        first_name_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Last Name:", font=("Arial", 12)).pack(pady=5)
        last_name_entry = ctk.CTkEntry(add_window)
        last_name_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Email:", font=("Arial", 12)).pack(pady=5)
        email_entry = ctk.CTkEntry(add_window)
        email_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Password:", font=("Arial", 12)).pack(pady=5)
        password_entry = ctk.CTkEntry(add_window, show="*")
        password_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Role:", font=("Arial", 12)).pack(pady=5)
        role_dropdown = ctk.CTkOptionMenu(add_window, values=["patient", "pharmacist", "admin"])
        role_dropdown.pack(pady=5)

        def validate_email(email):
            """Validate email format."""
            email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            return re.match(email_regex, email) is not None

        def validate_password(password):
            """Validate password strength."""
            return len(password) >= 8 and any(char.isdigit() for char in password) and any(char.isalpha() for char in password)

        def save_user():
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            email = email_entry.get()
            password = password_entry.get()
            role = role_dropdown.get()

            if not (first_name and last_name and email and password and role):
                CTkMessagebox(title="Input Error", message="All fields are required!", icon="warning")
                return

            if not validate_email(email):
                CTkMessagebox(title="Input Error", message="Invalid email format!", icon="warning")
                return

            if not validate_password(password):
                CTkMessagebox(
                    title="Input Error",
                    message="Password must be at least 8 characters long and contain both letters and numbers.",
                    icon="warning"
                )
                return

            try:
                # Hash the password using bcrypt
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                conn = connect_to_database()
                cursor = conn.cursor()
                query = """
                    INSERT INTO users (first_name, last_name, email, password, user_type)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (first_name, last_name, email, hashed_password, role))
                conn.commit()
                cursor.close()
                conn.close()

                self.load_users()
                CTkMessagebox(title="Success", message="User added successfully!", icon="check")
                add_window.destroy()

            except mysql.connector.Error as err:
                CTkMessagebox(title="Database Error", message=f"Error adding user: {err}", icon="error")

        save_button = ctk.CTkButton(add_window, text="Save", command=save_user, fg_color="#4CAF50")
        save_button.pack(pady=20)

    def open_context_menu(self, event):
        """Open a context menu to delete a selected user."""
        row_id = self.tree.identify_row(event.y)
        if row_id:
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label="Delete", command=lambda: self.delete_user(row_id))
            menu.post(event.x_root, event.y_root)

    def delete_selected_user(self):
        """Delete the currently selected user."""
        selected_item = self.tree.selection()
        if not selected_item:
            CTkMessagebox(title="Selection Error", message="No user selected!", icon="warning")
            return

        row_id = selected_item[0]
        self.delete_user(row_id)

    def delete_user(self, row_id):
        """Delete a user from the database."""
        values = self.tree.item(row_id, "values")
        user_id = values[0]

        confirm = CTkMessagebox(
            title="Delete Confirmation",
            message="Are you sure you want to delete this user?",
            icon="question",
            option_1="Yes",
            option_2="No",
        ).get()
        if confirm != "Yes":
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()

            self.load_users()
            CTkMessagebox(title="Deleted", message="User deleted successfully.", icon="info")

        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error deleting user: {err}", icon="error")

class InventoryManagementFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="lightgrey")

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Inventory Management", font=("Arial", 20, "bold"), text_color="#333"
        )
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="n")

        # Load Inventory Button
        self.load_button = ctk.CTkButton(
            self, text="Load Inventory", command=self.load_inventory, width=150
        )
        self.load_button.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        # Add Medicine Button
        self.add_medicine_button = ctk.CTkButton(
            self, text="Add Medicine", command=self.open_add_medicine_window, width=150
        )
        self.add_medicine_button.grid(row=1, column=1, padx=20, pady=10, sticky="e")

        # Scrollable Frame for Inventory List
        self.inventory_list_frame = ctk.CTkScrollableFrame(
            self, width=600, height=430, fg_color="white", corner_radius=10
        )
        self.inventory_list_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        # Configure layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Dictionary to map medicine IDs to widgets for easy updates
        self.medicine_widgets = {}

    def load_inventory(self):
        """Fetch current medicine inventory from the database and display it."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT medicine_id, medicine_name, stock, price FROM medicines")
            inventory = cursor.fetchall()
            cursor.close()
            conn.close()

            # Clear existing data
            for widget in self.inventory_list_frame.winfo_children():
                widget.destroy()

            # Display inventory
            for item in inventory:
                self.display_inventory_row(item)

        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error fetching inventory: {err}", icon="error")

    def display_inventory_row(self, item):
        """Display a single inventory item."""
        medicine_id = item["medicine_id"]

        # Medicine Information Label
        medicine_info = f"ID: {medicine_id} | Name: {item['medicine_name']} | Stock: {item['stock']} | Price: ${item['price']:.2f}"
        medicine_label = ctk.CTkLabel(
            self.inventory_list_frame, text=medicine_info, font=("Arial", 12), fg_color="lightgrey", corner_radius=5
        )
        medicine_label.grid(row=medicine_id, column=0, padx=5, pady=5, sticky="w")

        # Update Button
        update_button = ctk.CTkButton(
            self.inventory_list_frame, text="Update", width=60, command=lambda: self.open_update_medicine_window(item)
        )
        update_button.grid(row=medicine_id, column=1, padx=5, pady=5)

        # Delete Button
        delete_button = ctk.CTkButton(
            self.inventory_list_frame,
            text="Delete",
            fg_color="red",
            width=60,
            command=lambda: self.delete_medicine(medicine_id),
        )
        delete_button.grid(row=medicine_id, column=2, padx=5, pady=5)

        # Save widgets to dictionary
        self.medicine_widgets[medicine_id] = (medicine_label, update_button, delete_button)

    def open_add_medicine_window(self):
        """Open a new CTk window to add a medicine."""
        add_window = ctk.CTkToplevel(self)
        add_window.title("Add New Medicine")
        add_window.geometry("400x350")
        center_window(add_window, width=400, height=350)

        # Input fields for adding a new medicine
        ctk.CTkLabel(add_window, text="Medicine Name:", font=("Arial", 12)).pack(pady=5)
        medicine_name_entry = ctk.CTkEntry(add_window, placeholder_text="Enter medicine name")
        medicine_name_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Stock Quantity:", font=("Arial", 12)).pack(pady=5)
        stock_entry = ctk.CTkEntry(add_window, placeholder_text="Enter stock quantity")
        stock_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Price per Unit:", font=("Arial", 12)).pack(pady=5)
        price_entry = ctk.CTkEntry(add_window, placeholder_text="Enter price per unit")
        price_entry.pack(pady=5)

        def save_medicine():
            medicine_name = medicine_name_entry.get()
            stock = stock_entry.get()
            price = price_entry.get()

            if not (medicine_name and stock.isdigit() and price.replace('.', '', 1).isdigit()):
                CTkMessagebox(title="Input Error", message="Please fill all fields correctly!", icon="warning")
                return

            try:
                conn = connect_to_database()
                cursor = conn.cursor(dictionary=True)  # Ensure DictCursor is used
                query = "INSERT INTO medicines (medicine_name, stock, price) VALUES (%s, %s, %s)"
                cursor.execute(query, (medicine_name, int(stock), float(price)))
                conn.commit()

                # Fetch the new medicine details to display
                new_medicine_id = cursor.lastrowid
                cursor.execute("SELECT * FROM medicines WHERE medicine_id = %s", (new_medicine_id,))
                new_medicine = cursor.fetchone()  # Fetch as dictionary
                cursor.close()
                conn.close()

                self.display_inventory_row(new_medicine)  # Pass the dictionary to display
                CTkMessagebox(title="Success", message="Medicine added successfully!", icon="check")
                add_window.destroy()

            except mysql.connector.Error as err:
                CTkMessagebox(title="Database Error", message=f"Error adding medicine: {err}", icon="error")

        # Save button
        save_button = ctk.CTkButton(add_window, text="Save", command=save_medicine, fg_color="#4CAF50")
        save_button.pack(pady=20)

    def open_update_medicine_window(self, item):
        """Open a new CTk window to update medicine details."""
        update_window = ctk.CTkToplevel(self)
        update_window.title("Update Medicine")
        update_window.geometry("400x300")
        center_window(update_window, width=400, height=300)

        ctk.CTkLabel(update_window, text="Medicine Name:", font=("Arial", 12)).pack(pady=5)
        medicine_name_entry = ctk.CTkEntry(update_window, textvariable=ctk.StringVar(value=item["medicine_name"]))
        medicine_name_entry.pack(pady=5)

        ctk.CTkLabel(update_window, text="Stock Quantity:", font=("Arial", 12)).pack(pady=5)
        stock_entry = ctk.CTkEntry(update_window, textvariable=ctk.StringVar(value=str(item["stock"])))
        stock_entry.pack(pady=5)

        ctk.CTkLabel(update_window, text="Price per Unit:", font=("Arial", 12)).pack(pady=5)
        price_entry = ctk.CTkEntry(update_window, textvariable=ctk.StringVar(value=str(item["price"])))
        price_entry.pack(pady=5)

        def save_changes():
            medicine_name = medicine_name_entry.get()
            stock = stock_entry.get()
            price = price_entry.get()

            if not (medicine_name and stock.isdigit() and price.replace('.', '', 1).isdigit()):
                CTkMessagebox(title="Input Error", message="Please fill all fields correctly!", icon="warning")
                return

            try:
                conn = connect_to_database()
                cursor = conn.cursor()
                query = """
                    UPDATE medicines 
                    SET medicine_name = %s, stock = %s, price = %s
                    WHERE medicine_id = %s
                """
                cursor.execute(query, (medicine_name, int(stock), float(price), item["medicine_id"]))
                conn.commit()
                cursor.close()
                conn.close()

                item.update({"medicine_name": medicine_name, "stock": int(stock), "price": float(price)})
                self.update_inventory_row(item)
                CTkMessagebox(title="Success", message="Medicine updated successfully!", icon="info")
                update_window.destroy()

            except mysql.connector.Error as err:
                CTkMessagebox(title="Database Error", message=f"Error updating medicine: {err}", icon="error")

        save_button = ctk.CTkButton(update_window, text="Save Changes", command=save_changes, fg_color="#4CAF50")
        save_button.pack(pady=20)

    def update_inventory_row(self, item):
        """Update UI for a single medicine."""
        medicine_id = item["medicine_id"]
        medicine_info = f"ID: {medicine_id} | Name: {item['medicine_name']} | Stock: {item['stock']} | Price: ${item['price']:.2f}"

        medicine_label, update_button, delete_button = self.medicine_widgets[medicine_id]
        medicine_label.configure(text=medicine_info)

    def delete_medicine(self, medicine_id):
        """Delete a medicine."""
        confirm = CTkMessagebox(
            title="Delete Confirmation",
            message="Are you sure you want to delete this medicine?",
            icon="question",
            option_1="Yes",
            option_2="No",
        ).get()

        if confirm != "Yes":
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM medicines WHERE medicine_id = %s", (medicine_id,))
            conn.commit()
            cursor.close()
            conn.close()

            medicine_label, update_button, delete_button = self.medicine_widgets.pop(medicine_id)
            medicine_label.destroy()
            update_button.destroy()
            delete_button.destroy()

            CTkMessagebox(title="Deleted", message="Medicine deleted successfully.", icon="info")

        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error deleting medicine: {err}", icon="error")




class ReportsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="lightgrey")

        # Title for the Reports Section
        self.title_label = ctk.CTkLabel(
            self, text="Reports - Last 3 Months", font=("Arial", 18, "bold"), text_color="#1a73e8"
        )
        self.title_label.pack(padx=20, pady=20)

        # Dropdown to select the type of report
        self.report_type_var = ctk.StringVar(value="Select Report Type")
        self.report_dropdown = ctk.CTkOptionMenu(
            self,
            variable=self.report_type_var,
            values=["Orders Over Time", "Products Sold", "Revenue Summary"],
            fg_color="#4CAF50",
            button_color="#388E3C"
        )
        self.report_dropdown.pack(padx=10, pady=10)

        # Generate Reports Button
        self.generate_button = ctk.CTkButton(
            self,
            text="Generate Report",
            command=self.generate_reports,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            width=200,
        )
        self.generate_button.pack(padx=10, pady=20)

        # Frame for Plots
        self.plot_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10, width=600, height=400)
        self.plot_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def generate_reports(self):
        """Fetches data for reports and displays the selected plot."""
        report_type = self.report_type_var.get()
        if report_type == "Select Report Type":
            CTkMessagebox(
                title="Select Report",
                message="Please select a report type from the dropdown.",
                icon="warning"
            )
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            # Date 3 months ago
            three_months_ago = datetime.now() - timedelta(days=90)

            if report_type == "Orders Over Time":
                cursor.execute(
                    "SELECT DATE_FORMAT(date_ordered, '%Y-%m') AS month, COUNT(order_id) AS orders_count "
                    "FROM orders WHERE date_ordered >= %s GROUP BY month ORDER BY month ASC",
                    (three_months_ago,)
                )
                orders_data = cursor.fetchall()
                if orders_data:
                    self.plot_orders(orders_data)
                else:
                    self.display_empty_message("No orders placed in the last 3 months.")

            elif report_type == "Products Sold":
                cursor.execute(
                    "SELECT medicines.medicine_name, SUM(orders.quantity) AS total_sold "
                    "FROM orders "
                    "JOIN medicines ON orders.medicine_id = medicines.medicine_id "
                    "WHERE date_ordered >= %s "
                    "GROUP BY medicines.medicine_name ORDER BY total_sold DESC",
                    (three_months_ago,)
                )
                products_sold_data = cursor.fetchall()
                if products_sold_data:
                    self.plot_products_sold(products_sold_data)
                else:
                    self.display_empty_message("No products were sold in the last 3 months.")

            elif report_type == "Revenue Summary":
                cursor.execute(
                    "SELECT SUM(total_price) AS total_revenue FROM orders WHERE date_ordered >= %s",
                    (three_months_ago,)
                )
                total_revenue = cursor.fetchone()[0] or 0
                self.display_total_revenue(total_revenue)

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            CTkMessagebox(
                title="Database Error",
                message=f"An error occurred: {err}",
                icon="error"
            )

    def plot_orders(self, orders_data):
        """Display the number of orders placed in the last 3 months as a bar plot."""
        months = [data[0] for data in orders_data]
        orders_count = [data[1] for data in orders_data]

        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(months, orders_count, color="skyblue")
        ax.set_title("Orders Placed in the Last 3 Months", fontsize=14)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Number of Orders", fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        self.display_plot(fig)

    def plot_products_sold(self, products_sold_data):
        """Display the total products sold per medicine in the last 3 months as a vertical bar plot."""
        medicines = [data[0] for data in products_sold_data]
        total_sold = [data[1] for data in products_sold_data]

        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(medicines, total_sold, color="salmon")
        ax.set_title("Total Products Sold per Medicine", fontsize=14)
        ax.set_xlabel("Medicine", fontsize=12)
        ax.set_ylabel("Total Sold", fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        self.display_plot(fig)

    def display_total_revenue(self, total_revenue):
        """Display the total revenue generated in the last 3 months."""
        self.clear_plot_frame()
        if total_revenue > 0:
            revenue_label = ctk.CTkLabel(
                self.plot_frame,
                text=f"Total Revenue Generated in Last 3 Months: ${total_revenue:.2f}",
                font=("Arial", 16, "bold"),
                text_color="black"
            )
            revenue_label.pack(pady=(100, 20))
        else:
            self.display_empty_message("No revenue generated in the last 3 months.")

    def display_plot(self, fig):
        """Display a matplotlib figure in the plot_frame."""
        self.clear_plot_frame()
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def display_empty_message(self, message):
        """Display a message when no data is available for the selected report."""
        self.clear_plot_frame()
        empty_label = ctk.CTkLabel(
            self.plot_frame,
            text=message,
            font=("Arial", 14, "bold"),
            text_color="#777"
        )
        empty_label.pack(expand=True)

    def clear_plot_frame(self):
        """Clear all widgets in the plot frame."""
        for widget in self.plot_frame.winfo_children():
            widget.destroy()


# Main application execution
if __name__ == "__main__":
    app = AdminDashboard(user_id=1)  # Example user ID
    app.mainloop()

import customtkinter as ctk
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkScrollableFrame, CTkToplevel
from CTkMessagebox import CTkMessagebox
from CTkSpinbox import CTkSpinbox
from datetime import datetime
from tkinter import messagebox, filedialog, Toplevel
from PIL import Image, ImageTk
import mysql.connector
import os
from custom.navigation_frame_patient import NavigationFrame
from utils import connect_to_database
# from navigation_frame_patient import NavigationFrame
import time


def center_window(window, width=900, height=600):
    """Centers a given window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

class PatientDashboard(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id  # Store user_id in the dashboard instance
        self.title("Hospital Management System - Patient Dashboard")
        self.geometry("900x600")
        center_window(self)  # Center the main dashboard window


        # Configure layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initialize navigation and frames, pass sign-out command to navigation frame
        self.navigation_frame = NavigationFrame(master=self, signout_command=self.sign_out)
        self.navigation_frame.grid(row=0, column=0, sticky="ns")

        # Initialize frames, passing user_id to each
        self.home_frame = HomeFrame(master=self, user_id=self.user_id)
        self.upload_prescription_frame = UploadPrescriptionFrame(master=self, user_id=self.user_id)
        self.place_order_frame = PlaceOrderFrame(master=self, user_id=self.user_id)
        self.track_order_frame = TrackOrderFrame(master=self, user_id=self.user_id)

        # Display the default frame (Home)
        self.show_frame("home")

    def show_frame(self, frame_name):
        """Display the selected frame using grid."""
        # Hide all frames
        self.home_frame.grid_forget()
        self.upload_prescription_frame.grid_forget()
        self.place_order_frame.grid_forget()
        self.track_order_frame.grid_forget()

        # Show the selected frame
        if frame_name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "upload":
            self.upload_prescription_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "order":
            self.place_order_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "track":
            self.track_order_frame.grid(row=0, column=1, sticky="nsew")

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




class HomeFrame(CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.user_id = user_id
        self.configure(fg_color="lightgrey")

        # Create an inner frame for content organization
        self.inner_frame = CTkFrame(self, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=30, pady=20)

        # Title
        self.title_label = CTkLabel(
            self.inner_frame,
            text="Welcome to the Patient Dashboard!",
            font=("Arial", 20, "bold"),
            text_color="#333"
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        # Description
        self.description_label = CTkLabel(
            self.inner_frame,
            text=(
                "Here, you can upload prescriptions, place medication orders, "
                "and track your order status.\n\n"
                "Use the navigation menu to explore these features.\n\n"
                "Click below to view your previous prescriptions."
            ),
            font=("Arial", 14),
            justify="center",
            text_color="black",
            wraplength=500
        )
        self.description_label.grid(row=1, column=0, columnspan=2, padx=20, pady=(10, 20))

        # View Prescriptions Button
        self.view_prescriptions_button = CTkButton(
            self.inner_frame,
            text="View Previous Prescriptions",
            command=self.display_prescriptions,
            width=220,
            height=40,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        self.view_prescriptions_button.grid(row=2, column=0, columnspan=2, pady=(10, 20))

        # Create a scrollable frame for displaying the prescription table
        self.prescriptions_frame = CTkScrollableFrame(
            self.inner_frame,
            width=450,
            height=250,
            fg_color="white",
            corner_radius=15
        )
        self.prescriptions_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="nsew")
        self.prescriptions_frame.grid_remove()  # Initially hidden

        # Configure grid for responsiveness
        self.inner_frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_rowconfigure((0, 1, 2), weight=1)

    def display_prescriptions(self):
        """Fetch and display previous prescriptions in the scrollable frame."""
        prescriptions = self.fetch_prescriptions_from_db()

        # Adjust layout to minimize upper content
        self.title_label.grid_configure(pady=(5, 5))
        self.description_label.grid_configure(pady=(5, 5))
        self.view_prescriptions_button.grid_configure(pady=(5, 10))

        # Clear any existing content in the frame
        for widget in self.prescriptions_frame.winfo_children():
            widget.destroy()

        if prescriptions:
            # Add headers
            headers = ["Date", "Details", "View Image"]
            for col, header in enumerate(headers):
                header_label = CTkLabel(
                    self.prescriptions_frame,
                    text=header,
                    font=("Arial", 12, "bold"),
                    text_color="#333"
                )
                header_label.grid(row=0, column=col, padx=10, pady=5, sticky="nsew")

            # Add prescription rows
            for i, prescription in enumerate(prescriptions, start=1):
                date_label = CTkLabel(
                    self.prescriptions_frame,
                    text=prescription["date_prescribed"],
                    font=("Arial", 12),
                    text_color="#555"
                )
                date_label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

                # Display the image path as the prescription detail
                details_label = CTkLabel(
                    self.prescriptions_frame,
                    text=os.path.basename(prescription["prescription_details"]),
                    font=("Arial", 12),
                    text_color="#555",
                    wraplength=250,
                    justify="left"
                )
                details_label.grid(row=i, column=1, padx=10, pady=5, sticky="w")

                view_image_button = CTkButton(
                    self.prescriptions_frame,
                    text="View Image",
                    command=lambda p=prescription: self.view_prescription_image(p["prescription_details"]),
                    width=100,
                    fg_color="#0052cc",
                    hover_color="#003399",
                    corner_radius=8
                )
                view_image_button.grid(row=i, column=2, padx=10, pady=5)

            self.prescriptions_frame.grid()  # Show the prescriptions frame
        else:
            CTkMessagebox(title="Previous Prescriptions", message="No prescriptions available yet.", icon="info")

    def fetch_prescriptions_from_db(self):
        """Fetches previous prescriptions for the user from the database."""
        prescriptions = []
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            query = (
                "SELECT date_prescribed, prescription_details "
                "FROM prescriptions WHERE user_id = %s ORDER BY date_prescribed DESC"
            )
            cursor.execute(query, (self.user_id,))
            prescriptions = cursor.fetchall()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"An error occurred while fetching prescriptions: {err}", icon="error")
        return prescriptions

    def view_prescription_image(self, image_path):
        """Display a prescription image in a new window."""
        if not os.path.exists(image_path):
            CTkMessagebox(title="Error", message="Prescription image not found.", icon="error")
            return

        prescription_image_window = CTkToplevel(self)
        prescription_image_window.title("Prescription Image")
        prescription_image_window.geometry("600x600")
        center_window(prescription_image_window, width=600, height=600) 

        image = Image.open(image_path)
        resized_image = image.resize((500, 500))
        img = ImageTk.PhotoImage(resized_image)

        image_label = CTkLabel(prescription_image_window, image=img)
        image_label.image = img  # Prevent image garbage collection
        image_label.pack(pady=20, padx=20, expand=True)

        close_button = CTkButton(
            prescription_image_window,
            text="Close",
            command=prescription_image_window.destroy,
            width=100,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        close_button.pack(pady=20)


class UploadPrescriptionFrame(CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.user_id = user_id
        self.configure(fg_color="lightgrey")

        # Create an inner frame for layout organization
        self.inner_frame = CTkFrame(self, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=30, pady=20)

        # Title
        self.title_label = CTkLabel(
            self.inner_frame,
            text="Upload Prescription",
            font=("Arial", 20, "bold"),
            text_color="#333"
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        # Instructions
        self.instructions_label = CTkLabel(
            self.inner_frame,
            text="Select a scanned image of your prescription and upload it.",
            font=("Arial", 14),
            text_color="black",
            wraplength=500,
            justify="center"
        )
        self.instructions_label.grid(row=1, column=0, columnspan=2, padx=20, pady=(5, 20))

        # Select Prescription Button
        self.browse_button = CTkButton(
            self.inner_frame,
            text="Select Prescription Image",
            command=self.browse_image,
            width=220,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        self.browse_button.grid(row=2, column=0, columnspan=2, pady=(10, 10))

        # Selected file label
        self.file_label = CTkLabel(
            self.inner_frame,
            text="No file selected",
            font=("Arial", 12),
            text_color="grey"
        )
        self.file_label.grid(row=3, column=0, columnspan=2, pady=(5, 20))

        # Upload Prescription Button
        self.upload_button = CTkButton(
            self.inner_frame,
            text="Upload Prescription",
            command=self.upload_prescription,
            width=220,
            fg_color="#0052cc",
            hover_color="#003399"
        )
        self.upload_button.grid(row=4, column=0, columnspan=2, pady=(10, 20))

        # Prescription Table Header
        self.table_header = CTkLabel(
            self.inner_frame,
            text="Today's Uploaded Prescriptions",
            font=("Arial", 16, "bold"),
            text_color="#333"
        )
        self.table_header.grid(row=5, column=0, columnspan=2, pady=(20, 10))

        # Scrollable Frame for Prescription Table
        self.prescriptions_frame = CTkScrollableFrame(
            self.inner_frame,
            width=500,
            height=300,
            fg_color="white",
            corner_radius=15
        )
        self.prescriptions_frame.grid(row=6, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="nsew")

        # Grid Configuration
        self.inner_frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_rowconfigure(6, weight=1)

        # Load Prescriptions
        self.display_recent_prescriptions()

        # Path to the selected file
        self.selected_file_path = None

    def browse_image(self):
        """Open file dialog to select an image file."""
        file_path = filedialog.askopenfilename(
            title="Select Prescription Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            self.selected_file_path = file_path
            self.file_label.configure(text=os.path.basename(file_path))
        else:
            self.file_label.configure(text="No file selected")
            self.selected_file_path = None

    def upload_prescription(self):
        """Upload the selected image to the database with a specified storage path."""
        if not self.selected_file_path:
            CTkMessagebox(title="Error", message="Please select a prescription image first.", icon="error")
            return

        try:
            # Define the custom path to store the images
            base_storage_path = "prescriptions"
            user_directory = os.path.join(base_storage_path, f"user_{self.user_id}")
            os.makedirs(user_directory, exist_ok=True)

            # Generate a unique file name
            unique_name = f"{int(time.time())}_{os.path.basename(self.selected_file_path)}"
            save_path = os.path.join(user_directory, unique_name)

            # Copy the file
            print(f"Copying file from {self.selected_file_path} to {save_path}")
            with open(self.selected_file_path, "rb") as src, open(save_path, "wb") as dest:
                dest.write(src.read())

            # Save the relative path in the database
            relative_path = os.path.relpath(save_path, base_storage_path)
            conn = connect_to_database()
            cursor = conn.cursor()
            query = (
                "INSERT INTO prescriptions (user_id, date_prescribed, prescription_details) "
                "VALUES (%s, NOW(), %s)"
            )
            print(f"Executing SQL: {query} with user_id: {self.user_id} and save_path: {relative_path}")
            cursor.execute(query, (self.user_id, relative_path))
            conn.commit()
            cursor.close()
            conn.close()

            # Update table and reset file selection
            self.display_recent_prescriptions()
            self.file_label.configure(text="No file selected")
            self.selected_file_path = None

            CTkMessagebox(title="Success", message="Prescription uploaded successfully.", icon="info")
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            CTkMessagebox(title="Database Error", message=f"Database error: {err}", icon="error")
        except Exception as e:
            print(f"File error: {e}")
            CTkMessagebox(title="File Error", message=f"File error: {e}", icon="error")

    def display_recent_prescriptions(self):
        """Fetch and display today's prescriptions in the scrollable frame."""
        prescriptions = self.fetch_today_prescriptions()

        # Clear existing rows
        for widget in self.prescriptions_frame.winfo_children():
            widget.destroy()

        if prescriptions:
            # Add headers
            headers = ["Date", "File Name", "View"]
            for col, header in enumerate(headers):
                header_label = CTkLabel(
                    self.prescriptions_frame,
                    text=header,
                    font=("Arial", 12, "bold"),
                    text_color="#333"
                )
                header_label.grid(row=0, column=col, padx=10, pady=5, sticky="nsew")

            # Add prescription rows
            for i, prescription in enumerate(prescriptions, start=1):
                date_label = CTkLabel(
                    self.prescriptions_frame,
                    text=prescription["date_prescribed"],
                    font=("Arial", 12),
                    text_color="#555"
                )
                date_label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

                file_name_label = CTkLabel(
                    self.prescriptions_frame,
                    text=os.path.basename(prescription["prescription_details"]),
                    font=("Arial", 12),
                    text_color="#555",
                    wraplength=300,
                    justify="left"
                )
                file_name_label.grid(row=i, column=1, padx=10, pady=5, sticky="w")

                view_button = CTkButton(
                    self.prescriptions_frame,
                    text="View",
                    command=lambda p=prescription: self.view_prescription_image(p["prescription_details"]),
                    width=100,
                    fg_color="#0052cc",
                    hover_color="#003399"
                )
                view_button.grid(row=i, column=2, padx=10, pady=5)
        else:
            no_data_label = CTkLabel(
                self.prescriptions_frame,
                text="No prescriptions uploaded today.",
                font=("Arial", 12),
                text_color="grey"
            )
            no_data_label.pack(fill="both", expand=True)

    def fetch_today_prescriptions(self):
        """Fetch prescriptions uploaded today for the user."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            today_date = datetime.now().strftime("%Y-%m-%d")
            query = (
                "SELECT date_prescribed, prescription_details "
                "FROM prescriptions WHERE user_id = %s AND DATE(date_prescribed) = %s "
                "ORDER BY date_prescribed DESC"
            )
            cursor.execute(query, (self.user_id, today_date))
            prescriptions = cursor.fetchall()
            cursor.close()
            conn.close()
            return prescriptions
        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error fetching prescriptions: {err}", icon="error")
            return []

    def view_prescription_image(self, image_path):
        """View prescription image in a new window using CTkLabel."""
        if not os.path.exists(image_path):
            CTkMessagebox(title="Error", message="Prescription image not found.", icon="error")
            return

        # Create a new window to display the image
        image_window = CTkToplevel(self)
        image_window.title("Prescription Image")
        image_window.geometry("600x600")
        center_window(image_window, width=600, height=600)

        try:
            # Load and resize the image
            image = Image.open(image_path)
            resized_image = image.resize((500, 500))
            img = ImageTk.PhotoImage(resized_image)

            # Display the image in a label
            image_label = CTkLabel(image_window, image=img)
            image_label.image = img  # Prevent garbage collection
            image_label.pack(pady=20, padx=20, expand=True)

            # Add a close button
            close_button = CTkButton(
                image_window,
                text="Close",
                command=image_window.destroy,
                width=100,
                corner_radius=8,
                fg_color="#4CAF50",
                hover_color="#388E3C"
            )
            close_button.pack(pady=20)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to display image: {e}", icon="error")



class PlaceOrderFrame(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.user_id = user_id
        self.cart = []  # Initialize the cart as an empty list
        self.configure(fg_color="lightgrey")

        # Create an inner frame for layout organization
        self.inner_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=30, pady=20)

        # Title
        self.title_label = ctk.CTkLabel(
            self.inner_frame,
            text="Place Your Order",
            font=("Arial", 20, "bold"),
            text_color="#333"
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        # Prescription Selection
        self.prescription_label = ctk.CTkLabel(
            self.inner_frame,
            text="Select Prescription:",
            font=("Arial", 14),
            text_color="#555"
        )
        self.prescription_label.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="e")
        self.prescription_var = ctk.StringVar()
        self.prescription_menu = ctk.CTkOptionMenu(
            self.inner_frame,
            variable=self.prescription_var,
            values=[],  # Initially empty
            width=200
        )
        self.prescription_menu.grid(row=1, column=1, padx=10, pady=(5, 10), sticky="w")

        # Medicine Selection
        self.medicine_label = ctk.CTkLabel(
            self.inner_frame,
            text="Select Medicine:",
            font=("Arial", 14),
            text_color="#555"
        )
        self.medicine_label.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="e")
        self.medicine_var = ctk.StringVar()
        self.medicine_menu = ctk.CTkOptionMenu(
            self.inner_frame,
            variable=self.medicine_var,
            values=self.fetch_medicines(),
            width=200
        )
        self.medicine_menu.grid(row=2, column=1, padx=10, pady=(5, 10), sticky="w")

        # Quantity Selection using CTkSpinbox
        self.quantity_label = ctk.CTkLabel(
            self.inner_frame,
            text="Select Quantity:",
            font=("Arial", 14),
            text_color="#555"
        )
        self.quantity_label.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="e")
        self.quantity_spinbox = CTkSpinbox(
            self.inner_frame,
            start_value=1,
            scroll_value=1,
            width=200,
            font=("Arial", 14)
        )
        self.quantity_spinbox.grid(row=3, column=1, padx=10, pady=(5, 10), sticky="w")

        # Cart Listbox
        self.cart_list_label = ctk.CTkLabel(
            self.inner_frame,
            text="Your Cart:",
            font=("Arial", 14, "bold"),
            text_color="#333"
        )
        self.cart_list_label.grid(row=4, column=0, columnspan=2, pady=(20, 10))
        self.cart_listbox = ctk.CTkScrollableFrame(self.inner_frame, width=500, height=150, fg_color="white")
        self.cart_listbox.grid(row=5, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="nsew")

        # Buttons
        self.add_to_cart_button = ctk.CTkButton(
            self.inner_frame,
            text="Add to Cart",
            command=self.add_to_cart,
            width=150,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        self.add_to_cart_button.grid(row=6, column=0, padx=10, pady=(10, 20), sticky="e")
        self.checkout_button = ctk.CTkButton(
            self.inner_frame,
            text="Checkout",
            command=self.checkout,
            width=150,
            fg_color="#0052cc",
            hover_color="#003399"
        )
        self.checkout_button.grid(row=6, column=1, padx=10, pady=(10, 20), sticky="w")

        # Grid Configuration for Proportional Alignment
        self.inner_frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_columnconfigure(1, weight=1)
        self.inner_frame.grid_rowconfigure(5, weight=1)

        # Initialize dropdowns
        self.refresh_prescriptions()

    def fetch_prescriptions(self):
        """Fetch available prescriptions for the user."""
        prescriptions = []
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("SELECT prescription_id FROM prescriptions WHERE user_id = %s", (self.user_id,))
            prescriptions = [str(row[0]) for row in cursor.fetchall()]
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"An error occurred: {err}", icon="error")
        return prescriptions

    def fetch_medicines(self):
        """Fetch available medicines from the database."""
        medicines = []
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("SELECT medicine_name FROM medicines WHERE stock > 0")
            medicines = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"An error occurred: {err}", icon="error")
        return medicines

    def refresh_prescriptions(self):
        """Refresh the prescription dropdown with the latest data."""
        prescriptions = self.fetch_prescriptions()
        self.prescription_menu.configure(values=prescriptions)
        if prescriptions:
            self.prescription_var.set(prescriptions[0])  # Set the first value as default
        else:
            self.prescription_var.set("")

    def add_to_cart(self):
        """Add selected medicine and quantity to the cart."""
        prescription_id = self.prescription_var.get()
        medicine = self.medicine_var.get()
        quantity = int(self.quantity_spinbox.get())
        error_messages = []

        if not prescription_id:
            error_messages.append("Please select a prescription.")
        if not medicine:
            error_messages.append("Please select a medicine.")
        if quantity <= 0:
            error_messages.append("Please select a valid quantity.")

        if error_messages:
            CTkMessagebox(
                title="Validation Error",
                message="\n".join(error_messages),
                icon="warning"
            )
            return

        # Add to cart
        self.cart.append((prescription_id, medicine, quantity))
        self.update_cart_display()

    def update_cart_display(self):
        """Update the cart display in the listbox."""
        for widget in self.cart_listbox.winfo_children():
            widget.destroy()
        for i, (prescription_id, medicine, quantity) in enumerate(self.cart, start=1):
            cart_item_label = ctk.CTkLabel(
                self.cart_listbox,
                text=f"{i}. Prescription: {prescription_id}, Medicine: {medicine}, Quantity: {quantity}",
                font=("Arial", 12),
                text_color="#555"
            )
            cart_item_label.pack(padx=10, pady=5, anchor="w")

    def checkout(self):
        """Proceed to payment and show the order summary."""
        if not self.cart:
            CTkMessagebox(
                title="Cart Empty",
                message="Your cart is empty. Add items to the cart before checkout.",
                icon="warning"
            )
            return

        total_price = self.calculate_total_price()
        confirm = CTkMessagebox(
            title="Order Summary",
            message=f"Total Price: ${total_price:.2f}\nProceed to payment?",
            icon="question",
            option_1="Yes",
            option_2="No"
        )
        if confirm.get() == "Yes":
            self.process_payment(total_price)

    def calculate_total_price(self):
        """Calculate the total price of items in the cart."""
        total_price = 0
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            for _, medicine, quantity in self.cart:
                cursor.execute("SELECT price FROM medicines WHERE medicine_name = %s", (medicine,))
                price = cursor.fetchone()[0]
                total_price += price * quantity
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"An error occurred: {err}", icon="error")
        return total_price

    def process_payment(self, total_price):
        """Process payment, save order, and reset the UI."""
        self.save_order_to_database(total_price)
        CTkMessagebox(title="Success", message="Your order has been placed successfully!", icon="info")
        self.reset_order()

    def save_order_to_database(self, total_price):
        """Save the order details to the database."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            for prescription_id, medicine, quantity in self.cart:
                cursor.execute("SELECT medicine_id, stock FROM medicines WHERE medicine_name = %s", (medicine,))
                result = cursor.fetchone()
                medicine_id, stock = result
                new_stock = stock - quantity

                cursor.execute("UPDATE medicines SET stock = %s WHERE medicine_id = %s", (new_stock, medicine_id))
                cursor.execute(
                    "INSERT INTO orders (user_id, prescription_id, medicine_id, quantity, total_price, status, date_ordered) "
                    "VALUES (%s, %s, %s, %s, %s, 'pending', %s)",
                    (self.user_id, prescription_id, medicine_id, quantity, total_price, datetime.now())
                )
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"An error occurred while saving the order: {err}", icon="error")

    def reset_order(self):
        """Reset the cart and order details for a new order."""
        self.cart.clear()
        self.update_cart_display()
        self.quantity_spinbox.set(1)
        self.refresh_prescriptions()


class TrackOrderFrame(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.user_id = user_id
        self.configure(fg_color="lightgrey")

        # Create an inner frame for layout organization
        self.inner_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=30, pady=20)

        # Title
        self.title_label = ctk.CTkLabel(
            self.inner_frame,
            text="Track Your Orders",
            font=("Arial", 20, "bold"),
            text_color="#333"
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        # Scrollable Frame for Orders Table
        self.orders_frame = ctk.CTkScrollableFrame(
            self.inner_frame,
            width=700,
            height=400,
            fg_color="white",
            corner_radius=15
        )
        self.orders_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="nsew")

        # Grid Configuration
        self.inner_frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_rowconfigure(1, weight=1)

        # Load icons for different statuses
        self.icons = self.load_icons()

        # Display Orders
        self.display_orders()

    def load_icons(self):
        """Load status icons and return a dictionary."""
        icon_path = os.path.join(".", "static", "icons")
        icons = {
            "pending": ctk.CTkImage(Image.open(os.path.join(icon_path, "pending_icon.png")), size=(20, 20)),
            "approved": ctk.CTkImage(Image.open(os.path.join(icon_path, "approved_icon.png")), size=(20, 20)),
            "shipped": ctk.CTkImage(Image.open(os.path.join(icon_path, "shipped_icon.png")), size=(20, 20)),
            "delivered": ctk.CTkImage(Image.open(os.path.join(icon_path, "delivered_icon.png")), size=(20, 20)),
        }
        return icons

    def fetch_orders(self):
        """Fetch orders from the database for the current user."""
        orders = []
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT o.order_id, m.medicine_name, o.quantity, o.total_price, o.status, o.date_ordered 
                FROM orders o
                JOIN medicines m ON o.medicine_id = m.medicine_id
                WHERE o.user_id = %s
                ORDER BY o.date_ordered DESC
            """
            cursor.execute(query, (self.user_id,))
            orders = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as err:
            CTkMessagebox(title="Database Error", message=f"Error fetching orders: {err}", icon="error")
        return orders

    def display_orders(self):
        """Display each order in the orders frame with relevant details and icons."""
        orders = self.fetch_orders()

        # Clear any existing content in the frame
        for widget in self.orders_frame.winfo_children():
            widget.destroy()

        if not orders:
            no_orders_label = ctk.CTkLabel(
                self.orders_frame,
                text="No orders found.",
                font=("Arial", 14),
                text_color="grey"
            )
            no_orders_label.pack(fill="both", expand=True)
            return

        # Add table headers
        headers = ["", "Order ID", "Medicine Name", "Quantity", "Total Price", "Status", "Date Ordered"]
        for col, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                self.orders_frame,
                text=header,
                font=("Arial", 14, "bold"),
                text_color="#333"
            )
            header_label.grid(row=0, column=col, padx=10, pady=5, sticky="nsew")

        # Add rows for each order
        for i, order in enumerate(orders, start=1):
            icon = self.icons.get(order["status"], self.icons["pending"])
            icon_label = ctk.CTkLabel(self.orders_frame, image=icon, text="")
            icon_label.grid(row=i, column=0, padx=(10, 5), pady=10, sticky="w")

            order_id_label = ctk.CTkLabel(
                self.orders_frame,
                text=order["order_id"],
                font=("Arial", 12),
                text_color="#555"
            )
            order_id_label.grid(row=i, column=1, padx=10, pady=5, sticky="w")

            medicine_name_label = ctk.CTkLabel(
                self.orders_frame,
                text=order["medicine_name"],
                font=("Arial", 12),
                text_color="#555"
            )
            medicine_name_label.grid(row=i, column=2, padx=10, pady=5, sticky="w")

            quantity_label = ctk.CTkLabel(
                self.orders_frame,
                text=order["quantity"],
                font=("Arial", 12),
                text_color="#555"
            )
            quantity_label.grid(row=i, column=3, padx=10, pady=5, sticky="w")

            total_price_label = ctk.CTkLabel(
                self.orders_frame,
                text=f"${order['total_price']:.2f}",
                font=("Arial", 12),
                text_color="#555"
            )
            total_price_label.grid(row=i, column=4, padx=10, pady=5, sticky="w")

            status_label = ctk.CTkLabel(
                self.orders_frame,
                text=order["status"].capitalize(),
                font=("Arial", 12),
                text_color="#555"
            )
            status_label.grid(row=i, column=5, padx=10, pady=5, sticky="w")

            date_ordered_label = ctk.CTkLabel(
                self.orders_frame,
                text=f"{order['date_ordered']:%Y-%m-%d %H:%M:%S}",
                font=("Arial", 12),
                text_color="#555"
            )
            date_ordered_label.grid(row=i, column=6, padx=10, pady=5, sticky="w")

# Main application execution
if __name__ == "__main__":
    app = PatientDashboard(user_id=1)  # Example user ID
    app.mainloop()

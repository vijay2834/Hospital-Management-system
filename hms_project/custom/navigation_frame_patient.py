import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os

class NavigationFrame(ctk.CTkFrame):
    def __init__(self, master=None, signout_command=None):
        super().__init__(master, corner_radius=0)
        
        # Configure grid layout with no space between buttons
        self.grid_rowconfigure(5, weight=1)  # Row 5 will take remaining space
        self.grid_columnconfigure(0, weight=1)

        # Load images for icons and store them as instance variables
        image_path =  os.path.join(".", "static", "icons")
        
        # Store each image as an instance variable to keep it in memory
        self.home_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "home_icon.png")),
                                       dark_image=Image.open(os.path.join(image_path, "home_icon.png")), size=(20, 20))
        self.prescription_image = ctk.CTkImage(Image.open(os.path.join(image_path, "upload_icon.png")), size=(20, 20))
        self.order_image = ctk.CTkImage(Image.open(os.path.join(image_path, "order_icon.png")), size=(20, 20))
        self.track_image = ctk.CTkImage(Image.open(os.path.join(image_path, "track_order_icon.png")), size=(20, 20))

        # Navigation label
        self.navigation_label = ctk.CTkLabel(self, text="Patient Dashboard", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_label.grid(row=0, column=0, padx=20, pady=20)

        # Navigation buttons
        self.home_button = ctk.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Home",
                                         fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                         image=self.home_image, anchor="w", command=lambda: master.show_frame("home"))
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.upload_button = ctk.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Upload Prescription",
                                           fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                           image=self.prescription_image, anchor="w", command=lambda: master.show_frame("upload"))
        self.upload_button.grid(row=2, column=0, sticky="ew")

        self.order_button = ctk.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Place Order",
                                          fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                          image=self.order_image, anchor="w", command=lambda: master.show_frame("order"))
        self.order_button.grid(row=3, column=0, sticky="ew")

        self.track_button = ctk.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Track Order",
                                          fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                          image=self.track_image, anchor="w", command=lambda: master.show_frame("track"))
        self.track_button.grid(row=4, column=0, sticky="ew")

        # Add Sign Out Button at the bottom
        self.signout_button = ctk.CTkButton(self, text="Sign Out", command=signout_command, fg_color="#cc0000",
                                            hover_color="#ff3333", corner_radius=10)
        self.signout_button.grid(row=5, column=0, padx=20, pady=20, sticky="s")
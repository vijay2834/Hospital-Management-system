import customtkinter as ctk
from PIL import Image
import os

class NavigationFramePharmacist(ctk.CTkFrame):
    def __init__(self, master=None, signout_command=None):
        super().__init__(master, corner_radius=0)

        # Configure grid layout to eliminate any extra space
        self.grid_columnconfigure(0, weight=1)
        
        # Load images for icons
        icon_path = os.path.join(".", "static", "icons")
        
        # Store each image as an instance variable to keep it in memory
        self.home_image = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, "home_icon.png")),
                                       dark_image=Image.open(os.path.join(icon_path, "home_icon.png")), size=(20, 20))
        self.manage_prescriptions_image = ctk.CTkImage(Image.open(os.path.join(icon_path, "upload_icon.png")), size=(20, 20))
        self.orders_image = ctk.CTkImage(Image.open(os.path.join(icon_path, "order_icon.png")), size=(20, 20))

        # Navigation label without extra padding
        self.navigation_label = ctk.CTkLabel(self, text="Pharmacist Dashboard", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Navigation buttons without additional padding
        self.home_button = ctk.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Home",
                                         fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                         image=self.home_image, anchor="w", command=lambda: master.show_frame("home"))
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.manage_prescriptions_button = ctk.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Manage Prescriptions",
                                                         fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                         image=self.manage_prescriptions_image, anchor="w", command=lambda: master.show_frame("manage_prescriptions"))
        self.manage_prescriptions_button.grid(row=2, column=0, sticky="ew")

        self.orders_button = ctk.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="View Orders",
                                           fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                           image=self.orders_image, anchor="w", command=lambda: master.show_frame("view_orders"))
        self.orders_button.grid(row=3, column=0, sticky="ew")

        # Add a spacer row with weight to push the Sign Out button to the bottom
        self.grid_rowconfigure(4, weight=1)

        # Sign Out Button aligned at the bottom
        self.signout_button = ctk.CTkButton(self, text="Sign Out", command=signout_command, fg_color="#cc0000",
                                            hover_color="#ff3333", corner_radius=10)
        self.signout_button.grid(row=5, column=0, sticky="ew", padx=20, pady=20)

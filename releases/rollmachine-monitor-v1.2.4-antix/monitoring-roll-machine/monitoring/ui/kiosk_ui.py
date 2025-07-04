"""
Kiosk UI untuk monitoring mesin roll menggunakan Kivy dan KivyMD.
"""
from pathlib import Path
import serial.tools.list_ports
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import os

from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.app import App

from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.icon_definitions import md_icons
from kivymd.uix.behaviors.focus_behavior import StateFocusBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivy_garden.graph import Graph, MeshLinePlot
from collections import deque
import csv

from ..monitor import Monitor
from ..serial_handler import JSKSerialPort
from ..config import load_config, save_config
from ..logging_utils import setup_logging

logger = logging.getLogger(__name__)

class FormField(BoxLayout, StateFocusBehavior):
    """A single form field with label and input."""
    def __init__(self, label_text: str, hint_text: str, input_filter: Optional[str] = None, readonly: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(8)  # Increased spacing
        self.size_hint_y = None
        self.height = dp(100)  # Increased height for touch
        self.padding = [dp(8), dp(8), dp(8), dp(8)]  # Increased padding
        self.focus_color = (0.95, 0.95, 0.97, 1)
        self.unfocus_color = (1, 1, 1, 0)

        # Label with larger font
        self.label = MDLabel(
            text=label_text,
            theme_text_color="Primary",
            role="large",  # Larger font
            size_hint_y=None,
            height=dp(30),  # Increased height
            bold=True  # Make it bold
        )
        
        # Input field with larger font and touch-friendly size
        self.text_field = MDTextField(
            text="",
            hint_text=hint_text,
            mode="filled",
            input_filter=input_filter,
            size_hint_y=None,
            height=dp(60),  # Increased height for touch
            line_color_normal=(0.7, 0.7, 0.7, 1),
            line_color_focus=(0.2, 0.2, 0.8, 1),
            font_size=dp(20),  # Larger font size
            readonly=readonly,  # Add readonly support
            multiline=False,  # Single line input
        )

        self.add_widget(self.label)
        self.add_widget(self.text_field)

class ProductForm(MDCard):
    """Form untuk input informasi produk."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(24)
        self.spacing = dp(16)
        self.size_hint_y = None
        self.height = dp(600)  # Increased height for more fields
        self.elevation = 2
        self.radius = [dp(8)]

        # Title with bottom margin
        title_box = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(60),
            padding=[0, 0, 0, dp(8)]
        )
        
        title = MDLabel(
            text="Product Information",
            theme_text_color="Primary",
            role="large",
            size_hint_y=None,
            height=dp(50),
            bold=True
        )
        title_box.add_widget(title)
        self.add_widget(title_box)

        # Form fields container
        form_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(500),
            padding=dp(16),
            md_bg_color=(0.98, 0.98, 0.98, 1)
        )

        # ERP Item Selection
        self.item_code_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(60)
        )
        
        self.item_code_button = MDButton(
            MDButtonText(
                text="Select Item Code",
            ),
            style="filled",
            size_hint_x=0.7
        )
        self.item_code_button.bind(on_release=self.show_item_menu)
        
        self.refresh_button = MDButton(
            MDButtonIcon(
                icon="refresh",
            ),
            style="filled",
            size_hint_x=0.3
        )
        self.refresh_button.bind(on_release=self.refresh_items)
        
        self.item_code_layout.add_widget(self.item_code_button)
        self.item_code_layout.add_widget(self.refresh_button)
        form_container.add_widget(self.item_code_layout)

        # Create read-only ERP fields
        self.product_name_field = FormField(
            label_text="Product Name",
            hint_text="Selected product name",
            readonly=True
        )
        self.composition_field = FormField(
            label_text="Composition",
            hint_text="Product composition",
            readonly=True
        )
        self.production_date_field = FormField(
            label_text="Production Date",
            hint_text="YYYY-MM-DD",
            readonly=True
        )
        self.weight_field = FormField(
            label_text="Basic Weight (GSM)",
            hint_text="Gramasi",
            readonly=True
        )
        self.production_code_field = FormField(
            label_text="Production Code",
            hint_text="Production batch code",
            readonly=True
        )

        # Length input section with unit conversion
        self.actual_length_field = FormField(
            label_text="Actual Length (meters)",
            hint_text="Enter actual length",
            input_filter="float"
        )
        
        # Unit selection for label
        self.unit_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(60)
        )
        
        self.unit_label = MDLabel(
            text="Label Unit:",
            theme_text_color="Primary",
            size_hint_x=0.3
        )
        
        self.unit_button = MDButton(
            MDButtonText(
                text="meters",
            ),
            style="filled",
            size_hint_x=0.7
        )
        self.unit_button.bind(on_release=self.show_unit_menu)
        
        self.unit_layout.add_widget(self.unit_label)
        self.unit_layout.add_widget(self.unit_button)
        
        # Converted length display (read-only)
        self.converted_length_field = FormField(
            label_text="Length for Label",
            hint_text="Converted length",
            readonly=True
        )

        # Add all fields to form container
        for field in [
            self.product_name_field,
            self.composition_field,
            self.production_date_field,
            self.weight_field,
            self.production_code_field,
            self.actual_length_field,
            self.unit_layout,
            self.converted_length_field
        ]:
            form_container.add_widget(field)

        self.add_widget(form_container)

        # Initialize menus
        self.item_menu = None
        self.unit_menu = None
        self.available_items = []  # Will be populated from ERP
        
        # Bind length input to conversion
        self.actual_length_field.text_field.bind(
            text=self.update_converted_length
        )

    def show_item_menu(self, button):
        """Show the item selection dropdown menu."""
        if not self.item_menu:
            menu_items = []
            if self.available_items:
                for item in self.available_items:
                    menu_items.append({
                        "text": f"{item['code']} - {item['name']}",
                        "viewclass": "OneLineListItem",
                        "on_release": lambda x, i=item: self.select_item(i),
                    })
            else:
                menu_items.append({
                    "text": "No items available",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x: None,
                })
            
            self.item_menu = MDDropdownMenu(
                caller=self.item_code_button,
                items=menu_items,
                width_mult=4,
            )
        self.item_menu.open()

    def show_unit_menu(self, button):
        """Show the unit selection dropdown menu."""
        if not self.unit_menu:
            menu_items = [
                {
                    "text": "meter",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x: self.select_unit("meter"),
                },
                {
                    "text": "yard",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x: self.select_unit("yard"),
                }
            ]
            
            self.unit_menu = MDDropdownMenu(
                caller=self.unit_button,
                items=menu_items,
                width_mult=2,
                position="bottom"
            )
        self.unit_menu.open()

    def select_item(self, item: Dict[str, Any]) -> None:
        """Handle item selection from ERP dropdown."""
        self.item_code_button.text = item['code']
        self.product_name_field.text_field.text = item['name']
        self.composition_field.text_field.text = item.get('composition', '')
        self.production_date_field.text_field.text = item.get('prod_date', '')
        self.weight_field.text_field.text = str(item.get('weight', ''))
        self.production_code_field.text_field.text = item.get('prod_code', '')
        
        if self.item_menu:
            self.item_menu.dismiss()
            self.item_menu = None

    def select_unit(self, unit: str) -> None:
        """Handle unit selection."""
        self.unit_button.text = unit
        if self.unit_menu:
            self.unit_menu.dismiss()
            self.unit_menu = None
        self.update_converted_length()

    def update_converted_length(self, *args) -> None:
        """Update converted length based on input and selected unit."""
        try:
            actual_length = float(self.actual_length_field.text_field.text or 0)
            if self.unit_button.text == "yard":
                # Convert meters to yards (1 meter = 1.09361 yards)
                converted = actual_length * 1.09361
                self.converted_length_field.text_field.text = f"{converted:.2f} yard"
            else:
                # Keep in meters
                self.converted_length_field.text_field.text = f"{actual_length:.2f} meter"
        except ValueError:
            self.converted_length_field.text_field.text = "Invalid input"

    def refresh_items(self, *args) -> None:
        """Refresh items from ERP system."""
        # TODO: Implement ERP integration
        # For now, using mock data
        self.available_items = [
            {
                'code': 'ITEM001',
                'name': 'Cotton Fabric',
                'composition': '100% Cotton',
                'prod_date': '2024-03-20',
                'weight': '150',
                'prod_code': 'BATCH001'
            },
            {
                'code': 'ITEM002',
                'name': 'Polyester Blend',
                'composition': '60% Cotton, 40% Polyester',
                'prod_date': '2024-03-20',
                'weight': '180',
                'prod_code': 'BATCH002'
            }
        ]
        self.item_menu = None  # Reset menu to update items

class MachineStatus(MDCard):
    """Panel untuk menampilkan status mesin."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(20)
        self.spacing = dp(16)
        self.size_hint_y = None
        self.height = dp(400)  # Increased height
        self.elevation = 2
        self.radius = [dp(8)]

        # Title with icon
        title_box = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(50)
        )
        
        title_icon = MDButton(
            MDButtonIcon(
                icon="engine",
            ),
            style="text",
            size_hint_x=None,
            width=dp(48)
        )
        
        title = MDLabel(
            text="Machine Status",
            theme_text_color="Primary",
            role="large",
            bold=True
        )
        
        title_box.add_widget(title_icon)
        title_box.add_widget(title)
        self.add_widget(title_box)

        # Connection status with icon
        self.conn_status = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48)
        )
        
        self.conn_icon = MDButton(
            MDButtonIcon(
                icon="lan-disconnect",
            ),
            style="text",
            size_hint_x=None,
            width=dp(48)
        )
        
        self.conn_label = MDLabel(
            text="Disconnected",
            theme_text_color="Error",
            role="medium"
        )
        
        self.conn_status.add_widget(self.conn_icon)
        self.conn_status.add_widget(self.conn_label)
        self.add_widget(self.conn_status)

        # Status fields with large text
        self.rolled_length = MDLabel(
            text="0.0",
            theme_text_color="Primary",
            role="large",
            font_size=dp(36),  # Use explicit font size
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )
        self.rolled_length_unit = MDLabel(
            text="meters rolled",
            theme_text_color="Secondary",
            role="medium",
            halign="center",
            size_hint_y=None,
            height=dp(30)
        )

        self.speed = MDLabel(
            text="0.0",
            theme_text_color="Primary",
            role="large",
            font_size=dp(36),  # Use explicit font size
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )
        self.speed_unit = MDLabel(
            text="meters/minute",
            theme_text_color="Secondary",
            role="medium",
            halign="center",
            size_hint_y=None,
            height=dp(30)
        )

        # Current shift and time
        info_box = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(80),
            padding=[dp(8), dp(8), dp(8), dp(8)]
        )
        
        # Shift info
        shift_box = MDBoxLayout(
            orientation="vertical",
            size_hint_x=0.5
        )
        self.shift = MDLabel(
            text="1",
            theme_text_color="Primary",
            role="large",
            font_size=dp(28),  # Use explicit font size
            halign="center"
        )
        shift_label = MDLabel(
            text="Current Shift",
            theme_text_color="Secondary",
            role="medium",
            halign="center"
        )
        shift_box.add_widget(self.shift)
        shift_box.add_widget(shift_label)
        
        # Time info
        time_box = MDBoxLayout(
            orientation="vertical",
            size_hint_x=0.5
        )
        self.current_time = MDLabel(
            text="00:00:00",
            theme_text_color="Primary",
            role="large",
            font_size=dp(28),  # Use explicit font size
            halign="center"
        )
        time_label = MDLabel(
            text="Time",
            theme_text_color="Secondary",
            role="medium",
            halign="center"
        )
        time_box.add_widget(self.current_time)
        time_box.add_widget(time_label)
        
        info_box.add_widget(shift_box)
        info_box.add_widget(time_box)

        # Add all status components
        for widget in [
            self.rolled_length,
            self.rolled_length_unit,
            self.speed,
            self.speed_unit,
            info_box
        ]:
            self.add_widget(widget)

        # Start clock update
        Clock.schedule_interval(self.update_time, 1)

    def update_time(self, dt):
        """Update current time display."""
        self.current_time.text = datetime.now().strftime("%H:%M:%S")

    def update_connection_status(self, connected: bool):
        """Update connection status display."""
        if connected:
            self.conn_icon.icon = "lan-connect"
            self.conn_label.text = "Connected"
            self.conn_label.theme_text_color = "Success"
        else:
            self.conn_icon.icon = "lan-disconnect"
            self.conn_label.text = "Disconnected"
            self.conn_label.theme_text_color = "Error"

    def update_status(self, length: float, speed: float, shift: int):
        """Update machine status display."""
        self.rolled_length.text = f"{length:.1f}"
        self.speed.text = f"{speed:.1f}"
        self.shift.text = str(shift)

class ConnectionSettings(MDCard):
    """Panel untuk pengaturan koneksi serial."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(20)
        self.spacing = dp(16)
        self.size_hint_y = None
        self.height = dp(300)
        self.elevation = 2
        self.radius = [dp(8)]
        self.available_ports: List[str] = []
        self._is_port_available = False

        # Title with icon
        title_box = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(50)
        )
        
        title_icon = MDButton(
            MDButtonIcon(
                icon="serial-port",
            ),
            style="text",
            size_hint_x=None,
            width=dp(48)
        )
        
        title = MDLabel(
            text="Connection Settings",
            theme_text_color="Primary",
            role="large",
            bold=True
        )
        
        title_box.add_widget(title_icon)
        title_box.add_widget(title)
        self.add_widget(title_box)

        # Port selection with large touch targets
        port_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(160),
            padding=[0, dp(8), 0, dp(8)]
        )
        
        # Port selection row
        port_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(60)
        )
        
        # Port dropdown button
        self.port_button = MDButton(
            MDButtonText(
                text="PORT",  # Default text showing it's a port selection
            ),
            MDButtonIcon(
                icon="chevron-down",
            ),
            style="outlined",  # Start with outlined style
            size_hint_x=0.7,
            height=dp(56)
        )
        self.port_button.bind(on_release=self.show_port_menu)

        # Port spinner
        self.port_spinner = MDCircularProgressIndicator(
            size_hint=(None, None),
            size=(dp(46), dp(46)),
            active=False
        )
        
        # Refresh button
        self.refresh_btn = MDButton(
            MDButtonText(
                text="Refresh",
            ),
            MDButtonIcon(
                icon="refresh",
            ),
            style="filled",
            size_hint_x=0.3,
            height=dp(56)
        )
        self.refresh_btn.bind(on_release=self.refresh_ports)
        
        port_row.add_widget(self.port_button)
        port_row.add_widget(self.port_spinner)
        port_row.add_widget(self.refresh_btn)
        
        # Port status message
        self.port_status = MDLabel(
            text="Silakan pilih port yang tersedia",
            theme_text_color="Secondary",
            role="medium",
            size_hint_y=None,
            height=dp(30)
        )
        
        # Auto-connect switch row
        auto_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(60)
        )
        
        auto_label = MDLabel(
            text="Auto Connect",
            theme_text_color="Primary",
            role="medium",
            size_hint_x=0.7
        )
        
        self.auto_connect = MDSwitch(
            size_hint_x=0.3,
            pos_hint={"center_y": 0.5},
            disabled=True  # Start disabled until port is selected
        )
        
        auto_row.add_widget(auto_label)
        auto_row.add_widget(self.auto_connect)
        
        # Add rows to port layout
        port_layout.add_widget(port_row)
        port_layout.add_widget(self.port_status)
        port_layout.add_widget(auto_row)
        self.add_widget(port_layout)

        # Connection info
        info_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None,
            height=dp(60),
            padding=[dp(8), dp(4), dp(8), dp(4)],
            md_bg_color=(0.95, 0.95, 0.95, 1)
        )
        
        self.conn_info = MDLabel(
            text="Baudrate: 19200, Data: 8bit, Parity: None, Stop: 1bit",
            theme_text_color="Secondary",
            role="medium",
            size_hint_y=None,
            height=dp(30)
        )
        
        self.last_connected = MDLabel(
            text="Last Connected: Never",
            theme_text_color="Secondary",
            role="medium",
            size_hint_y=None,
            height=dp(30)
        )
        
        info_box.add_widget(self.conn_info)
        info_box.add_widget(self.last_connected)
        self.add_widget(info_box)

        # Initialize port menu
        self.port_menu = None
        self.refresh_ports()

    def show_port_menu(self, button):
        """Show the port selection dropdown menu."""
        if not self.port_menu:
            menu_items = []
            ports = list(serial.tools.list_ports.comports())
            
            if not ports:
                menu_items.append({
                    "text": "Tidak ada port yang tersedia",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x: self.select_port(""),
                })
            else:
                for port in ports:
                    menu_items.append({
                        "text": port.device,
                        "viewclass": "OneLineListItem",
                        "on_release": lambda x, p=port.device: self.select_port(p),
                    })
            
            self.port_menu = MDDropdownMenu(
                caller=self.port_button,
                items=menu_items,
                width_mult=2,
                position="bottom"
            )
        self.port_menu.open()

    def select_port(self, port_name: str) -> None:
        """Handle port selection."""
        if not port_name:
            self._set_no_port_state()
            return
            
        self.port_button.text = port_name
        if self.port_menu:
            self.port_menu.dismiss()
            self.port_menu = None

    def _set_no_port_state(self):
        """Set UI state when no port is available."""
        self.port_button.text = "PORT"  # Keep showing PORT as the button text
        self.port_button.style = "outlined"
        self.port_status.text = "Port Tidak Ditemukan"  # Show status message instead
        self.port_status.theme_text_color = "Error"
        self.auto_connect.active = False
        self.auto_connect.disabled = True
        self._is_port_available = False

    def refresh_ports(self, *args) -> None:
        """Refresh the list of available serial ports."""
        self.port_spinner.active = True
        self.available_ports = []
        
        try:
            ports = list(serial.tools.list_ports.comports())
            self.available_ports = [port.device for port in ports]
            
            if self.available_ports:
                # Check if currently selected port is still available
                current_port = self.port_button.text
                if current_port != "PORT" and current_port in self.available_ports:
                    self.select_port(current_port)
                else:
                    self.select_port(self.available_ports[0])
                self.port_status.text = "Silakan pilih port yang tersedia"
                self.port_status.theme_text_color = "Secondary"
            else:
                self._set_no_port_state()
                self.port_status.text = "Tidak ada port yang tersedia"
                
        except Exception as e:
            self._set_no_port_state()
            self.port_status.text = "Gagal mendapatkan daftar port"
            logger.error(f"Error refreshing ports: {e}")
            
        finally:
            self.port_spinner.active = False
            self.port_menu = None
            logger.info(f"Found ports: {self.available_ports}")

    def get_selected_port(self) -> str:
        """Get the currently selected port."""
        if self._is_port_available and self.port_button.text != "PORT":
            return self.port_button.text
        return ""

    def get_auto_connect(self) -> bool:
        """Get auto-connect setting."""
        return self.auto_connect.active and self._is_port_available

class ControlButtons(MDBoxLayout):
    """Panel untuk tombol kontrol."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = dp(10)
        self.padding = dp(20)
        self.size_hint_y = None
        self.height = dp(80)

        # Start/Stop button
        self.start_button = MDButton(
            MDButtonText(
                text="Start Monitoring",
            ),
            style="filled",
            md_bg_color=(0.2, 0.8, 0.2, 1),  # Green
            size_hint_x=0.5
        )

        # Save button
        self.save_button = MDButton(
            MDButtonText(
                text="Save Data",
            ),
            style="filled",
            md_bg_color=(0.2, 0.2, 0.8, 1),  # Blue
            size_hint_x=0.5,
            disabled=True
        )

        self.add_widget(self.start_button)
        self.add_widget(self.save_button)

class Statistics(MDCard):
    """Panel untuk statistik dan visualisasi data."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(20)
        self.spacing = dp(10)
        self.elevation = 2

        # Data storage
        self.max_points = 100
        self.length_data = deque(maxlen=self.max_points)
        self.speed_data = deque(maxlen=self.max_points)
        self.timestamps = deque(maxlen=self.max_points)

        # Title
        title = MDLabel(
            text="Statistics",
            theme_text_color="Primary",
            role="large",
            size_hint_y=None,
            height=dp(50)
        )
        self.add_widget(title)

        # Graphs layout
        graphs_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10)
        )

        # Length graph
        self.length_graph = Graph(
            xlabel='Time',
            ylabel='Length (m)',
            x_ticks_minor=5,
            x_ticks_major=25,
            y_ticks_major=10,
            y_grid=True,
            x_grid=True,
            padding=5,
            x_grid_label=True,
            y_grid_label=True,
            xmin=0,
            xmax=100,
            ymin=0,
            ymax=50
        )
        self.length_plot = MeshLinePlot(color=[0, 1, 0, 1])
        self.length_graph.add_plot(self.length_plot)
        graphs_layout.add_widget(self.length_graph)

        # Speed graph
        self.speed_graph = Graph(
            xlabel='Time',
            ylabel='Speed (m/s)',
            x_ticks_minor=5,
            x_ticks_major=25,
            y_ticks_major=1,
            y_grid=True,
            x_grid=True,
            padding=5,
            x_grid_label=True,
            y_grid_label=True,
            xmin=0,
            xmax=100,
            ymin=0,
            ymax=5
        )
        self.speed_plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.speed_graph.add_plot(self.speed_plot)
        graphs_layout.add_widget(self.speed_graph)

        self.add_widget(graphs_layout)

    def update_data(self, data: Dict[str, Any]) -> None:
        """Update data dan grafik."""
        try:
            timestamp = datetime.now()
            length = data.get('length', 0)
            speed = data.get('speed', 0)

            # Store data
            self.timestamps.append(timestamp)
            self.length_data.append(length)
            self.speed_data.append(speed)

            # Update length plot
            length_points = [(i, y) for i, y in enumerate(self.length_data)]
            self.length_plot.points = length_points

            # Update speed plot
            speed_points = [(i, y) for i, y in enumerate(self.speed_data)]
            self.speed_plot.points = speed_points

            # Adjust y-axis limits if needed
            if length > self.length_graph.ymax:
                self.length_graph.ymax = length * 1.2
            if speed > self.speed_graph.ymax:
                self.speed_graph.ymax = speed * 1.2

        except Exception as e:
            logger.error(f"Error updating statistics: {e}")

    def export_data(self, filename: str) -> None:
        """Export data ke file CSV."""
        try:
            export_dir = Path("export")
            export_dir.mkdir(exist_ok=True)
            filepath = export_dir / filename

            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Length (m)', 'Speed (m/s)'])
                for ts, length, speed in zip(self.timestamps, self.length_data, self.speed_data):
                    writer.writerow([ts.isoformat(), length, speed])

            logger.info(f"Data exported to {filepath}")

        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            raise

class MonitoringKioskApp(MDApp):
    """Aplikasi utama monitoring kiosk."""
    def __init__(self, **kwargs):
        # Set up kiosk mode before super().__init__
        from kivy.config import Config
        Config.set('graphics', 'fullscreen', 'auto')
        Config.set('graphics', 'borderless', '1')
        Config.set('kivy', 'exit_on_escape', '0')  # Disable Esc key exit
        Config.set('kivy', 'keyboard_mode', 'systemanddock')  # Enable both system and dock keyboard
        
        super().__init__(**kwargs)
        self.monitor: Optional[Monitor] = None
        self.config = {
            "port": "COM1",
            "baudrate": 19200,
            "auto_connect": False,
            "language": "en"
        }
        self.config.update(load_config())
        setup_logging()
        
        # Set up window properties
        Window.borderless = True
        Window.fullscreen = 'auto'
        Window.allow_screensaver = False

    def build(self):
        """Build UI aplikasi."""
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        # Main layout with responsive sizing
        main_layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20),
            md_bg_color=(0.95, 0.95, 0.95, 1)  # Light gray background
        )
        
        # Header with clock
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            padding=[dp(16), 0, dp(16), 0]
        )
        
        # App title
        app_title = MDLabel(
            text="Fabric Roll Monitoring",
            theme_text_color="Primary",
            role="large",
            font_size=dp(24),  # Use explicit font size instead of font_style
            bold=True,
            size_hint_x=0.7
        )
        
        # Clock display
        self.clock_display = MDLabel(
            text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            theme_text_color="Secondary",
            role="large",
            halign="right",
            size_hint_x=0.3
        )
        
        header.add_widget(app_title)
        header.add_widget(self.clock_display)
        main_layout.add_widget(header)
        
        # Content area with scrolling
        content_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            adaptive_height=True
        )
        
        # Top section (Product Form & Machine Status)
        top_section = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(20),
            size_hint_y=None,
            height=dp(600)  # Increased height
        )
        
        # Product form in a scroll view for small screens
        product_scroll = MDScrollView(
            size_hint_x=0.6
        )
        self.product_form = ProductForm()
        product_scroll.add_widget(self.product_form)
        
        # Machine status and connection settings
        status_section = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            size_hint_x=0.4
        )
        self.machine_status = MachineStatus()
        self.conn_settings = ConnectionSettings()
        status_section.add_widget(self.machine_status)
        status_section.add_widget(self.conn_settings)
        
        top_section.add_widget(product_scroll)
        top_section.add_widget(status_section)
        content_layout.add_widget(top_section)
        
        # Control buttons
        self.control_buttons = ControlButtons()
        content_layout.add_widget(self.control_buttons)
        
        # Statistics section
        self.statistics = Statistics()
        content_layout.add_widget(self.statistics)
        
        # Add content to a scroll view for very small screens
        main_scroll = MDScrollView()
        main_scroll.add_widget(content_layout)
        main_layout.add_widget(main_scroll)
        
        # Setup event handlers
        self.control_buttons.start_button.bind(on_release=self.start_monitoring)
        self.control_buttons.save_button.bind(on_release=self.save_data)
        
        # Setup keyboard
        Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
        Window.softinput_mode = "below_target"
        
        # Start update timers
        Clock.schedule_interval(self.update_status, 1.0)
        Clock.schedule_interval(self.update_clock, 1.0)
        
        return main_layout

    def start_monitoring(self, *args):
        """Mulai monitoring mesin."""
        try:
            if not self.monitor:
                port = self.config.get("port", "COM1")
                baudrate = self.config.get("baudrate", 19200)
                serial_port = JSKSerialPort(port=port, baudrate=baudrate)
                serial_port.open()
                serial_port.enable_auto_recover()
                
                self.monitor = Monitor(
                    serial_port=serial_port,
                    on_data=self.handle_data,
                    on_error=self.handle_error
                )
            
            self.monitor.start()
            self.conn_settings.conn_status.text = "Connection Status: Connected ✅"
            self.conn_settings.conn_status.theme_text_color = "Success"
            self.conn_settings.last_connected.text = f"Last Connected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            self.show_error("Failed to start monitoring", str(e))

    def stop_monitoring(self, *args):
        """Stop monitoring mesin."""
        try:
            if self.monitor:
                self.monitor.stop()
                self.monitor.serial_port.disable_auto_recover()
            self.conn_settings.conn_status.text = "Connection Status: Disconnected ❌"
            self.conn_settings.conn_status.theme_text_color = "Error"
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
            self.show_error("Failed to stop monitoring", str(e))

    def handle_data(self, data: Dict[str, Any]) -> None:
        """Handle data dari monitor."""
        # Data handling akan diupdate di update_status
        pass

    def handle_error(self, error: Exception) -> None:
        """Handle error dari monitor."""
        logger.error(f"Monitor error: {error}")
        self.show_error("Monitor Error", str(error))

    def save_data(self, *args):
        """Simpan data monitoring ke file."""
        try:
            if self.monitor:
                # TODO: Implement data saving
                pass
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            self.show_error("Failed to save data", str(e))

    def update_status(self, dt):
        """Update status display setiap interval."""
        if self.monitor and self.monitor.is_running:
            try:
                status = self.monitor.get_status()
                if status:
                    self.machine_status.rolled_length.text = f"Rolled Length: {status['current_count']:.1f} m"
                    self.machine_status.speed.text = f"Speed: {status['current_speed']:.1f} m/min"
                    self.machine_status.shift.text = f"Shift: {status['shift']}"
                    
                    # Update target status
                    target = float(self.product_form.target_length.text or 0)
                    if status['current_count'] >= target:
                        self.machine_status.target_status.text = "Target Status: Reached ✅"
                        self.machine_status.target_status.theme_text_color = "Success"
                    else:
                        self.machine_status.target_status.text = "Target Status: Not Reached ❌"
                        self.machine_status.target_status.theme_text_color = "Error"
            except Exception as e:
                logger.error(f"Error updating status: {e}")

    def show_error(self, title: str, message: str):
        """Show error dialog."""
        if not hasattr(self, 'dialog') or not self.dialog:
            self.dialog = MDDialog(
                title=title,
                text=message,
                buttons=[
                    MDButton(
                        MDButtonText(
                            text="OK",
                        ),
                        style="text",
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
        self.dialog.open()

    def on_stop(self):
        """Cleanup saat aplikasi ditutup."""
        if self.monitor:
            self.monitor.stop()
        save_config(self.config)

    def update_clock(self, dt):
        """Update clock display."""
        self.clock_display.text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    MonitoringKioskApp().run() 
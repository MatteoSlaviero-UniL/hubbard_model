import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from hubbard import Hubbard

COLOR_INTENSITY = 20

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Default Parameters
        self.LATTICE_SIZE = 10
        self.NUM_ELECTRONS = 50
        self.U = 1.0
        self.T = 1.0
        self.STEP_INTERVAL = 0.001  # Default interval for autoplay in seconds

        # Simulation Variables
        self.hubbard = None
        self.success_count = 0
        self.fail_count = 0
        self.autoplay_running = False

        # Timer for autoplay
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.perform_step)

        # Initialize UI
        self.init_ui()

    def init_ui(self):
        """
        Set up the main window UI.
        """
        self.setWindowTitle("Hubbard Model Simulation")
        self.setGeometry(100, 100, 900, 700)

        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)

        # Parameter Controls
        control_layout = QtWidgets.QHBoxLayout()

        self.lattice_size_input = QtWidgets.QSpinBox(self)
        self.lattice_size_input.setRange(2, 15)
        self.lattice_size_input.setValue(self.LATTICE_SIZE)
        control_layout.addWidget(QtWidgets.QLabel("Lattice Size (NxN):"))
        control_layout.addWidget(self.lattice_size_input)

        self.num_electrons_input = QtWidgets.QSpinBox(self)
        self.num_electrons_input.setRange(0, 2 * 15 * 15)
        self.num_electrons_input.setValue(self.NUM_ELECTRONS)
        control_layout.addWidget(QtWidgets.QLabel("Number of Electrons:"))
        control_layout.addWidget(self.num_electrons_input)

        self.u_input = QtWidgets.QDoubleSpinBox(self)
        self.u_input.setRange(0.1, 100.0)
        self.u_input.setDecimals(2)
        self.u_input.setValue(self.U)
        control_layout.addWidget(QtWidgets.QLabel("U (On-Site Repulsion):"))
        control_layout.addWidget(self.u_input)

        self.t_input = QtWidgets.QDoubleSpinBox(self)
        self.t_input.setRange(0.1, 100.0)
        self.t_input.setDecimals(2)
        self.t_input.setValue(self.T)
        control_layout.addWidget(QtWidgets.QLabel("T (Hopping Parameter):"))
        control_layout.addWidget(self.t_input)

        self.step_interval_input = QtWidgets.QDoubleSpinBox(self)
        self.step_interval_input.setRange(0.001, 2.0)
        self.step_interval_input.setDecimals(3)
        self.step_interval_input.setValue(self.STEP_INTERVAL)
        control_layout.addWidget(QtWidgets.QLabel("Step Interval (seconds):"))
        control_layout.addWidget(self.step_interval_input)

        main_layout.addLayout(control_layout)

        # Grid Layout for Lattice Visualization
        self.grid_layout = QtWidgets.QGridLayout()
        main_layout.addLayout(self.grid_layout)

        # Buttons and Counters
        button_layout = QtWidgets.QHBoxLayout()

        self.init_random_button = QtWidgets.QPushButton("Initialize Random", self)
        self.init_random_button.clicked.connect(self.initialize_random)
        button_layout.addWidget(self.init_random_button)

        self.init_af_button = QtWidgets.QPushButton("Initialize AF", self)
        self.init_af_button.clicked.connect(self.initialize_af)
        button_layout.addWidget(self.init_af_button)

        self.init_localized_button = QtWidgets.QPushButton("Initialize Localized", self)
        self.init_localized_button.clicked.connect(self.initialize_localized)
        button_layout.addWidget(self.init_localized_button)

        self.play_button = QtWidgets.QPushButton("Perform Step", self)
        self.play_button.clicked.connect(self.perform_step)
        button_layout.addWidget(self.play_button)

        self.autoplay_button = QtWidgets.QPushButton("Autoplay", self)
        self.autoplay_button.clicked.connect(self.toggle_autoplay)
        button_layout.addWidget(self.autoplay_button)

        self.success_label = QtWidgets.QLabel("Successful Steps: 0", self)
        button_layout.addWidget(self.success_label)

        self.fail_label = QtWidgets.QLabel("Failed Steps: 0", self)
        button_layout.addWidget(self.fail_label)

        main_layout.addLayout(button_layout)

    def initialize_random(self):
        """
        Initialize the lattice randomly and update the UI.
        """
        self.initialize_lattice("random")

    def initialize_af(self):
        """
        Initialize the lattice in an antiferromagnetic way and update the UI.
        """
        self.initialize_lattice("af")

    def initialize_localized(self):
        """
        Initialize the lattice in a localized way and update the UI.
        """
        self.initialize_lattice("localized")

    def initialize_lattice(self, mode="random"):
        """
        Initialize the lattice based on the selected mode.
        """
        self.LATTICE_SIZE = self.lattice_size_input.value()
        self.NUM_ELECTRONS = self.num_electrons_input.value()
        self.U = self.u_input.value()
        self.T = self.t_input.value()

        self.hubbard = Hubbard(size=self.LATTICE_SIZE, u=self.U, t=self.T, num_electrons=self.NUM_ELECTRONS)

        if mode == "random":
            self.hubbard.initialize_lattice()
        elif mode == "af":
            self.hubbard.initialize_af()
        elif mode == "localized":
            self.hubbard.initialize_localized()

        self.success_count = 0
        self.fail_count = 0

        self.update_counters()
        self.setup_grid()
        self.update_grid()

    def setup_grid(self):
        """
        Set up the grid layout for lattice visualization.
        """
        # Clear existing grid
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Create a new grid
        self.grid_cells = [[QtWidgets.QLabel("", self) for _ in range(self.LATTICE_SIZE)] for _ in range(self.LATTICE_SIZE)]

        for x in range(self.LATTICE_SIZE):
            for y in range(self.LATTICE_SIZE):
                label = self.grid_cells[x][y]
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
                label.setFixedSize(40, 40)
                label.setStyleSheet("border: 1px solid black;")
                self.grid_layout.addWidget(label, x, y)

    def perform_step(self):
        """
        Perform one simulation step and update the UI.
        """
        if not self.hubbard:
            QtWidgets.QMessageBox.warning(self, "Error", "Initialize the lattice first!")
            return

        success, (x, y), spin, (target_x, target_y) = self.hubbard.simulate_step()

        if success:
            self.success_count += 1
            color = "green"
        else:
            self.fail_count += 1
            color = "red"

        self.update_counters()
        self.update_grid()

        # Clear highlights from the previous step
        self.clear_highlights()

        self.highlight_cell(x, y, "yellow")
        self.highlight_cell(target_x, target_y, color)

    def toggle_autoplay(self):
        """
        Toggle autoplay on or off.
        """
        if self.autoplay_running:
            self.timer.stop()
            self.autoplay_button.setText("Autoplay")
        else:
            interval = self.step_interval_input.value()
            self.timer.start(int(interval * 1000))  # Convert seconds to milliseconds
            self.autoplay_button.setText("Stop Autoplay")

        self.autoplay_running = not self.autoplay_running

    def update_counters(self):
        """
        Update the success and failure counters in the UI.
        """
        self.success_label.setText(f"Successful Steps: {self.success_count}")
        self.fail_label.setText(f"Failed Steps: {self.fail_count}")

    def clear_highlights(self):
        """
        Reset all cells' borders to the default style without altering background colors.
        """
        for x in range(self.LATTICE_SIZE):
            for y in range(self.LATTICE_SIZE):
                current_style = self.grid_cells[x][y].styleSheet()
                updated_style = ";".join(
                    part for part in current_style.split(";") if not part.strip().startswith("border")
                )
                self.grid_cells[x][y].setStyleSheet(f"{updated_style}; border: 1px solid black;")

    def update_grid(self):
        """
        Update the grid display based on the lattice state.
        """
        if not self.hubbard:
            return

        lattice = self.hubbard.get_lattice()

        # Calculate alpha value based on percentage
        alpha = int(COLOR_INTENSITY / 100 * 255)  # Scale to 0-255 range

        for x in range(self.LATTICE_SIZE):
            for y in range(self.LATTICE_SIZE):
                up = lattice[0, x, y]
                down = lattice[1, x, y]

                if up and down:
                    text = "↑↓"
                    background_color = f"rgba(0, 255, 0, {alpha})"  # Green for both spins
                elif up:
                    text = "↑"
                    background_color = f"rgba(255, 0, 0, {alpha})"  # Red for spin up
                elif down:
                    text = "↓"
                    background_color = f"rgba(0, 0, 255, {alpha})"  # Blue for spin down
                else:
                    text = ""
                    background_color = "rgba(255, 255, 255, 0)"  # Transparent for empty

                # Update cell display
                self.grid_cells[x][y].setText(text)
                self.grid_cells[x][y].setStyleSheet(f"background-color: {background_color}; border: 1px solid black;")

    def highlight_cell(self, x, y, color):
        """
        Highlight a specific cell in the grid with a border color, preserving the background color.
        """
        if 0 <= x < self.LATTICE_SIZE and 0 <= y < self.LATTICE_SIZE:
            current_style = self.grid_cells[x][y].styleSheet()
            updated_style = ";".join(
                part for part in current_style.split(";") if not part.strip().startswith("border")
            )
            self.grid_cells[x][y].setStyleSheet(f"{updated_style}; border: 2px solid {color};")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
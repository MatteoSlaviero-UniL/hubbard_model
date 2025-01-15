import numpy as np
import random

class Hubbard:
    def __init__(self, size=5, u=1.0, t=1.0, num_electrons=10, seed=42):
        """
        Initialize the Hubbard model simulation.
        :param size: Size of the NxN lattice.
        :param u: On-site repulsion parameter.
        :param t: Hopping parameter.
        :param num_electrons: Total number of electrons (half up, half down).
        :param seed: Random seed for reproducibility.
        """
        self.size = size
        self.u = u
        self.t = t
        self.num_electrons = num_electrons
        self.seed = seed
        self.electric_field_strength = 0.0
        self.lattice = None
        self.left = 0
        self.right = 1
        random.seed(seed)
        np.random.seed(seed)

    def initialize_lattice(self):
        """
        Initializes the lattice with random placement of electrons.
        Each site can have at most one up and one down electron.
        """
        self.lattice = np.zeros((2, self.size, self.size), dtype=int)  # 2 layers: up (0), down (1)
        electrons_placed = 0

        while electrons_placed < min(self.num_electrons, 2 * self.size **2):
            x, y = np.random.randint(0, self.size, size=2)
            spin = np.random.choice([0, 1])  # 0 for up, 1 for down
            if self.lattice[spin, x, y] == 0:  # Place if empty
                self.lattice[spin, x, y] = 1
                electrons_placed += 1

    def initialize_af(self):
        """
        Initialize the lattice in an antiferromagnetic configuration.
        Alternating spins (up and down) throughout the lattice.
        If the lattice size is odd, print an error and do not initialize.
        """
        if self.size % 2 != 0:
            print("Error: Lattice size must be even for antiferromagnetic initialization.")
            return

        self.lattice = np.zeros((2, self.size, self.size), dtype=int)
        for x in range(self.size):
            for y in range(self.size):
                spin = (x + y) % 2  # Alternating spins
                self.lattice[spin, x, y] = 1


    def initialize_localized(self):
        """
        Initialize the lattice in a localized configuration.
        Top half of the lattice is fully occupied.
        """
        self.lattice = np.zeros((2, self.size, self.size), dtype=int)
        mid = self.size // 2
        for x in range(self.size):
            for y in range(mid):
                self.lattice[0, x, y] = 1  # Up electron
                self.lattice[1, x, y] = 1  # Down electron

    def get_lattice(self):
        """
        Returns the current state of the lattice.
        """
        if self.lattice is None:
            raise ValueError("Lattice has not been initialized.")
        return self.lattice

    def simulate_step(self):
        """
        Perform a single Metropolis step.
        :return: Tuple (success, (x, y), spin, (target_x, target_y)).
        """
        if self.lattice is None:
            raise ValueError("Lattice has not been initialized.")

        # Select a random occupied site
        occupied_sites = np.argwhere(self.lattice > 0)
        if occupied_sites.size == 0:
            return False, None, None, None

        site_idx = np.random.randint(len(occupied_sites))
        spin, x, y = occupied_sites[site_idx]

        # Choose a random neighbor (periodic boundary conditions)
        if random.random() < self.electric_field_strength:
            # Bias towards right movement
            neighbors = [(0, 1), (0, -1), (1, 0), (1, 0)]  # Two (1, 0) for bias
        else:
            neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        dx, dy = random.choice(neighbors)
        target_x = (x + dx) % self.size
        target_y = (y + dy) % self.size

        if target_x > x:
            self.right +=1
        elif target_x < x:
            self.left +=1

        print(f"Left: {self.left}, Right: {self.right}")

        # Check target site
        target_spin = spin
        target_state = self.lattice[target_spin, target_x, target_y]

        if target_state == 1:  # Same spin at target, step fails
            return False, (x, y), spin, (target_x, target_y)

        # Energy difference calculation
        companion_start = self.lattice[1 - spin, x, y]
        companion_target = self.lattice[1 - spin, target_x, target_y]
        delta_energy = 0

        if companion_start == 1:  # Start with companion
            delta_energy -= self.u
        if companion_target == 1:  # Target has companion
            delta_energy += self.u

        # Metropolis condition
        if delta_energy < 0 or random.random() < np.exp(-delta_energy / self.t):
            # Perform the move
            self.lattice[spin, x, y] = 0
            self.lattice[spin, target_x, target_y] = 1
            return True, (x, y), spin, (target_x, target_y)

        # Step fails
        return False, (x, y), spin, (target_x, target_y)

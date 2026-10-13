class EnvSimulation:
    """Environnement d'apprentissage par renforcement pour le feu "C" du carrefour.

    Actions : 0 = garder la phase verte actuelle, 1 = basculer vers l'autre.
    État    : niveau de file d'attente de chaque branche + phase verte actuelle.
    Récompense : - nombre de véhicules arrêtés (à chaque seconde simulée).
    """

    TLS = "C"
    EDGES = ["N2C", "S2C", "E2C", "O2C"]
    GREEN = [0, 2]          # index des phases vertes dans le programme du feu
    YELLOW_TIME = 3         # durée du jaune (s)
    MIN_GREEN = 5           # durée minimale d'un vert avant de pouvoir basculer (s)
    DECISION_STEPS = 5      # secondes simulées entre deux décisions de l'agent

    def __init__(self, config, runner):
        self.config = config
        self.runner = runner
        self.api = runner.api
        self.running = False

    # --- Baseline : feu fixe, sans agent ---

    def run_simulation(self):
        """Exécute la configuration SUMO avec son feu fixe et affiche les statistiques."""
        self._start()
        try:
            edges = [edge for edge in self.api.edge.getIDList() if not edge.startswith(":")]
            while self.api.simulation.getMinExpectedNumber() > 0:
                self.api.simulationStep()
                t = self.api.simulation.getTime()
                if t % 300 == 0:
                    attente = sum(self.api.edge.getWaitingTime(edge) for edge in edges)
                    print(f"t={t:.0f}s  véhicules={self.api.vehicle.getIDCount()}  attente={attente:.0f}s")
        finally:
            self.close()

    # --- Interface d'apprentissage ---

    def reset(self):
        """Relance la simulation et renvoie l'état initial."""
        self.close()
        self._start()
        self.green = 0              # index dans GREEN
        self.time_in_green = 0
        self._set_phase(self.GREEN[self.green])
        return self.get_state()

    def step(self, action):
        """Applique l'action, avance la simulation et renvoie (état, récompense, terminé)."""
        reward = 0
        if action == 1 and self.time_in_green >= self.MIN_GREEN:
            reward += self._switch()
        reward += self._advance(self.DECISION_STEPS)
        done = self.api.simulation.getMinExpectedNumber() == 0
        return self.get_state(), reward, done

    def get_state(self):
        """Tuple (niveau N, S, E, O, phase verte) utilisable comme clé de Q-table."""
        queues = tuple(self._level(self.api.edge.getLastStepHaltingNumber(e)) for e in self.EDGES)
        return queues + (self.green,)

    def close(self):
        if self.running:
            self.runner.close()
            self.running = False

    # --- Méthodes internes ---

    def _start(self):
        self.runner.start(self.config)
        self.running = True

    @staticmethod
    def _level(n):
        """0 = vide, 1 = faible, 2 = moyen, 3 = saturé."""
        return 0 if n == 0 else 1 if n <= 3 else 2 if n <= 7 else 3

    def _advance(self, seconds):
        """Avance de `seconds` pas et renvoie la récompense cumulée."""
        reward = 0
        for _ in range(seconds):
            self.api.simulationStep()
            self.time_in_green += 1
            reward -= sum(self.api.edge.getLastStepHaltingNumber(e) for e in self.EDGES)
        return reward

    def _switch(self):
        """Passe par le jaune puis active l'autre phase verte."""
        self._set_phase(self.GREEN[self.green] + 1)     # 0 -> 1, 2 -> 3
        reward = self._advance(self.YELLOW_TIME)
        self.green = 1 - self.green
        self._set_phase(self.GREEN[self.green])
        self.time_in_green = 0
        return reward

    def _set_phase(self, phase):
        """Force la phase et empêche SUMO de la changer tout seul."""
        self.api.trafficlight.setPhase(self.TLS, phase)
        self.api.trafficlight.setPhaseDuration(self.TLS, 1000)

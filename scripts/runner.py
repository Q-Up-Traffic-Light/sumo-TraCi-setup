
class Runner:
    gui = False
    api = None

    def start(self, config):
        raise NotImplementedError

    def close(self):
        self.api.close()


class TraciRunner(Runner):
    def __init__(self, gui=False):
        import traci
        self.api = traci
        self.gui = gui

    def start(self, config):
        import sumolib
        SUMO = sumolib.checkBinary("sumo-gui" if self.gui else "sumo")
        cmd = [SUMO, "-c", str(config)]
        if self.gui:
            cmd += ["--start", "--delay", "100", "--quit-on-end"]

        self.api.start(cmd)


class libsumoRunner(Runner):
    def __init__(self, gui=False):
        import os, sumo
        os.add_dll_directory(os.path.join(sumo.SUMO_HOME, "bin"))
        import libsumo
        self.api = libsumo

    def start(self, config):
        import sumolib
        self.api.start([sumolib.checkBinary("sumo"), "-c", str(config)])
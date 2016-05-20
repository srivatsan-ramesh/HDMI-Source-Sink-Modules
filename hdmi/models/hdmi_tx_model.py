

class HDMITxModel:

    def __init__(self, clock, reset, video_interface, aux_interface, hdmi_interface):

        self.clock = clock
        self.reset = reset
        self.video_interface = video_interface
        self.aux_interface = aux_interface
        self.hdmi_interface = hdmi_interface

    def process(self):

        pass

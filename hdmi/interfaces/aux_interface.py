from myhdl import Signal, intbv


class AuxInterface:

    def __init__(self, clock, aux_depth=(4, 4, 4)):

        """
         This interface is the internal interface modeled after
         the xapp495 internal audio interface
        """

        self.clock = clock
        self.aux_depth = aux_depth

        # AUX data from audio source
        self.aux0 = Signal(intbv(0)[aux_depth[0]:])
        self.aux1 = Signal(intbv(0)[aux_depth[1]:])
        self.aux2 = Signal(intbv(0)[aux_depth[2]:])

        # Audio data enable
        self.ade = Signal(bool(0))

    def write_aux(self, aux0, aux1, aux2):

        """
         Transactor for passing signals to audio interface
        """

        self.aux0.next = aux0
        self.aux1.next = aux1
        self.aux2.next = aux2

        yield self.clock.posedge

        # uncomment to see output
        # print(aux0, aux1, aux2)

    def read_aux(self):

        yield self.clock.posedge

    def get_aux_data(self):

        return self.aux0, self.aux1, self.aux2

    def enable_aux(self):

        self.ade = Signal(bool(1))

    def disable_aux(self):

        self.ade = Signal(bool(0))

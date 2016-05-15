from myhdl import Signal


class HDMIInterface:

    def __init__(self, clock):

        """
         This interface is the internal interface modeled after
         the xapp495 external HDMI interface
        """

        self.clock = clock

        # Differential TMDS output/input signals
        self.TMDS_R_P = Signal(bool(0))
        self.TMDS_R_N = Signal(bool(1))

        self.TMDS_G_P = Signal(bool(0))
        self.TMDS_G_N = Signal(bool(1))

        self.TMDS_B_P = Signal(bool(0))
        self.TMDS_B_N = Signal(bool(1))

        self.TMDS_CLK_P = Signal(bool(0))
        self.TMDS_CLK_N = Signal(bool(0))

    def _print_data(self):

        print('R+ : {} , R- : {}'.format(self.TMDS_R_P, self.TMDS_R_N))
        print('G+ : {} , G- : {}'.format(self.TMDS_G_P, self.TMDS_G_N))
        print('B+ : {} , B- : {}'.format(self.TMDS_B_P, self.TMDS_B_N))
        print('B+ : {} , B- : {}'.format(self.TMDS_CLK_P, self.TMDS_CLK_N))

    def write_data(self, TMDS_R, TMDS_G, TMDS_B, TMDS_CLK):

        """
         Write transactor for passing signals to external HDMI interface
        """

        self.TMDS_R_P.next = TMDS_R
        self.TMDS_G_P.next = TMDS_G
        self.TMDS_B_P.next = TMDS_B
        self.TMDS_CLK_P.next = TMDS_CLK
        self.TMDS_R_N.next = 0 if TMDS_R == 1 else 1
        self.TMDS_G_N.next = 0 if TMDS_G == 1 else 1
        self.TMDS_B_N.next = 0 if TMDS_B == 1 else 1
        self.TMDS_CLK_N.next = 0 if TMDS_CLK == 1 else 1

        yield self.clock.posedge

        # can be uncommented to see output
        # print('Write :')
        # self._print_data()

    def read_data(self):

        yield self.clock.posedge

        # can be uncommented to see output
        # print('Read :')
        # self._print_data()

    def get_TMDS_data(self):

        return (self.TMDS_R_P,
                self.TMDS_G_P,
                self.TMDS_B_P,
                self.TMDS_CLK_P)

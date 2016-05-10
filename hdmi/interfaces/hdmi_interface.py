from myhdl import Signal


class HDMIInterface:

    def __init__(self, TMDS_CLK_P, TMDS_CLK_N):

        """
         This interface is the internal interface modeled after
         the xapp495 external HDMI interface
        """

        # Differential TMDS output/input signals
        self.TMDS_R_P = Signal(0)
        self.TMDS_R_N = Signal(1)

        self.TMDS_G_P = Signal(0)
        self.TMDS_G_N = Signal(1)

        self.TMDS_B_P = Signal(0)
        self.TMDS_B_N = Signal(1)

        self.TMDS_CLK_P = TMDS_CLK_P
        self.TMDS_CLK_N = TMDS_CLK_N

    def _print_data(self):

        print('R+ : {} , R- : {}'.format(self.TMDS_R_P, self.TMDS_R_N))
        print('G+ : {} , G- : {}'.format(self.TMDS_G_P, self.TMDS_G_N))
        print('B+ : {} , B- : {}'.format(self.TMDS_B_P, self.TMDS_B_N))

    def write_data(self, TMDS_R, TMDS_G, TMDS_B):

        """
         Write transactor for passing signals to external HDMI interface
        """

        yield self.TMDS_CLK_P.posedge

        self.TMDS_R_P.next = TMDS_R
        self.TMDS_G_P.next = TMDS_G
        self.TMDS_B_P.next = TMDS_B
        self.TMDS_R_N.next = 0 if TMDS_R == 1 else 1
        self.TMDS_G_N.next = 0 if TMDS_G == 1 else 1
        self.TMDS_B_N.next = 0 if TMDS_B == 1 else 1

        # can be uncommented to see output
        # print('Write :')
        # self._print_data()

    def read_data(self):

        yield self.TMDS_CLK_P.posedge

        # can be uncommented to see output
        # print('Read :')
        # self._print_data()

    def get_TMDS_data(self):

        return (self.TMDS_R_P,
                self.TMDS_G_P,
                self.TMDS_B_P)
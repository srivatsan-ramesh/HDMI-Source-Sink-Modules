import itertools
from myhdl import Signal, instance, Simulation

from hdmi.interfaces import HDMIInterface
from hdmi.utils import clock_driver


def test_hdmi_interface():

    TMDS_CLK_P = Signal(0)
    TMDS_CLK_N = Signal(1)

    clk_drive_p = clock_driver(TMDS_CLK_P)
    clk_drive_n = clock_driver(TMDS_CLK_N)

    hdmi_interface = HDMIInterface(TMDS_CLK_P, TMDS_CLK_N)

    @instance
    def test():

        data = itertools.product([0, 1], repeat = 3)

        for TMDS_data in data:
            yield hdmi_interface.write_data(*TMDS_data)
            yield hdmi_interface.read_data()
            assert hdmi_interface.get_TMDS_data() == TMDS_data

    return clk_drive_p, clk_drive_n, test

test_instance = test_hdmi_interface()

sim = Simulation(test_instance)
sim.run(16)
sim.quit()

import itertools
from myhdl import Signal, instance, Simulation

from hdmi.interfaces import HDMIInterface
from hdmi.utils import clock_driver


def test_hdmi_interface():

    clock5x = Signal(bool(0))
    clock5x_not = Signal(bool(0))

    clk_drive = clock_driver(clock5x)
    clk_drive_not = clock_driver(clock5x_not)

    hdmi_interface = HDMIInterface(clock5x, clock5x_not)

    @instance
    def test():

        data = itertools.product([0, 1], repeat=4)

        for TMDS_data in data:
            yield hdmi_interface.write_data(*TMDS_data), \
                  hdmi_interface.read_data()
            assert hdmi_interface.get_TMDS_data() == TMDS_data

    return clk_drive, clk_drive_not, test

test_instance = test_hdmi_interface()

sim = Simulation(test_instance)
sim.run(16)
sim.quit()

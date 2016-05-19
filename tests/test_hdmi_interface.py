import itertools
from myhdl import Signal, instance, Simulation

from hdmi.interfaces import HDMIInterface
from hdmi.utils import clock_driver


def test_hdmi_interface():

    clock = Signal(bool(0))

    clk_drive = clock_driver(clock)

    hdmi_interface = HDMIInterface(clock)

    @instance
    def test():

        data = itertools.product([0, 1], repeat=4)

        for TMDS_data in data:
            yield hdmi_interface.write_data(*TMDS_data), \
                  hdmi_interface.read_data()
            assert hdmi_interface.get_TMDS_data() == TMDS_data

    return clk_drive, test

test_instance = test_hdmi_interface()

sim = Simulation(test_instance)
sim.run(16)
sim.quit()

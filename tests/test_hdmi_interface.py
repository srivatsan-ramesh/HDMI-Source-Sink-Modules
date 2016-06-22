import itertools
from myhdl import Signal, instance, block, instances

from hdmi.interfaces import HDMIInterface
from hdmi.utils import clock_driver


@block
def test_hdmi_interface():

    clock10x = Signal(bool(0))

    clk_drive = clock_driver(clock10x)

    hdmi_interface = HDMIInterface(clock10x)

    @instance
    def test():

        data = itertools.product([0, 1], repeat=4)

        for TMDS_data in data:
            yield hdmi_interface.write_data(*TMDS_data), \
                  hdmi_interface.read_data()
            assert hdmi_interface.get_TMDS_data() == TMDS_data

    return instances()

if __name__ == '__main__':
    test_instance = test_hdmi_interface()
    test_instance.run_sim(16)
    test_instance.quit_sim()

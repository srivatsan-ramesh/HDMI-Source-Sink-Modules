from myhdl import Signal, instance, Simulation, instances

from hdmi.interfaces import AuxInterface
from hdmi.utils import clock_driver


def test_aux_interface():

    aux_depth = (4, 4, 4)

    clock = Signal(0)
    clock_drive = clock_driver(clock)
    aux_interface = AuxInterface(clock, aux_depth)
    aux_data = (0, 0, 0)

    @instance
    def test():

        yield aux_interface.enable_aux()

        # I have no idea as to what to pass as auxiliary data
        yield aux_interface.write_aux(*aux_data), \
            aux_interface.read_aux()
        assert aux_interface.get_aux_data() == aux_data

        # AUX data can be updated here
        yield aux_interface.write_aux(*aux_data), \
            aux_interface.read_aux()
        assert aux_interface.get_aux_data() == aux_data

        yield aux_interface.disable_aux()

    return instances()

test_instance = test_aux_interface()

sim = Simulation(test_instance)
sim.run(8)
sim.quit()

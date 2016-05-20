from myhdl import instance, Simulation, Signal, ResetSignal

from hdmi.interfaces import VideoInterface, AuxInterface, HDMIInterface
from hdmi.models import HDMITxModel, HDMIRxModel
from hdmi.utils import clock_driver


def test_tmds_codec():

    clock = Signal(bool(0))
    reset = ResetSignal(0, True, False)

    video_interface_tx = VideoInterface(clock)
    aux_interface_tx = AuxInterface(clock)
    hdmi_interface_tx = HDMIInterface(clock)

    video_interface_rx = VideoInterface(clock)
    aux_interface_rx = AuxInterface(clock)
    hdmi_interface_rx = hdmi_interface_tx

    hdmi_tx_model = HDMITxModel(clock, reset, video_interface_tx, aux_interface_tx, hdmi_interface_tx)
    hdmi_rx_model = HDMIRxModel(clock, reset, video_interface_rx, aux_interface_rx, hdmi_interface_rx)
    clk = clock_driver(clock)
    video_data = int('10101010', 2)
    aux_data = (0, 1, 2)

    @instance
    def test():
        yield video_interface_tx.write_pixel(video_data)
        yield video_interface_rx.read_pixel()
        assert video_interface_rx.get_pixel() == video_data

        yield aux_interface_tx.write_aux(*aux_data)
        yield aux_interface_rx.read_aux()
        assert aux_interface_rx.get_aux_data() == aux_data

    return test, clk, hdmi_tx_model.process, hdmi_rx_model.process()

t = test_tmds_codec()
sim = Simulation(t)
sim.run(1000)

from myhdl import instance, Signal, ResetSignal, traceSignals, instances, block

from hdmi.interfaces import VideoInterface, AuxInterface, HDMIInterface
from hdmi.models import HDMITxModel, HDMIRxModel
from hdmi.utils import clock_driver

@block
def test_hdmi_model():

    clock, clock5x = [Signal(bool(0)) for _ in range(2)]
    clock5x_not = Signal(bool(1))
    reset = ResetSignal(0, True, False)

    video_interface_tx = VideoInterface(clock)
    aux_interface_tx = AuxInterface(clock)
    hdmi_interface_tx = HDMIInterface(clock5x, clock5x_not)

    video_interface_rx = VideoInterface(clock)
    aux_interface_rx = AuxInterface(clock)
    hdmi_interface_rx = hdmi_interface_tx

    hdmi_tx_model = HDMITxModel(clock, clock5x, clock5x_not, reset,
                                video_interface_tx, aux_interface_tx, hdmi_interface_tx)
    hdmi_rx_model = HDMIRxModel(video_interface_rx, aux_interface_rx, hdmi_interface_rx)

    clk = clock_driver(clock, 5)
    clk_5x = clock_driver(clock5x)
    clk_5x_not = clock_driver(clock5x_not)

    video_data = [int('10101010', 2)]*3
    aux_data = (10, 15, 10)
    hdmi_tx_inst = hdmi_tx_model.process()
    hdmi_tx_inst.name = 'tx_process'
    hdmi_rx_inst = hdmi_rx_model.process()
    hdmi_rx_inst.name = 'rx_process'

    @instance
    def test():
        yield video_interface_tx.disable_video(), aux_interface_tx.disable_aux()
        yield video_interface_tx.enable_video(), video_interface_tx.write_pixel(video_data)
        for _ in range(100):
            yield video_interface_tx.write_pixel(video_data)
        yield video_interface_tx.disable_video()
        for _ in range(10):
            yield clock.posedge
        yield aux_interface_tx.enable_aux(), aux_interface_tx.write_aux(*aux_data)
        for _ in range(20):
            yield aux_interface_tx.write_aux(*aux_data)
        yield aux_interface_tx.disable_aux()
        for _ in range(10):
            yield clock.posedge

    return clk, clk_5x, clk_5x_not, hdmi_tx_inst, hdmi_rx_inst, test

t = test_hdmi_model()
t.config_sim(trace=True)
t.run_sim(10000)

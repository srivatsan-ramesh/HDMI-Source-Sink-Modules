from myhdl import instance, Signal, ResetSignal, block, delay, StopSimulation

from hdmi.interfaces import VideoInterface, AuxInterface, HDMIInterface
from hdmi.models import HDMITxModel, HDMIRxModel
from hdmi.utils import clock_driver

@block
def test_hdmi_model():

    # Clock and reset signals
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

    clk = clock_driver(clock, 10)
    clk_5x = clock_driver(clock5x, 2)
    clk_5x_not = clock_driver(clock5x_not, 2)

    video_data = [int('10101010', 2)]*3
    aux_data = (10, 15, 10)
    hdmi_tx_inst = hdmi_tx_model.process()
    hdmi_tx_inst.name = 'tx_process'
    hdmi_rx_inst = hdmi_rx_model.process()
    hdmi_rx_inst.name = 'rx_process'

    # List which acts as a queue to store the input signals for 16 clock cycles
    input_signals = []

    def append_signals():

        """
        appends the current values of the signals in the Tx end to the list input_signals
        """

        input_signals.append([video_interface_tx.get_pixel(),
                              aux_interface_tx.get_aux_data()[1:], # Ignoring the data from aux0
                              video_interface_tx.get_vde(),
                              aux_interface_tx.get_ade()])

    def get_signals():

        """
        :return: the current values of the signals in the Rx end.
        """

        return [video_interface_rx.get_pixel(),
                aux_interface_rx.get_aux_data()[1:],  # Ignoring the data from aux0
                video_interface_rx.get_vde(),
                aux_interface_rx.get_ade()]

    @instance
    def assert_io():

        """
        Asserts whether the current output value and the input value before 16 clock cycles are equal
        """

        for _ in range(16):
            yield clock.posedge
        while True:
            yield delay(1)
            output_signal = get_signals()
            input_signal = input_signals.pop(0)
            assert input_signal == output_signal
            if len(input_signals) == 0:
                raise StopSimulation
            yield clock.posedge

    @instance
    def test():

        yield video_interface_tx.disable_video(), aux_interface_tx.disable_aux()
        append_signals()
        yield video_interface_tx.enable_video(), video_interface_tx.write_pixel(video_data)
        append_signals()
        for _ in range(100):
            yield video_interface_tx.write_pixel(video_data)
            append_signals()
        yield video_interface_tx.disable_video()
        append_signals()
        for _ in range(10):
            yield clock.posedge
            append_signals()
        yield aux_interface_tx.enable_aux(), aux_interface_tx.write_aux(*aux_data)
        append_signals()
        for _ in range(20):
            yield aux_interface_tx.write_aux(*aux_data)
            append_signals()
        yield aux_interface_tx.disable_aux()
        append_signals()
        for _ in range(10):
            yield clock.posedge
            append_signals()

    return clk, clk_5x, clk_5x_not, hdmi_tx_inst, hdmi_rx_inst, test, assert_io

t = test_hdmi_model()
t.run_sim()

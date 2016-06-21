import itertools
from myhdl import instance, Signal, ResetSignal, block, delay, StopSimulation, instances

from hdmi.cores.receiver import hdmi_decoder
from hdmi.cores.transmitter import hdmi_encoder
from hdmi.interfaces import VideoInterface, AuxInterface, HDMIInterface
from hdmi.utils import clock_driver


@block
def test_hdmi_core():
    # Clock and reset signals
    clock, clock2x, clock10x, serdes_strobe = [Signal(bool(0)) for _ in range(4)]
    reset = ResetSignal(0, True, False)

    video_interface_tx = VideoInterface(clock)
    aux_interface_tx = AuxInterface(clock)
    hdmi_interface_tx = HDMIInterface(clock10x)

    video_interface_rx = VideoInterface(clock)
    aux_interface_rx = AuxInterface(clock)
    hdmi_interface_rx = hdmi_interface_tx

    hdmi_tx_inst = hdmi_encoder(clock, clock2x, clock10x, reset, serdes_strobe,
                                video_interface_tx, aux_interface_tx, hdmi_interface_tx)
    hdmi_rx_inst = hdmi_decoder(reset, hdmi_interface_rx, video_interface_rx, aux_interface_rx)

    clk = clock_driver(clock, 10)
    clk_2x = clock_driver(clock2x, 5)
    clk_10x = clock_driver(clock10x, 1)

    video_source = itertools.product(['0', '1'], repeat=8)
    aux_data = (10, 15, 10)

    # List which acts as a queue to store the input signals for 16 clock cycles
    input_signals = []

    def append_signals():

        """
        Appends the current values of the signals in the Tx end to the list input_signals
        """

        input_signals.append([video_interface_tx.get_pixel(),
                              aux_interface_tx.get_aux_data()[1:],  # Ignoring the data from aux0
                              video_interface_tx.get_vde(),
                              aux_interface_tx.get_ade()])

    def get_signals():

        """
        Returns:
            the current values of the signals in the Rx end.
        """

        return [video_interface_rx.get_pixel(),
                aux_interface_rx.get_aux_data()[1:],  # Ignoring the data from aux0
                video_interface_rx.get_vde(),
                aux_interface_rx.get_ade()]

    @instance
    def assign_strobe():

        yield clock10x.posedge
        while True:
            for _ in range(4):
                yield clock10x.posedge
            serdes_strobe.next = 1
            yield clock10x.posedge
            serdes_strobe.next = 0

    @instance
    def assert_io():

        """
        Asserts whether the current output value and the input value before 16 clock cycles are equal
        """

        for _ in range(19):
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
        video_data = [int(''.join(next(video_source)), 2) for _ in range(3)]
        yield video_interface_tx.enable_video(), video_interface_tx.write_pixel(video_data)
        append_signals()
        for _ in range(83):
            video_data = [int(''.join(next(video_source)), 2) for __ in range(3)]
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

    return instances()

t = test_hdmi_core()
t.run_sim()

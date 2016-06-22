from myhdl import instance, Signal, ResetSignal, block, StopSimulation, instances

from hdmi.cores.receiver import hdmi_decoder
from hdmi.cores.transmitter import hdmi_encoder
from hdmi.interfaces import VideoInterface, AuxInterface, HDMIInterface
from hdmi.utils import clock_driver

import pytest


@block
def core_conversion_testbench():
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

    video_source = (155, 244, 134)
    aux_data = (10, 15, 10)

    @instance
    def test():

        yield clock.posedge
        video_interface_tx.vde.next = True
        video_interface_tx.blue.next = video_source[0]
        video_interface_tx.green.next = video_source[1]
        video_interface_tx.red.next = video_source[2]
        yield clock.posedge
        video_interface_tx.vde.next = False
        yield clock.posedge
        for _ in range(20):
            yield clock.posedge
        print(video_interface_rx.red, video_interface_rx.green, video_interface_rx.blue)
        aux_interface_tx.ade.next = True
        aux_interface_tx.aux0.next = aux_data[0]
        aux_interface_tx.aux1.next = aux_data[1]
        aux_interface_tx.aux2.next = aux_data[2]
        yield clock.posedge
        aux_interface_tx.ade.next = False
        yield clock.posedge
        for _ in range(20):
            yield clock.posedge
        print(aux_interface_rx.aux0, aux_interface_rx.aux1, aux_interface_rx.aux2)
        raise StopSimulation

    return instances()


@pytest.mark.xfail
def test_core_conversion():
    t = core_conversion_testbench()
    assert t.verify_convert() == True


if __name__ == '__main__':
    test_core_conversion()

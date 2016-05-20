from myhdl import instance, Simulation, delay, always, Signal, ResetSignal

from hdmi.models import HDMITxModel, HDMIRxModel


def clock_driver(clock, d=1):

    half_period = delay(d)

    @always(half_period)
    def drive_clock():
        clock.next = not clock

    return drive_clock


def test_tmds_codec():

    clock = Signal(bool(0))
    reset = ResetSignal(0, True, False)

    hdmi_tx_model = HDMITxModel(clock, reset) # incomplete
    hdmi_rx_model = HDMIRxModel(clock, reset)
    clk = clock_driver(clock)
    video_data = int('10101010', 2)

    @instance
    def test():
        pass
    return test, clk, hdmi_tx_model.process, hdmi_rx_model.process()

t = test_tmds_codec()
sim = Simulation(t)
sim.run(1000)

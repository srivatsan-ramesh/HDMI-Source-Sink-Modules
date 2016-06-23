from myhdl import block, instance, instances

from hdmi.utils import clock_driver

inst_count = 0


@block
def pll_clock_generator(clock_feedback_out, pll_clock0, pll_clock1, pll_clock2,
                        pll_locked, clock_feedback_in, clock, reset, clock_fb_out_mult=10,
                        clock0_divide=1, clock1_divide=10, clock2_divide=5):

    """

    A block that generates clocks of three different frequencies and will be used by the
    receiver core. This will be replaced by the xilinx primitive PLL_BASE during conversion.

    Args:
        clock_feedback_out: A feedback signal
        pll_clock0: clock generated with time period 2*clock0_divide
        pll_clock1: clock generated with time period 2*clock1_divide
        pll_clock2: clock generated with time period 2*clock2_divide
        pll_locked: A signal denoting that the phase is locked
        clock_feedback_in: Input feedback signal
        clock: global clock
        reset: reset signal
        clock_fb_out_mult: The value to be multiplied with global clock frequency
        clock0_divide: The value to be divided from clock_fb_out_mult to get the frequency
        clock1_divide: The value to be divided from clock_fb_out_mult to get the frequency
        clock2_divide: The value to be divided from clock_fb_out_mult to get the frequency

    Returns:
        myhdl.instances() : A list of myhdl instances.

    """

    global inst_count
    clock0_inst = clock_driver(pll_clock0, clock0_divide)
    clock1_inst = clock_driver(pll_clock1, clock1_divide)
    clock2_inst = clock_driver(pll_clock2, clock2_divide)

    @instance
    def initialize():
        pll_locked.next = 1
        yield clock.posedge

    inst_count += 1

    return instances()

pll_clock_generator.verilog_code = """
PLL_BASE # (
.CLKIN_PERIOD(10),
.CLKFBOUT_MULT($clock_fb_out_mult),
.CLKOUT0_DIVIDE($clock0_divide),
.CLKOUT1_DIVIDE($clock1_divide),
.CLKOUT2_DIVIDE($clock2_divide),
.COMPENSATION("INTERNAL")
) PLL_$inst_count (
.CLKFBOUT($clock_feedback_out),
.CLKOUT0($pll_clock0),
.CLKOUT1($pll_clock1),
.CLKOUT2($pll_clock2),
.CLKOUT3(),
.CLKOUT4(),
.CLKOUT5(),
.LOCKED($pll_locked),
.CLKFBIN($clock_feedback_in),
.CLKIN($clock),
.RST($reset)
);
"""


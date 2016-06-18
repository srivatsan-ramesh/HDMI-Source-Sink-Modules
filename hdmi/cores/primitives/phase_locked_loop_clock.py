from myhdl import block, instance, instances

from hdmi.utils import clock_driver

inst_count = 0


@block
def pll_clock_generator(clock_feedback_out, pll_clock0, pll_clock1, pll_clock2,
                        pll_locked, clock_feedback_in, clock, reset, clock_fb_out_mult=10,
                        clock0_divide=1, clock1_divide=10, clock2_divide=5):
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
    .CLKOUT1_DIVIDE($cock1_divide),
    .CLKOUT2_DIVIDE($cock2_divide),
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


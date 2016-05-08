from myhdl import Signal, intbv, always


class VideoIntf:

    color_depth = (8, 8, 8)

    def __init__(self, color_depth = (8, 8, 8)):

        self.color_depth = color_depth

        # RGB data from video source
        self.red = Signal(intbv(0)[color_depth[0]:])
        self.green = Signal(intbv(0)[color_depth[1]:])
        self.blue = Signal(intbv(0)[color_depth[2]:])

        # Video timing controls
        self.vsync = Signal(bool(0))
        self.hsync = Signal(bool(0))
        self.vde = Signal(bool(0))

    # Transactors for passing signals to video interface

    COLOR_BARS = (
            # r, g, b
            (1, 1, 1,),  # white
            (1, 1, 0,),  # yellow
            (0, 1, 1,),  # cyan
            (0, 1, 0,),  # green
            (1, 0, 1,),  # magenta
            (1, 0, 0,),  # red
            (0, 0, 1,),  # blue
            (0, 0, 0,),  # black
        )

    hpxl = 0
    vpxl = 0

    def write_video(self, clk, resolution = (640, 480)):

        # Generate color bars and sends it through the video interface
        @always(clk.posedge)
        def write():
            bar_index = self.hpxl // (resolution[0] // len(self.COLOR_BARS))
            color_max_value = map(lambda x : 2**x - 1, self.color_depth)
            pixel_value = [a*b for a,b in zip(color_max_value, self.COLOR_BARS[bar_index])]
            print(pixel_value)
            # setting the pixel xolor values
            self.red.next = Signal(intbv(pixel_value[0])[self.color_depth[0]:])
            self.green.next = Signal(intbv(pixel_value[1])[self.color_depth[1]:])
            self.blue.next = Signal(intbv(pixel_value[2])[self.color_depth[2]:])

            self.hpxl += 1
            if self.hpxl >= resolution[0]:
                self.hsync.next = Signal(bool(1))
                self.hpxl = 0
                self.vpxl += 1
            else:
                self.hsync.next = Signal(bool(0))
            if self.vpxl >= resolution[1]:
                self.vsync.next = Signal(bool(1))
                self.vpxl = 0
            else:
                self.vsync.next = Signal(bool(0))

        return write

    def reset_counter(self):

        self.hpxl = 0
        self.vpxl = 0

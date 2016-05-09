from myhdl import Signal, intbv


class VideoInterface:

    def __init__(self, clock, resolution=(640, 480), color_depth=(8, 8, 8)):

        """
         This interface is the internal interface modeled after the xapp495 internal video interface
        """

        self.clock = clock

        self.resolution = resolution
        self.color_depth = color_depth

        self.hpixel = 0
        self.vpixel = 0

        # RGB data from video source
        self.red = Signal(intbv(0)[color_depth[0]:])
        self.green = Signal(intbv(0)[color_depth[1]:])
        self.blue = Signal(intbv(0)[color_depth[2]:])

        # Video timing controls
        self.vsync = Signal(0)
        self.hsync = Signal(0)
        self.vde = Signal(0)

    def write_frame(self, frame):

        """
         Transactors for passing signals to video interface
        """

        for pixel in frame:
            yield self.clock.posedge
            color_max_value = map(lambda x: 2 ** x - 1, self.color_depth)
            pixel = [int(a * b) for a, b in zip(color_max_value, pixel)]
            self.red.next = pixel[0]
            self.green.next = pixel[1]
            self.blue.next = pixel[2]

            # uncomment to see output
            print(self.red, self.green, self.blue)

            self.hpixel += 1
            if self.hpixel >= self.resolution[0]:
                self.hsync.next = 1
                self.hpixel = 0
                self.vpixel += 1
            else:
                self.hsync.next = 0
            if self.vpixel >= self.resolution[1]:
                self.vsync.next = 1
                self.vpixel = 0
            else:
                self.vsync.next = 0

    def reset_cursor(self):

        self.hpixel, self.vpixel = 0, 0

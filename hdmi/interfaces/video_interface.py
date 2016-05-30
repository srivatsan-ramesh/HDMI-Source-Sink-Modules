from myhdl import Signal, intbv


class VideoInterface:

    def __init__(self, clock, resolution=(640, 480), color_depth=(8, 8, 8)):

        """
         This interface is the internal interface modeled after
         the xapp495 internal video interface

         Args:
             :param clock: pixel clock
             :param resolution (optional): Resolution of the video to be transmitted or received.
                                           Default value: (640, 480)
             :param color_depth (optional): The bus width of each channel of the video
                                            Default value: (8, 8, 8)

         Usage:
            video_interface = VideoInterface()

        """

        self.clock = clock

        self.resolution = resolution
        self.color_depth = color_depth
        self.pixel = [0, 0, 0]

        self.hpixel = 0 # column number of the current pixel
        self.vpixel = 0 # row number of the current pixel

        # RGB data from video source
        self.red = Signal(intbv(0)[color_depth[0]:])
        self.green = Signal(intbv(0)[color_depth[1]:])
        self.blue = Signal(intbv(0)[color_depth[2]:])

        # Video timing controls
        self.vsync = Signal(bool(0))
        self.hsync = Signal(bool(0))

        # Video data enable
        self.vde = Signal(bool(0))

    def write_pixel(self, pixel):

        """
         Write transactor for passing signals to video interface

         Args:
            :param pixel: The pixel value is a tuple (R, G, B)

         Usage:
            # Values passed should be non negative integers less than 2**color_depth[i]
            video_interface.write_pixel(3, 4, 5)

        """

        self.pixel = pixel
        self.red.next = pixel[0]
        self.green.next = pixel[1]
        self.blue.next = pixel[2]

        # uncomment to see output
        # print(self.red, self.green, self.blue)

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

        yield self.clock.posedge

    def read_pixel(self):

        yield self.clock.posedge

    def get_pixel(self):

        """
        :return: pixel values R, G, B
        """

        return [self.red.val[:], self.green.val[:], self.blue.val[:]]

    def reset_cursor(self):

        """
        Resets the horizontal and vertical counters to 0.
        """

        self.hpixel, self.vpixel = 0, 0

    def enable_video(self):

        """
        Makes the VDE signal 1
        """

        self.vde.next = 1
        yield self.clock.posedge

    def disable_video(self):

        """
        Makes the VDE signal 0
        """

        self.vde.next = 0
        yield self.clock.posedge

    def get_vde(self):

        """
        :return: returns the VDE signal
        """

        return self.vde.val

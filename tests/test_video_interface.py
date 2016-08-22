from myhdl import Signal, block, instance, instances

from hdmi.interfaces import VideoInterface
from hdmi.utils import clock_driver


@block
def test_video_interface():

    # resolution of the video is kept low to reduce simulation time
    res = (50, 50)

    # a sample pixel
    pixel = [1, 0, 0]

    clock = Signal(bool(0))
    clock_drive = clock_driver(clock)

    video_interface = VideoInterface(clock, res)

    @instance
    def test():

        video_interface.reset_cursor()
        yield video_interface.enable_video()

        # iterating over the frame
        for _ in range(res[0]*res[1]):
            # Sending a pixel
            yield video_interface.write_pixel(pixel), \
                video_interface.read_pixel()
            assert video_interface.get_pixel() == pixel

        yield video_interface.disable_video()

    return instances()

test_inst = test_video_interface()
test_inst.run_sim(10000)
test_inst.quit_sim()

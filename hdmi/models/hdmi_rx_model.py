from myhdl import Signal, always_comb, intbv, always, ConcatSignal, instance, block

from hdmi.models import DecoderModel


class HDMIRxModel:

    def __init__(self, video_interface, aux_interface, hdmi_interface):

        """
        A non-convertible HDMI Transmitter Model which encodes the input video and AUX data and transmits it.
        This is modelled after the xapp495 HDMI Tx module.

        Args:
            :param video_interface: An instance of the VideoInterface class
            :param aux_interface: An instance of the AUXInterface class
            :param hdmi_interface: An instance of the HDMIInterface class

        Usage:
            hdmi_rx_model = HDMIRxModel(*params)
            process_inst = hdmi_rx_model.process()
            process_inst.run_sim()
        """

        self.video_interface = video_interface
        self.aux_interface = aux_interface
        self.hdmi_interface = hdmi_interface

    @block
    def process(self):

        """
        It simulates the process of the receiving data by the HDMI receiver.

        Usage:
            process_inst = hdmi_rx_model.process()
            process_inst.run_sim()
        """

        red = Signal(intbv(0)[10:0])
        green = Signal(intbv(0)[10:0])
        blue = Signal(intbv(0)[10:0])

        video_preamble = Signal(bool(0))
        data_island_preamble = Signal(bool(0))

        # control signals for different channels
        r_c0, g_c0, b_c0 = [Signal(bool(0)) for _ in range(3)]
        r_c1, g_c1, b_c1 = [Signal(bool(0)) for _ in range(3)]
        r_vde, g_vde, b_vde = [Signal(bool(0)) for _ in range(3)]
        r_ade, g_ade, b_ade = [Signal(bool(0)) for _ in range(3)]

        red_decoder = DecoderModel(self.hdmi_interface.TMDS_CLK_P, red, video_preamble, data_island_preamble,
                                   r_c0, r_c1, r_vde, r_ade,
                                   self.video_interface.red, self.aux_interface.aux2, channel='RED')
        green_decoder = DecoderModel(self.hdmi_interface.TMDS_CLK_P, green, video_preamble, data_island_preamble,
                                     g_c0, g_c1, g_vde, g_ade,
                                     self.video_interface.green, self.aux_interface.aux1, channel='GREEN')
        blue_decoder = DecoderModel(self.hdmi_interface.TMDS_CLK_P, blue, video_preamble, data_island_preamble,
                                    b_c0, b_c1, b_vde, b_ade,
                                    self.video_interface.blue, self.aux_interface.aux0, channel='BLUE')

        red_decoder_inst = red_decoder.process()
        red_decoder_inst.name = 'red_decoder'
        green_decoder_inst = green_decoder.process()
        green_decoder_inst.name = 'green_decoder'
        blue_decoder_inst = blue_decoder.process()
        blue_decoder_inst.name = 'blue_decoder'

        @always_comb
        def continuous_assignment():
            self.video_interface.vde.next = r_vde
            self.aux_interface.ade.next = r_ade
            self.video_interface.hsync.next = self.aux_interface.aux0[0] if b_ade else b_c0
            self.video_interface.vsync.next = self.aux_interface.aux0[1] if b_ade else b_c1

        @always(self.hdmi_interface.TMDS_CLK_P.posedge)
        def sequential():
            control = ConcatSignal(g_c0, g_c1, r_c0, r_c1)
            video_preamble.next = 1 if control == int('1000', 2) else 0
            data_island_preamble.next = 1 if control == int('1010', 2) else 0

        red_list = ['0' for _ in range(10)]
        green_list = ['0' for _ in range(10)]
        blue_list = ['0' for _ in range(10)]

        # Deserialize the parallel serial input
        @instance
        def deserialize():
            while True:
                data = self.hdmi_interface.get_TMDS_data()
                yield self.hdmi_interface.read_data()
                # print('rx : ', self.hdmi_interface.get_TMDS_data(), now())
                red_list.append('1' if data[0] else '0')
                green_list.append('1' if data[1] else '0')
                blue_list.append('1' if data[2] else '0')
                red_list.pop(0)
                green_list.pop(0)
                blue_list.pop(0)

        @instance
        def assign():
            while True:
                yield red_decoder.write_data(int(''.join(red_list[::-1]), 2)), \
                      green_decoder.write_data(int(''.join(green_list[::-1]), 2)), \
                      blue_decoder.write_data(int(''.join(blue_list[::-1]), 2))

        return continuous_assignment, sequential, assign, deserialize, \
            red_decoder_inst, green_decoder_inst, blue_decoder_inst

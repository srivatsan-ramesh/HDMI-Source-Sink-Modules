from myhdl import Signal, intbv


class AuxInterface:

    def __init__(self, clock, aux_depth=(4, 4, 4)):

        """

         This interface is the internal interface modeled after
         the xapp495 internal audio interface

         Args:
             clock: pixel clock.
             aux_depth (optional): The bus width of the aux interface
                                          Default value: (4, 4, 4)

        Usage:
            aux_interface = AuxInterface()

        """

        self.clock = clock
        self.aux_depth = aux_depth

        # AUX data from audio source
        self.aux0 = Signal(intbv(0)[aux_depth[0]:])
        self.aux1 = Signal(intbv(0)[aux_depth[1]:])
        self.aux2 = Signal(intbv(0)[aux_depth[2]:])

        # Audio data enable
        self.ade = Signal(bool(0))

    def write_aux(self, aux0, aux1, aux2):

        """

         Transactor for passing signals to audio interface

         Args:
             aux0: The auxiliary data(usually audio data)
             aux1: The auxiliary data(usually audio data)
             aux2: The auxiliary data(usually audio data)

         Usage:
            # Values passed should be non negative integers less than 2**aux_depth[i]
            yield aux_interface.write_aux(2, 2, 2)

        """

        self.aux0.next = aux0
        self.aux1.next = aux1
        self.aux2.next = aux2

        yield self.clock.posedge

        # uncomment to see output
        # print(aux0, aux1, aux2)

    def read_aux(self):

        yield self.clock.posedge

    def get_aux_data(self):

        """

        Returns:
            A tuple of aux signal values

        """

        return self.aux0.val[:], self.aux1.val[:], self.aux2.val[:]

    def enable_aux(self):

        """

        Makes the ADE signal 1

        """

        self.ade.next = 1
        yield self.clock.posedge

    def disable_aux(self):

        """

        Makes the ADE signal 0

        """

        self.ade.next = 0
        yield self.clock.posedge

    def get_ade(self):

        """

        Returns:
            ADE signal value

        """

        return self.ade.val

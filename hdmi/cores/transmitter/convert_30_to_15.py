from myhdl import Signal, intbv, always, always_comb, block

from hdmi.cores.primitives import DRAM16XN


@block
def convert_30_to_15(reset, clock, clockx2, data_in, tmds_data2, tmds_data1, tmds_data0):

    # RAM Address
    write_addr, _write_addr, read_addr, _read_addr = [Signal(intbv(0)[4:0]) for _ in range(4)]

    data_int = Signal(intbv(0)[30:0])

    address = range(6)

    @always(write_addr)
    def case_wa():

        if write_addr < 15:
            _write_addr.next = address[write_addr] + 1
        else:
            _write_addr.next = 0

    @always(clock.posedge, reset.posedge)
    def fdc():
        if reset:
            write_addr.next = 0
        else:
            write_addr.next = _write_addr

    o_data_out = Signal(intbv(0)[30:0])     # Dummy variable
    fifo_u = DRAM16XN(data_in, write_addr, read_addr, Signal(True), clock, o_data_out, data_int)

    @always(read_addr)
    def case_ra():

        if read_addr < 15:
            _read_addr.next = address[read_addr] + 1
        else:
            _read_addr.next = 0

    reset_sync, _reset_sync, reset_p = [Signal(bool(0)) for _ in range(3)]

    sync = Signal(bool(0))

    @always(clockx2.posedge, reset.posedge)
    def fdp():
        if reset:
            reset_sync.next = 1
        else:
            reset_sync.next = reset

    @always(clockx2.posedge)
    def fdr():
        if reset_p:
            sync.next = 0
        else:
            sync.next = not sync

    @always(clockx2.posedge)
    def fdre():
        if reset_p:
            read_addr.next = 0
        elif sync:
            read_addr.next = _read_addr

    db = Signal(intbv(0)[30:0])

    @always(clockx2.posedge)
    def fde():
        if sync:
            db.next = data_int

    mux = Signal(intbv(0)[15:0])

    @always_comb
    def mux_logic():
        if not sync:
            mux.next = db[15:0]
        else:
            mux.next = db[30:15]

    @always(clockx2.posedge)
    def fd():
        _reset_sync.next = reset_sync
        reset_p.next = _reset_sync
        tmds_data0.next = mux[5:0]
        tmds_data1.next = mux[10:5]
        tmds_data2.next = mux[15:10]

    return fd, fdc, fde, fdp, fdr, fdre, mux_logic, fifo_u

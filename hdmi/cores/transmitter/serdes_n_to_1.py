from myhdl import block, instance, delay

count = 0


@block
def serdes_n_to_1(io_clock, serdes_strobe, reset, g_clock, data_in, iob_data_out, factor=8):
    global count

    @instance
    def serialize():
        i = 0

        yield g_clock.posedge
        iob_data_out.next = data_in[i]
        i += 1

        while True:
            yield io_clock.posedge, reset.posedge
            yield delay(1)
            if reset:
                iob_data_out.next = 0
                i = 0
            else:
                iob_data_out.next = data_in[i]
                i += 1
                if i == factor:
                    i = 0

    count += 1
    return serialize


serdes_n_to_1.verilog_code = """

wire		cascade_di_$count ;
wire		cascade_do_$count ;
wire		cascade_ti_$count ;
wire		cascade_to_$count ;
wire	[8:0]	mdatain_$count ;

genvar j_$count ;

generate
    for (j_$count = 0 ; j_$count <= ($factor - 1) ; j_$count = j_$count + 1)
    begin : loop0_$count
        assign mdatain_$count[j_$count] = $data_in[j_$count] ;
    end
endgenerate

generate
    for (j_$count = ($factor) ; j_$count <= 8 ; j_$count = j_$count + 1)
    begin : loop1_$count
        assign mdatain_$count[j_$count] = 1'b0 ;
    end
endgenerate

OSERDES2 #(
    .DATA_WIDTH     	($factor),
    .DATA_RATE_OQ      	("SDR"),
    .DATA_RATE_OT      	("SDR"),
    .SERDES_MODE    	("MASTER"),
    .OUTPUT_MODE 		("DIFFERENTIAL"))
oserdes_m_$count (
    .OQ       		($iob_data_out),
    .OCE     		(1'b1),
    .CLK0    		($io_clock),
    .CLK1    		(1'b0),
    .IOCE    		($serdes_strobe),
    .RST     		($reset),
    .CLKDIV  		($g_clock),
    .D4  			(mdatain_$count[7]),
    .D3  			(mdatain_$count[6]),
    .D2  			(mdatain_$count[5]),
    .D1  			(mdatain_$count[4]),
    .TQ  			(),
    .T1 			(1'b0),
    .T2 			(1'b0),
    .T3 			(1'b0),
    .T4 			(1'b0),
    .TRAIN    		(1'b0),
    .TCE	   		(1'b1),
    .SHIFTIN1 		(1'b1),			// Dummy input in Master
    .SHIFTIN2 		(1'b1),			// Dummy input in Master
    .SHIFTIN3 		(cascade_do_$count),		// Cascade output D data from slave
    .SHIFTIN4 		(cascade_to_$count),		// Cascade output T data from slave
    .SHIFTOUT1 		(cascade_di_$count),		// Cascade input D data to slave
    .SHIFTOUT2 		(cascade_ti_$count),		// Cascade input T data to slave
    .SHIFTOUT3 		(),			// Dummy output in Master
    .SHIFTOUT4 		()) ;			// Dummy output in Master

OSERDES2 #(
    .DATA_WIDTH     	($factor),
    .DATA_RATE_OQ      	("SDR"),
    .DATA_RATE_OT      	("SDR"),
    .SERDES_MODE    	("SLAVE"),
    .OUTPUT_MODE 		("DIFFERENTIAL"))
oserdes_s_$count (
    .OQ       		(),
    .OCE     		(1'b1),
    .CLK0    		($io_clock),
    .CLK1    		(1'b0),
    .IOCE    		($serdes_strobe),
    .RST     		($reset),
    .CLKDIV  		($g_clock),
    .D4  			(mdatain_$count[3]),
    .D3  			(mdatain_$count[2]),
    .D2  			(mdatain_$count[1]),
    .D1  			(mdatain_$count[0]),
    .TQ  			(),
    .T1 			(1'b0),
    .T2 			(1'b0),
    .T3  			(1'b0),
    .T4  			(1'b0),
    .TRAIN 			(1'b0),
    .TCE	 		(1'b1),
    .SHIFTIN1 		(cascade_di_$count),		// Cascade input D from Master
    .SHIFTIN2 		(cascade_ti_$count),		// Cascade input T from Master
    .SHIFTIN3 		(1'b1),			// Dummy input in Slave
    .SHIFTIN4 		(1'b1),			// Dummy input in Slave
    .SHIFTOUT1 		(),			// Dummy output in Slave
    .SHIFTOUT2 		(),			// Dummy output in Slave
    .SHIFTOUT3 		(cascade_do_$count),   	// Cascade output D data to Master
    .SHIFTOUT4 		(cascade_to_$count)) ; 	// Cascade output T data to Master
"""

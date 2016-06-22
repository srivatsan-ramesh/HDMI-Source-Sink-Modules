from myhdl import block

from hdmi.cores.primitives import ram16x1d

inst_count = 0

@block
def dram16xn(data_in, address, address_dp, write_enable, clock,
             o_data_out, o_data_out_dp, data_width=30):

    global inst_count
    ram16x1d_inst = ram16x1d(data_in, write_enable, clock, address, address_dp, o_data_out, o_data_out_dp, data_width)
    inst_count += 1
    return ram16x1d_inst

dram16xn.verilog_code = """
genvar i_$inst_count;
generate
  for(i_$inst_count = 0 ; i_$inst_count < $data_width ; i_$inst_count = i_$inst_count + 1) begin : dram16s_$inst_count
    RAM16X1D i_RAM16X1D_U_$inst_count(
      .D($data_in[i_$inst_count]),        //insert input signal
      .WE($write_enable),         //insert Write Enable signal
      .WCLK($clock),            //insert Write Clock signal
      .A0($address[0]),       //insert Address 0 signal port SPO
      .A1($address[1]),       //insert Address 1 signal port SPO
      .A2($address[2]),       //insert Address 2 signal port SPO
      .A3($address[3]),       //insert Address 3 signal port SPO
      .DPRA0($address_dp[0]), //insert Address 0 signal dual port DPO
      .DPRA1($address_dp[1]), //insert Address 1 signal dual port DPO
      .DPRA2($address_dp[2]), //insert Address 2 signal dual port DPO
      .DPRA3($address_dp[3]), //insert Address 3 signal dual port DPO
      .SPO($o_data_out[i_$inst_count]),   //insert output signal SPO
      .DPO($o_data_out_dp[i_$inst_count]) //insert output signal DPO
    );
  end
endgenerate
"""
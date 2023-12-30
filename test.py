#! /usr/bin/env python3

import sys
import pyvisa

def word8(bin_data):
    word8 = bin_data[0] 
    return word8


def word16(bin_data):
    word16 = bin_data[1] + (bin_data[0] << 8)
    return word16

def word32(bin_data):
    word32 = bin_data[3] + (bin_data[2] << 8) + (bin_data[1] <<16) + (bin_data[0] <<24)
    return word32

def word64(bin_data):
    word64 =    bin_data[7]        + (bin_data[6] <<  8) + (bin_data[5] <<16) + (bin_data[4] <<24) \
             + (bin_data[3] << 32) + (bin_data[2] << 40) + (bin_data[1] <<48) + (bin_data[0] <<56)
    return word64

def decode_analyzer(bin_data):
    offset = 0
    instrument_id = word32(bin_data[offset:])
    offset += 4
    revision_code = word32(bin_data[offset:])
    offset += 4
    nr_pod_pairs = word32(bin_data[offset:])
    offset += 4
    analyzer_id = word32(bin_data[offset:])
    offset += 4
    machine_data_mode = word32(bin_data[offset:])
    offset += 4
    pods_list = word32(bin_data[offset:])
    offset += 4
    master_chip = word32(bin_data[offset:])
    offset += 4
    max_hw_depth = word32(bin_data[offset:])
    offset += 4
    offset += 4
    sample_period_ps = word64(bin_data[offset:])
    offset += 8
    tag_type = word32(bin_data[offset:])
    offset += 4
    trigger_offset_ps = word64(bin_data[offset:])
    offset += 8
    offset += 30

    print("Analyzer:")
    print("instrument_id:", instrument_id)
    print("revision_code:", revision_code)
    print("nr_pod_pairs:", nr_pod_pairs)
    print("analyzer_id:", analyzer_id)
    print("machine_data_mode:", machine_data_mode)
    print(f"pods_list: %x (%s)" % (pods_list, "{0:b}".format(pods_list)) )
    print("master_chip:", master_chip)
    print("max_hw_depth:", max_hw_depth)
    print("sample_period_ps:", sample_period_ps)
    print("tag_type:", tag_type)
    print("trigger_offset_ps:", trigger_offset_ps)

def decode_acq_data(bin_data):
    pass
    

def decode_section(bin_data):

    # SECTION HEADER
    offset = 0
    section_header = bin_data[offset:offset+16]
    offset += 16

    assert(section_header[0:10].decode('utf-8') == "DATA      ")

    module_id = int(section_header[11])
    block_length = word32(section_header[12:])

    # DATA PREAMBLE - ANALYZER 1
    decode_analyzer(bin_data[offset:])
    offset += 70
    print()

    # DATA PREAMBLE - ANALYZER 2
    decode_analyzer(bin_data[offset:])
    offset += 70
    print()

    offset += 56

    # NUMBER OF VALID ROWS 
    pods_valid_rows = [None] * 8
    for pod_nr in reversed(range(8)):
        valid_rows = word32(bin_data[offset:])
        pods_valid_rows[pod_nr] = valid_rows
        offset += 4
        pass

    print(pods_valid_rows)

    offset += 56

    # TRACE POINT LOCATIONS
    trace_point_locations = [None] * 8
    for pod_nr in reversed(range(8)):
        trace_point_location = word32(bin_data[offset:])
        trace_point_locations[pod_nr] = trace_point_location
        offset += 4
        pass

    print(trace_point_locations)

    offset += 234

    # RTC
    print(offset)
    rtc_year = word16(bin_data[offset:])
    offset += 2
    rtc_month = word8(bin_data[offset:])
    offset += 1
    rtc_day_month = word8(bin_data[offset:])
    offset += 1
    rtc_day_week = word8(bin_data[offset:])
    offset += 1
    rtc_hour = word8(bin_data[offset:])
    offset += 1
    rtc_minute = word8(bin_data[offset:])
    offset += 1
    rtc_second = word8(bin_data[offset:])
    offset += 1

    print(rtc_year, rtc_month, rtc_day_month, rtc_hour, rtc_minute, rtc_second)

    max_nr_valid_rows = max(pods_valid_rows)
    print(max_nr_valid_rows)

    print(offset)
    acquisition_data = []
    for i in range(max_nr_valid_rows):
        sample_point = [None] * 9       # One more for clock
        for pod_nr in reversed(range(10)):
            if pod_nr==9:
                offset += 2
                continue
            pod_data = word16(bin_data[offset:offset+2])
            offset += 2
            sample_point[pod_nr] = pod_data
        acquisition_data.append(sample_point)
    print(offset)

    #print(bin_data[offset:])

    if False:
        for i in range(max_nr_valid_rows):
            print(i)
            tag1 = word64(bin_data[offset:offset+2])
            offset += 8
            tag2 = word64(bin_data[offset:offset+2])
            offset += 8

    print(offset)
    print(bin_data[offset:])
        


def decode_data(bin_data):
    # block length specifier: 10 bytes 
    offset = 0
    bls = bin_data[offset:offset+10]
    offset += 10

    assert(chr(bls[0]) == '#')
    assert(chr(bls[1]) == '8')
    len = int(bls[2:])
    print("block length:", len)
    print()

    block_length = decode_section(bin_data[offset:])
    offset += 16

    pass


if False:
    rm      = pyvisa.ResourceManager()
    #inst    = rm.open_resource("TCPIP0::192.168.1.200::5025::SOCKET")
    inst    = rm.open_resource("GPIB::10")
    
    inst.write(":syst:dsp 'Hello!'")
    inst.write(":beep")
    #inst.write("*IDN?")
    #print(inst.read_raw())
    
    print("IDN? ", inst.query("*IDN?"))
    print("SELECT? ", inst.query(":select?"))
    inst.write(":select 1")
    inst.write(":dblock unpacked")
    print("DBLOCK?", inst.query(":dblock?"))

    inst.write(":syst:data?")
    data = inst.read_raw()

    with open("data.bin", "wb") as f:
        f.write(data)

if True:
    print(f"Reading {sys.argv[1]}...\n")
    with open(sys.argv[1], "rb") as f:
        bin_data = f.read()

    decode_data(bin_data)
    

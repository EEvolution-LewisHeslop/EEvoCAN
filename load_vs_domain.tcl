###############################################################################
# (C) COPYRIGHT Sevcon 2004
# 
# CCL Project Reference C6944 - Magpie
# 
# FILE
#     $Revision:1.53$
#     $Author:pe$
#     $ProjectName:DVT$ 
# 
# ORIGINAL AUTHOR
#     Chris Hauxwell
# 
# DESCRIPTION
#     Tcl script(s) to assist with loading programs into flash using the
#     bootloader programs.
# 
# REFERENCES    
#     C6944-TM-187
# 
# MODIFICATION HISTORY
###############################################################################

# Flag to warn against potential bricking of units
global error_during_load_dld
set error_during_load_dld 0


###############################################################################
#
# vs_bl_backdoor
#
# PARAMETERS
# ==========
#
# RETURNS
# =======
# Nothing
#
# DESCRIPTION
# ===========
# Sends a CAN message which the Bootloader will look for at start up. If the
# Bootloader receives this message with these contents it will remain active.
# Useful to get back to the Bootloader if your application is crashing.
#
proc vs_bl_backdoor {} {
    # send the backdoor CAN message
    can send "0x0055 0x46 0xB3 0x2E 0x49 0xB7 0x6F 0x03 0xCB"
}


###############################################################################
#
# vs_bl_upload
#
# PARAMETERS
# ==========
# node_id       - The Node ID.
# mem           - Memory space to upload from (APPDATA, PRODDATA, FRAM)
# hexfilename   - File to save hex image to (alternatively leave blank to return data from function)
#
# RETURNS
# =======
# Nothing
#
# DESCRIPTION
# ===========
# Uploads a hex image from the requested memory space
#
proc vs_bl_upload {node_id mem {hexfilename ""}} {

    # some data for the programming algos later
    #   devicestartaddress = 0x10000
    #   pagelength         = 0x1000    4kB blocks
    set mem_info [vs_get_memory_info $mem]
    if {$mem_info == ""} {return "ERROR: Invalid memory ($mem)"}
    
    infomsg "Memory info: $mem_info"
    set devicestartaddress  [lindex $mem_info 0]
    set deviceendaddress    [lindex $mem_info 1]
    set devicelength        [lindex $mem_info 2]
    set pagelength          [lindex $mem_info 3]
    set pad                 [lindex $mem_info 4]
    set access              [lindex $mem_info 5]
    set bl_mem_id           [lindex $mem_info 6]

    # check access permissions
    if {($access != "RO") && ($access != "RW")} {
        Return "ERROR: Read access is not allowed."
    }

    # set read command for application
    set cmd [format 0x%04x [expr ($bl_mem_id << 8) | 0x0005]]
	set result [sdo_wnx $node_id 0x5FF0 1 $cmd]
    if {$result != "OK"} {
        puts "Attempt to set memory ($mem, $bl_mem_id) into read mode (0x05) failed. Result = $result"
        return $result
    }
    infomsg "Read command to $mem OK"

    # read the domain as a block of bytes
    set can_data_bytes [sdo_rn $node_id 0x5FF0 2]
    if {(0 != [string match "*Abort*" $can_data_bytes]) || (0 != [string match "*Timeout*" $can_data_bytes])} {
        infomsg "ERROR: Read command failed during upload. Returned $can_data_bytes" error
        return $can_data_bytes
    }

    # first 4 bytes is the length of the data
    set explength [expr [merge_hex [lrange $can_data_bytes 0 3]]] 
    set data_bytes [lrange $can_data_bytes 4 end]
    set actlength [llength $data_bytes]
    infomsg "Expected amount of data = $explength, actual amount of data = $actlength"
    
    # if no filename is passed, just return the output
    if {$hexfilename == "NULL"} {
        return $data_bytes
    } 

    # else open a file, build up the hex record and save it. NOTE: This could do with more finesse!
    if {[catch {set fid [open $hexfilename w]} err]} {
        infomsg "Unable to open hex file. Returned $err" error
        return "Error - unable to open file"
    }


    set bytes_saved 0
    set addr_high -1

    # 0x00 = data
    # 0x01 = end of file
    # 0x04 = upper 16bit address (of 32bit)
    while {$bytes_saved < $actlength} {
    
        set bytes_remain [expr $actlength - $bytes_saved]
        set addr_now [expr $devicestartaddress + $bytes_saved]
        
        
        # Hex files only support 16-bit addresses typically, so when we have an address
        # which is > 0xFFFF, then the upper 16-bits (0xXXXX0000) must be stored in a seperate
        # line with type = 04. So add this line each time the upper 16-bits of the address
        # changes.
        set calc_addr_high [expr $addr_now / 65536]
        if { $addr_high != $calc_addr_high } {
        
            set addr_high $calc_addr_high
            set csum [expr 2 + 4 + (($addr_high & 0xFF00)/ 256) + ($addr_high & 0xFF)]
            set csum [expr (256 - ($csum % 256)) & 0xFF]
            
            # data len = 02
            # address = 0000
            # record = 04
            # data = dddd
            # checksum = cc
        
            # :llaaaarrddddcc
            
            set this_line ":02000004[format "%04X" $addr_high][format "%02X" $csum]"
            fputs $fid "$this_line"
        }
        
        # allow max of 16 bytes of data per line (unless we have <16 bytes left)
        if { $bytes_remain >= 16 } {
            set bytes_this_line 16
        } else {
            set bytes_this_line $bytes_remain
        }
        

        # normal line
        # :llaaaarrdd---ddcc
        
        set this_line ":"
        set csum 0
        
        #length
        append this_line "[format "%02X" $bytes_this_line]"
        incr csum [expr $bytes_this_line]
        
        #address low
        set addr_low [expr $addr_now & 0xFFFF]
        append this_line "[format "%04X" $addr_low]"
        incr csum [expr (($addr_low & 0xFF00)/ 256) + ($addr_low & 0xFF)]
        
        #record = 00 for data
        append this_line "00"
        
        #data
        for {set i $bytes_saved} {$i < [expr $bytes_saved + $bytes_this_line]} {incr i} {
            
            set data [lrange $data_bytes $i $i]
            
            incr csum [expr $data]
            append this_line "[format "%02X" $data]"
        }
        
        #checksum
        set csum [expr (256 - ($csum % 256)) & 0xFF]
        append this_line "[format "%02X" $csum]"
        
        #output the line to the file
        fputs $fid "$this_line"
        
        incr bytes_saved $bytes_this_line
    }

    # set end of file
    
    # data len = 00
    # address = 0000
    # record = 01
    # checksum = FF
    
    #            llaaaarrcc
    fputs $fid ":00000001FF"
    close $fid 
    
    return OK
}


###############################################################################
#
# vs_bl_download
#
# PARAMETERS
# ==========
# node_id       - The Node ID.
# mem           - Memory space to download to (APP, APPDATA, PRODDATA, FRAM)
# hexfilename   - File to save hex image to (alternatively leave blank to return data from function)
#
# RETURNS
# =======
# Nothing
#
# DESCRIPTION
# ===========
# Downloads a hex image to the requested memory space
#
proc vs_bl_download {node_id mem {hexfilename ""}} {

    # some data for the programming algos later
    set mem_info [vs_get_memory_info $mem]
    if {$mem_info == ""} {return "ERROR: Invalid memory ($mem)"}
    
    infomsg "Memory info: $mem_info"
    set devicestartaddress  [lindex $mem_info 0]
    set deviceendaddress    [lindex $mem_info 1]
    set devicelength        [lindex $mem_info 2]
    set pagelength          [lindex $mem_info 3]
    set pad                 [lindex $mem_info 4]
    set access              [lindex $mem_info 5]
    set bl_mem_id           [lindex $mem_info 6]

    # check access permissions
    if {($access != "WO") && ($access != "RW")} {
        Return "ERROR: Write access is not allowed."
    }


    # if no hex filename is specified open using tk_getOpenFile
    if {$hexfilename == ""} {
        set hexfilename [tk_getOpenFile -filetypes {{"Hex code files" {*.hex}} {"All files" {*.*}}}]
        infomsg "File name: $hexfilename"
    }
    
    # load DLD filename
    if {![file exists $hexfilename]} {return "cant find $hexfilename"}
    if {[catch {set fid [open $hexfilename]} err]} {
        return "unable to open file $err"
    }
    
    set hex [read $fid]
    close $fid

    # convert hex image to an array 
    array set hex_array [vs_hex_image_to_hex_array $hex]

    # unhelpfully, arrays are not sorted by default, so we need to look through it to find the start and end address
    set max_addr 0
    set min_addr 0xffffffff
    foreach addr [array names hex_array] {
        if {$addr>$max_addr} {
            set max_addr $addr
        }
        if {$addr < $min_addr} {
            set min_addr $addr
        }
    }
    infomsg "min_addr = [format 0x%08x $min_addr], max_addr = [format 0x%08x $max_addr]"

    # so now ask set the command and program memory space to Write, Application, and check the bootloader allows it
    set cmd [format 0x%04x [expr ($bl_mem_id << 8) | 0x0004]]
	set result [sdo_wnx $node_id 0x5FF0 1 $cmd]
    if {$result != "OK"} {
        puts "Attempt to set memory ($mem, $bl_mem_id) into write mode (0x04) failed. Result = $result"
        return $result
    }
    infomsg "Write command to $mem OK"

    # smallest block size we will send is 4kB, so pad out hex array to a 4kB boundary
    set padded_max_addr $max_addr
    while {[expr (($padded_max_addr + 1) - $devicestartaddress) % $pagelength != 0]} {
        incr padded_max_addr
        set hex_array($padded_max_addr) $pad
    } 

    #debug
#    infomsg "Padded from [format 0x%08x $max_addr] to [format 0x%08x $padded_max_addr]. Just out of interest data around max_addr"
#    for {set i [expr $max_addr - 2]} {$i < [expr $max_addr + 4]} {incr i} {
#        if {$i <= $deviceendaddress} {
#            infomsg "Padding @ [format 0x%08x $i] = $hex_array($i)"
#        }
#    }

    # send the data in 4kB blocks
    set byte_list ""
    for {set i $min_addr} {$i <= $padded_max_addr} {incr i} {
        append byte_list " $hex_array($i)"
        
        #if we've hit 4kB
        if {[llength $byte_list] >= $pagelength} {
            # and send the hex list to the bootloader via segmented SDO transfer
            set result [sdo_wn $node_id 0x5FF0 2 $byte_list]
            if {$result != "OK"} {
                puts "Attempt to write Application memory to domain object failed. Result = $result"
                return $result
            }

            infomsg "Sent data to [format 0x%08x $i]" 
            update
            
            # clear byte_list for next 4kB
            set byte_list ""
        }
    }

    # byte_list should be empty here. If not, we've not sent all the data!
    if {($byte_list != "") && ($i != $padded_max_addr)} {
        return "ERROR: We've not sent all the data to the bootloader"
        infomsg "ERROR: We've not sent all the data to the bootloader. byte_list = $byte_list. And i = $i and padded_max_addr = $padded_max_addr"
    }

    return "OK"
}


###############################################################################
#
# vs_get_memory_info
#
# PARAMETERS
# ==========
# mem       - Memory space identifier.
#
# RETURNS
# =======
# Details on the memory space
#   - Start address
#   - End address
#   - Length
#   - Page length (used to pad out memory to fill an entire block)
#   - Pad value (typically 0x00 for NVM, or 0xFF for application) 
#   - Read/Write access (equal to RW, RO, WO) 
#   - Memory ID in bootloader 
#
# DESCRIPTION
# ===========
# Returns information required for memory accesses
#
proc vs_get_memory_info {mem} {
    set result ""

# restore this        APPDATA   { set result "0x40000 0x7F000 0x3EFFF 0x1000  0x00    RW      0x02"}

    #                           Start   End     Len     Page    Pad     RW      BL_ID
    switch $mem {
        APP       { set result "0x10000 0x3FFFF 0x30000 0x1000  0xFF    WO      0x01"}
        APPDATA   { set result "0x40000 0x41FFF 0x2000  0x1000  0x00    RW      0x02"}
        PRODDATA  { set result "0x7F000 0x7FFFF 0x1000  0x1000  0x00    RW      0x03"}
        FRAM      { set result "0x0     0x0FFF  0x1000  0x1000  0x00    RW      0x04"}
        default   { infomsg "Available memories are: APP, APPDATA, PRODDATA, FRAM"}
    }

    return $result
}


###############################################################################
#
# vs_bts
#
# PARAMETERS
# ==========
# node_id       - The Node ID.
#
# RETURNS
# =======
# Nothing
#
# DESCRIPTION
# ===========
# Requests the bootloader software to start
#
proc vs_bts {{node_id 1}} {
    # TODO - need to implement this.
    return "ERROR: This needs to be implemented"
}


###############################################################################
#
# vs_bte
#
# PARAMETERS
# ==========
# node_id       - The Node ID.
#
# RETURNS
# =======
# Nothing
#
# DESCRIPTION
# ===========
# Requests the bootloader software to end
#
proc vs_bte {{node_id 1}} {
    # send command EXIT (0x02) to the bootloader. Ignore the result, it'll time out anyway 
    sdo_wnx $node_id 0x05FF0 1 0x0002   
    return "OK"
}


#
# proc converts standard intel hex to a list of bytes array
#
proc vs_hex_image_to_hex_array {hex_code} {
    set hex_code [split $hex_code \n]
    set hex_code_len [llength $hex_code]
    if {$hex_code_len == 0} {
        error "not enough data $hex_code_len "; 
    } 
        
    set line_no 0    
    set finished 0
    set err 0
    set address_msb -1
    set tot_byte_count 0

    while { ($line_no <= $hex_code_len) && !$finished} {
        set line [lindex $hex_code $line_no]

        set start_code    [string range $line 0     0    ]
        set byte_count "0x[string range $line 1     2    ]"
        set address    "0x[string range $line 3     6    ]"
        set type       "0x[string range $line 7     8    ]"
        set data          [string range $line 9     end-2]
        set checksum   "0x[string range $line end-1 end  ]"
        

        # handle type:
        #   0x00 - Data bytes
        #   0x01 - End of hex record
        #   0x04 - New section
        switch $type {
            0x00 {
                    # sanity check byte_address incase its not been set first
                    if {$address_msb == -1} {
                        error "Data received before new section started"
                        set finished 1
                        set err 1
                    }
                    
                    # calculate byte address msb + address
                    set byte_address [expr $address_msb + $address]
                    
                    # split data bytes into seperate values
                    for {set byte 0} {$byte < $byte_count} {incr byte} { 
                
                        # add to list if in range
                        set byte_list($byte_address) "0x[string range $data [expr $byte * 2] [expr ($byte * 2) + 1]]"
                        incr byte_address
                        incr tot_byte_count
                    }
            
                 }
    
            0x01 {
                    # finished so break out of while loop
                    set finished 1
                 }
    
            0x02 {
                    # calculate address msb as data shifted by 4 (basically adds one nibble to the address space)
                    set address_msb [expr 0x$data << 4]
                    infomsg "Type 02: data = $data, address_msb = [format 0x%08x $address_msb]"
                 }
    
            0x03 {
                    # ignore this (but indicate it was received)
                    infomsg "Received this line and don't know what to do with it: $line"
                    infomsg "Type 03: Byte count = $byte_count, address = $address, type = $type, data = $data, checksum = $checksum"
                 }

            0x04 {
                    # calculate address msb as data shifted into top word
                    set address_msb [expr 0x$data << 16]
                    infomsg "Type 04: data = $data, address_msb = [format 0x%08x $address_msb]"
                 }
            
            0x05 {
					#sets the execution start address	
                    infomsg "Type 05: data = $data. This is where the program execution will start. We can ignore this."
				}
            
            default {
                    set finished 1
                    error "Error: Unexpected type ($type)"
                 }
        }
        incr line_no
   }
    return [array get byte_list]
}

proc debug_back_up {} {
			

}
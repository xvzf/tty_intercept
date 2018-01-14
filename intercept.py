#!/usr/bin/env python3

import os, pty, threading, time
from serial import Serial
from binascii import hexlify

class SerialIntercept(object):

    # Just for better readability

    # PTY vars
    pty_master =        None
    pty_slave =         None
    pty_slave_name =    None
    pty_master_name =   None

    # Serial port vars
    serial_port =       None
    serial_baud =       None
    serial_conn =       None

    # Output
    fd_out =            None
    writing =           False

    def __init__(self, port="/dev/ttyUSB0", baud=9600, logfile="/tmp/intercept.txt"):
        self.setup_pty()
        self.setup_serial(port, baud)
        self.setup_out(logfile)

        # Actual interception
        self.thread_in = threading.Thread(target=SerialIntercept.bridge_in, args=[self])
        self.thread_out = threading.Thread(target=SerialIntercept.bridge_out, args=[self])
        self.thread_in.start()
        self.thread_out.start()


    def setup_pty(self):
        # Create the pseudoterminal
        m, s = pty.openpty()

        self.pty_master =   m
        self.pty_slave =    s

        # Get filedescr names
        self.pty_slave_name = os.ttyname(s)
        self.pty_master_name = os.ttyname(m)


    def setup_serial(self, port, baud):
        try:
            self.serial_conn = Serial(port, baud)
        except:
            print("@TODO")
            pass


    def setup_out(self, outfile):
        self.fd_out = open(outfile, "w")


    def log(self, tolog):
        while self.writing:
            pass
        
        # Basic mutex, pretty slow but working for serial interception
        self.writing = True
        self.fd_out.write(tolog + "\n")
        self.fd_out.flush()
        self.writing = False


    # Bridges virtual tty over to serial connection
    def bridge_in(self):
        while True:
            byte = os.read(self.pty_master, 1)
            self.serial_conn.write(byte)
            self.log(f"< 0x{hexlify(byte).decode('UTF-8')}")

    
    def bridge_out(self):
        while True:
            byte = self.serial_conn.read(1)
            os.write(self.pty_master, byte)
            self.log(f"> 0x{hexlify(byte).decode('UTF-8')}")


    def get_intercepted_tty(self):
        return self.pty_slave_name



if __name__ == "__main__":
    si = SerialIntercept()
    print(f"New tty for /dev/ttyUSB0: {si.get_intercepted_tty()}")
    while True:
        time.sleep(10)
        pass
    si = SerialIntercept()
    print(f"Slave Name {si.get_slave_name()}")

#   ser = Serial(si.get_intercepted_tty(), 2400, timeout=1)
#   ser.write("Test".encode())
#
#   time.sleep(0.5)
#   while ser.in_waiting > 0:
#       print(f"Serial Read: {ser.read()}")

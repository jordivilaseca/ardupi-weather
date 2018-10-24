import os
import sys
import termios
import atexit
from select import select
import time


class Terminal:

    def __init__(self):

        self.currentInp = ""

        # Save the terminal settings
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)
        # New terminal setting unbuffered
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)
        # Support normal-terminal reset at exit
        atexit.register(self.set_normal_term)


    def set_normal_term(self):
        ''' Resets to normal terminal.  On Windows this is a no-op.
        '''
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)


    def getch(self):
        ''' Returns a keyboard character after kbhit() has been called.
            Should not be called in the same program as getarrow().
        '''
        return sys.stdin.read(1)

    def kbhit(self):
        ''' Returns True if keyboard character was hit, False otherwise.
        '''
        dr,dw,de = select([sys.stdin], [], [], 0)
        return dr != []

    def readLine(self):
        ret = ""
        if self.kbhit():
            c = self.getch()
            if c == '\n':
                ret = self.currentInp
                print (self.currentInp)
                self.currentInp = ""
            else:
                self.currentInp += c
        return ret

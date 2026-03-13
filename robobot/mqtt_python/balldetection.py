import sys
#import threading
import time as t
#import select
import numpy as np
import cv2 as cv
from datetime import *
# robot function
from spose import pose
from sir import ir
from uservice import service

def BallDetection():
    distance = ir.ir[0]

    if 0.1 <= distance <= 0.2:
        print("Object detected")
        service.send("robobot/cmd/T0", "servo 1 100 300")


if __name__ == "__main__":
    if service.process_running("mqtt-client"):
      print("% mqtt-client is already running - terminating")
      print("%   if it is partially crashed in the background, then try:")
      print("%     pkill mqtt-client")
      print("%   or, if that fails use the most brutal kill")
      print("%     pkill -9 mqtt-client")
    else:
      # set title of process, so that it is not just called Python
      print("% Starting")
      # where is the MQTT data server:
      #service.setup('localhost') # localhost
      service.setup('10.197.219.35') # Hugo
      #service.setup('10.197.217.81') # Juniper
      #service.setup('10.197.217.80') # Newton
      # service.setup('bode.local') # Bode
      if service.connected:
        while True:
          BallDetection()
          t.sleep(0.1)

      service.terminate()
    print("% Program Terminated")

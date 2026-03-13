# fsm_george.py
import time as t
import numpy as np
from spose import pose
from uservice import service

'''
start
  ↓
0.5 m forward
  ↓
90° turn
  ↓
0.5 m forward
  ↓
stop
'''

def simpleFSM():
    state = 0
    pose.tripBreset()
    print("% Starting simple FSM")

    while not service.stop:
        if state == 0:
            print("State 0: Move forward")
            service.send("robobot/cmd/ti", "rc 0.2 0")  # forward
            pose.tripBreset()
            state = 1

        elif state == 1:
            if pose.tripB > 0.5:
                service.send("robobot/cmd/ti", "rc 0 0")  # stop
                pose.tripBreset()
                state = 2

        elif state == 2:
            print("State 2: Turn 90°")
            service.send("robobot/cmd/ti", "rc 0 0.5")  # turn
            state = 3

        elif state == 3:
            if pose.tripBh > np.pi/2:
                service.send("robobot/cmd/ti", "rc 0 0")  # stop
                pose.tripBreset()
                state = 4

        elif state == 4:
            print("State 4: Move forward again")
            service.send("robobot/cmd/ti", "rc 0.2 0")
            state = 5

        elif state == 5:
            if pose.tripB > 10:
                service.send("robobot/cmd/ti", "rc 0 0")
                state = 99

        elif state == 99:
            print("% FSM finished")
            break

        t.sleep(0.05)


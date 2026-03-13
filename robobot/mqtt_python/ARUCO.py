import cv2.aruco as aruco
from scam import cam
import time as t
from spose import pose
from uservice import service
import numpy as np
# Opsætning af ArUco-detektor
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)

def search_and_center(target_id=10):
    print(f"% Starter søgning efter ID {target_id}...")
    
    # Start en langsom rotation
    # Vi bruger en lav hastighed (0.3), så kameraet kan nå at se koden uden motion blur
    service.send("robobot/cmd/ti", "rc 0.0 0.4")
    
    found = False
    while not service.stop:
        ok, img, imgTime = cam.getImage()
        if not ok:
            continue
            
        corners, ids, _ = detector.detectMarkers(img)
        
        if ids is not None:
            for i in range(len(ids)):
                if ids[i][0] == target_id:
                    print(f"% ID {target_id} fundet! Stopper og centrerer...")
                    service.send("robobot/cmd/ti", "rc 0.0 0.0")
                    found = True
                    break
        
        if found:
            # Nu kalder vi den funktion vi lavede før
            service.send("robobot/cmd/T0","servo 1 400 -300") # (servo front fast)
            t.sleep(0.01)
            return center_on_marker(target_id)
            t.sleep(0.1)
            
        t.sleep(0.01) # Hurtigt loop for at opfange markøren hurtigst muligt
    
    return False


def driveTurn90(direction):
    # Nulstil vinkeltælleren (tripBh måler ændring i vinkel)
    pose.tripBreset() 
    
    # Sæt drejerate (rad/s). Positiv er venstre, negativ er højre.
    rate = 0.8 if direction == "left" else -0.8
    target_angle = 1.57 # 90 grader i radianer (pi/2)

    print(f"% Starter 90 graders drej til {direction}...")
    
    # Start motoren
    service.send("robobot/cmd/ti", f"rc 0.0 {rate}")

    # Loop indtil vi har drejet nok
    while abs(pose.tripBh) < target_angle and not service.stop:
        # Vi sover kun kort for ikke at belaste CPU'en
        t.sleep(0.01)
    
    # Stop robotten
    service.send("robobot/cmd/ti", "rc 0.0 0.0")
    print(f"% Færdig! Drejede {abs(pose.tripBh):.3f} rad.")



# Husk at definere denne variabel i toppen af dit script (uden for funktioner)
last_aruco_time = 0

def check_for_aruco_navigation():
    global last_aruco_time
    
    # 1. Hent billede fra kameraet
    ok, img, imgTime = cam.getImage()
    
    if ok:
        # 2. Led efter markere
        corners, ids, _ = detector.detectMarkers(img)
        
        # 3. Tjek om vi har set noget og om "cooldown" (5 sek) er ovre
        if ids is not None and (t.time() - last_aruco_time > 5):
            marker_id = ids[0][0]

            if marker_id == 10:
                center_on_marker(10)
                last_aruco_time = t.time()
                return True
            
            if marker_id == 42: # Højre
                print(f"% ArUco {marker_id} fundet: Drejer 90 grader HØJRE")
                driveTurn90("right")
                last_aruco_time = t.time()
                return True # Fortæller loopet at vi har reageret
                
            elif marker_id == 43: # Venstre
                print(f"% ArUco {marker_id} fundet: Drejer 90 grader VENSTRE")
                driveTurn90("left")
                last_aruco_time = t.time()
                return True # Fortæller loopet at vi har reageret
                
    return False # Vi så intet eller reagerede ikke

def center_on_marker(target_id=10):
    print(f"% Forsøger at centrere på ID {target_id}...")
    
    while not service.stop:
        ok, img, imgTime = cam.getImage()
        if not ok:
            continue
            
        corners, ids, _ = detector.detectMarkers(img)
        
        # Tjek om vi ser det rigtige ID
        found = False
        if ids is not None:
            for i in range(len(ids)):
                if ids[i][0] == target_id:
                    # Find midten af markøren i pixels (x-koordinat)
                    # corners[i] er en liste af de 4 hjørner, vi tager gennemsnittet
                    marker_center_x = np.mean(corners[i][0][:, 0])
                    
                    # Find midten af selve billedet
                    image_center_x = img.shape[1] / 2
                    
                    # Beregn fejlen (hvor mange pixels er vi ved siden af?)
                    error = marker_center_x - image_center_x
                    
                    # Hvis fejlen er lille nok (f.eks. +/- 10 pixels), stopper vi
                    if abs(error) < 10:
                        service.send("robobot/cmd/ti", "rc 0.0 0.0")
                        print("% Markør centreret!")
                        return True
                    
                    # Drej proportionelt med fejlen
                    # Vi bruger en lille 'gain' (0.002) til at styre hastigheden
                    turn_speed = -0.002 * error 
                    
                    # Begræns max hastighed så den ikke spinner vildt
                    turn_speed = max(min(turn_speed, 0.4), -0.4)
                    
                    service.send("robobot/cmd/ti", f"rc 0.0 {turn_speed}")
                    found = True
                    break
        
        if not found:
            # Hvis vi mister markøren, stopper vi for en sikkerheds skyld
            service.send("robobot/cmd/ti", "rc 0.0 0.0")
            print("% Markør mistet under centrering!")
            return False
            
        t.sleep(0.05) # Lille pause for ikke at stresse CPU'en

def lower_servo_and_pause():
    print("% Sænker servo og pauser i 10 sekunder...")
    
    # Kør servoen ned (position 500, hastighed 200 - juster selv tallene)
    service.send("robobot/cmd/T0", "servo 1 400 -200")
    
    # Vent i 10 sekunder
    t.sleep(10)
    
    print("% Pause slut - fortsætter mission.")
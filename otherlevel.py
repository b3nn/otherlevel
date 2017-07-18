#!/usr/bin/python

# Otherlevel -- by 0xb3nn 07/2017
# Conducts repeated probes of the Othermill bed and prints the offset of 
# these points. Can be useful for testing how level the bed, or a 
# conductive surface, is.

# RUN AT YOUR OWN RISK! 
# Monitor the mill while running this script. 
# Be prepared to hit emergency stop on mill if necessary!
# Script should run after a reboot of mill to avoid unexpected settings.
# ONLY TESTED ON THE OTHERMILL V2 (non-Pro) Firmware 72.73

# You may need to "pip install pyserial" and "numpy" if it fails here
import serial, numpy, json, time, sys, math

# Othermill will have 2 Com ports when powered on. The first one,
# "Control Channel" worked for me. OSX/Linux will be something 
# like "/dev/tty.usbmodem621"
COM_PORT = "COM7"

# First test point location. Others points calculated from here. In MMs.
X_START = 18
Y_START = 18

# This step size worked for me to avoid the deeper holes in the bed
STEP_SIZE = 25

# Set this to True to see response to commands sent to the mill
VERBOSE = False

# Max Bed size is x:140 y:100
X_STOP = 140
Y_STOP = 100

# Found I needed a delay between commands or mill got unhappy
SLEEPTIME = 0.5

# GCODE Commands
GCODE_HOME = """
M05 G94 G90 G21 G64 G17 G55 F0S0 (starting sandbox)
M30
G28.3X147Y120.5Z-61.5
G28.2Z0X0Y0
S1200
M00
M05 G93 G90 G21 G64 G17 G55 F0S0 (exiting sandbox)
"""

GCODE_PROBE = """
M05 G94 G90 G21 G64 G17 G55 F0S0 (starting sandbox)
G91
G38.2Z-60.5F100
"""

GCODE_RISE = """
G0 Z15
"""

GCODE_INIT = """
M30
{"sr":""}
{"sys":{"ja":1000000}}
"""

ser = None

def send_gcode(gcode):
    global ser
    if VERBOSE:
        print("Sending: " + gcode)
    ser.write(gcode)
    time.sleep(SLEEPTIME)
    bytesToRead = ser.inWaiting()

    while bytesToRead:
        if bytesToRead > 0 :
            x = ser.read(bytesToRead)
            if VERBOSE:
                print(x)
        if VERBOSE:
            print("..sleeping")
        time.sleep(SLEEPTIME)
        bytesToRead = ser.inWaiting()


def send_gcode_lines(CODE):
    for line in CODE.splitlines():
        send_gcode(line + "\n")


def get_z():
    bytesToRead = ser.inWaiting()
    junk = ser.read(bytesToRead)    
    ser.write('{"sr":""}' + "\n")
    time.sleep(SLEEPTIME)
    bytesToRead = ser.inWaiting()
    x = ser.read(bytesToRead)
    response = json.loads(x.strip())
    z = response["r"]["sr"]["mpoz"]
    return z


def print_results(a):
    #Print the output in the order that matches the bed layout
    ys_per_step = int(math.ceil(float(Y_STOP - Y_START) / float(STEP_SIZE)))
    xs_per_step = int(math.ceil(float(X_STOP - X_START) / float(STEP_SIZE)))

    for x in range(0, xs_per_step):
        for y in range((ys_per_step -1), -1, -1):
            i = y + (x * ys_per_step)
            sys.stdout.write("% 7.3f   " % a[i])
        print("\n")


def main():
    global ser
    
    try:
        ser = serial.Serial(COM_PORT, 9600, timeout=2)
    except Exception, e:
        print("Error opening COM port. Make sure mill is connected & powered on.")
        print("Set COM_PORT in this script to the correct one for your system.")
        print("Otherplan should be closed in order for this to connect.")
        print(str(e))
        exit()

    start_time = time.strftime("%Y-%m-%d %H:%M:%S")

    print("Init Session")
    send_gcode_lines(GCODE_INIT)

    print("Start Homing")
    send_gcode_lines(GCODE_HOME)

    print("Set Incremental Mode")
    send_gcode("G91" + "\n")

    zs=[]
    X = X_START

    while X < X_STOP:
      Y = Y_START
      send_gcode("G53G00X" + str(STEP_SIZE) + "Y0.0\n")

      while Y < Y_STOP:
        # Move to new location
        print("Moving X:" + str(X) + " Y:" + str(Y))
        send_gcode("G53G00X0.0Y" + str(STEP_SIZE) + "\n")

        # Probe Z
        print("Starting Probe")
        send_gcode_lines(GCODE_PROBE)

        Z_LAST = get_z()
        zs.append(Z_LAST)
        print("Last Z: " + str(Z_LAST))

        # Raise Probe up
        send_gcode(GCODE_RISE)

        Y = Y + STEP_SIZE

      # Reset the Y spot
      send_gcode("G53G00X0.0Y-" + str(Y-Y_START) + "\n")
      X = X + STEP_SIZE

    print("\nReport from " + start_time)
    mean = numpy.mean(zs)
    print("Mean: " + str(mean))
    print("Standard Deviation: " + str(numpy.std(zs)))

    print("\nZ Results Map")
    print_results(zs)

    print("\nOffsets from Mean")
    zs_std = map(lambda x: round(x - mean, 3), zs)
    print_results(zs_std)


if __name__ == '__main__':
    main()
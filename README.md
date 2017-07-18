# Otherlevel
Script to test and report repeated bed probe results on the Othermill CNC.
Conducts repeated probes of the Othermill bed and prints the offset of 
these points. Can be useful for testing how level the bed, or a 
conductive surface, is.

**RUN AT YOUR OWN RISK!** 
Monitor the mill while running this script. 
Be prepared to hit emergency stop on mill if necessary!
Script should run after a reboot of mill to avoid unexpected settings.
ONLY TESTED ON THE OTHERMILL V2 (non-Pro) Firmware 72.73

# Requirements and Setup
Requires Python 2.7 (may need to pip install pyserial and numby)
Othermill will have 2 Com ports when powered on. The first one,
"Control Channel" worked for me. OSX/Linux will be something 
like "/dev/tty.usbmodem621". Set this for the COM_PORT in the code.
Otherplan will need to be closed when running this script.

# Sample Results
The results will print to match the orintation of the bed while
looking directly at the front of the Othermill. 

```
Report from 2017-07-16 16:16:38
Mean: -47.3084
Standard Deviation: 0.00970772887961

Z Results Map
-47.299   -47.314   -47.320   -47.318

-47.310   -47.302   -47.313   -47.301

-47.319   -47.311   -47.299   -47.297

-47.324   -47.312   -47.295   -47.298

-47.327   -47.311   -47.301   -47.297


Offset from Mean Map
  0.009    -0.006    -0.012    -0.010

 -0.002     0.006    -0.005     0.007

 -0.011    -0.003     0.009     0.011

 -0.016    -0.004     0.013     0.010

 -0.019    -0.003     0.007     0.011
```


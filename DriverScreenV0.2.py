'''
Last Edit: 03/24/2023

Mason Myre

The Following code is for the driver display

Please make sure to include the following in the lib folder:
adafruit_display_text
adafruit_mcp2515
adafruit_ssd1325.py

Changelog:
added a warning symbol when the pico temp, motor temp, or motor controller temp went above 45c, 70c, and 70c respectively


TODO:
Get the temperature of the driver control pico instead of the screen pico
Either use CAN or just send it directly as an INT


'''

import board
import busio
import math
import struct
import time
import analogio
import digitalio
import displayio
import terminalio
import adafruit_ssd1325
from adafruit_mcp2515       import MCP2515 as CAN
from adafruit_mcp2515.canio import RemoteTransmissionRequest, Message, Match, Timer
from adafruit_display_text import label
import adafruit_mcp2515
import microcontroller 



current = -1
lowTemp = 20
highTemp = 20
avgTemp = 20

# Release the displays and start the clock
boot_time = time.monotonic()
displayio.release_displays()

# Create the SPI Buss
spi = busio.SPI(board.GP2, board.GP3, board.GP4)

# Set up the MCP 2515 on the SPI Bus
can_cs = digitalio.DigitalInOut(board.GP9)
can_cs.switch_to_output()
mcp = CAN(spi, can_cs, baudrate = 500000, crystal_freq = 16000000, silent = False,loopback = False)

# Set up the OLED on the SPI Bus
cs = board.GP22
dc = board.GP23
reset = board.GP21
WIDTH = 128
HEIGHT = 64
BORDER = 0
FONTSCALE = 1

display_bus = displayio.FourWire(spi, command=dc, chip_select=cs, reset=reset, baudrate=1000000)
display = adafruit_ssd1325.SSD1325(display_bus, width=WIDTH, height=HEIGHT)
display.brightness = 1.0



startTime = time.time()
# Make the display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000  # Black

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a label
text = "SOLAR CAR ISU"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_width = text_area.bounding_box[2] * FONTSCALE
text_group = displayio.Group(
    scale=FONTSCALE,
    x=display.width // 2 - text_width // 2,
    y=display.height // 2,
)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)
time.sleep(2.5)
splash.pop(-1)




tire_diameter = 22
mph     = 0
voltage = 0
current = 0
eff     = 0
heatsink_temp = 0
motor_temp = 0
DCU_timeout = 0
prevDCU_time = time.monotonic_ns()
pico_temp_str = ""
motor_temp_str = ""
heatsink_temp_str = "" #heatsink for the motor controller

# Draw Speed/effecency Label
text_group = displayio.Group(scale=3, x=3, y=12)
text = "S: {:04.1f}".format(mph)
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

# Draw Amperage Label
text_group = displayio.Group(scale=3, x=3, y=41)
text = "A: {:04.1f}".format(current)
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

# Draw voltage/current Label
text_group = displayio.Group(scale=1, x=0, y=60)
text = "S:{:04.1f} M:{:04.1f} H:{:04.1f}".format(microcontroller.cpu.temperature, motor_temp, heatsink_temp)
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

time.sleep(0.5)

runTime = time.time()

def _shaune_theCAN_isfull():
    message_count = listener.in_waiting()
    if message_count >300:
        mcp._unread_message_queue.clear()





flip_time  = time.monotonic_ns()
current_flip = 'ampvolt'

def send_error(bool,loc):
    if bool:
        # Draw temp/dcu timeout Label
        text_group = displayio.Group(scale=1, x=15, y=60)
        text = error_dick[loc] 
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
        text_group.append(text_area)  # Subgroup for text scaling
        splash[-1] = text_group
        time.sleep(0.5)

    else:
        pass

error_dick = {'BMS': "BMS Fault",'pico_temp': "Pico Overheat",'DCU_timeout': "it ain't got no gas in it" }



while True:
    #send_error(DCU_timeout < 250000000,'DCU_timeout')
    #send_error(microcontroller.cpu.temperature > 65,'pico_temp')

        
    with mcp.listen(timeout=0) as listener:
        

        
        _shaune_theCAN_isfull()
        eff = (mph*1000) / (current*voltage + 0.000001) 
        eff = 99.99 if eff > 99.9 else eff


        #print_string = "{:06.2f}".format(float(time.monotonic()-boot_time)) + "\t" + "{:05.1f}".format(voltage) + "\t"  + "{:05.1f}".format(current) + "\t"  + "{:05.1f}".format(mph)+"\t"+str(eff)
        #print(print_string,end='\t')
        


        # Draw Speed Label
        text_group = displayio.Group(scale=3, x=3, y=12)
        text = "S: {:04.1f}".format(mph)
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
        text_group.append(text_area)  # Subgroup for text scaling
        splash[-3] = text_group

        # Draw Amperage Label
        text_group = displayio.Group(scale=3, x=3, y=41)
        text = "A: {:04.1f}".format(current)
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
        text_group.append(text_area)  # Subgroup for text scaling
        splash[-2] = text_group

        # flip after 1.25 sec
        #rewrite the code to not flip anymore
        #text_group = displayio.Group(scale = 1, x = 0, y = 60) #set up display area
        #text = pico_temp_str + motor_temp_str + heatsink_temp_str
        

        #text = "P:{:04.1f} M:{:04.1f} H:{:04.1f}".format(microcontroller.cpu.temperature, motor_temp, heatsink_temp) #pico temp, motor temp, motor controller temp
        #text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
        #text_group.append(text_area)  # Subgroup for text scaling
        #splash[-1] = text_group

        #Here starts where we do the CAN things
        message_count = listener.in_waiting()
        #print("message count = {}".format(message_count),end = '\n')
        if message_count == 0:

            continue
        
        next_message = listener.receive()
        message_num = 0

        
        while not next_message is None: #while next message

            message_num += 1

            # Check the id to properly unpack it
            # Updated the CAN message as of 3/24/24 NEED TO PUT IN TEAMS SREADSHEET
            
            if next_message.id == 0x402:
            #unpack and print the message
                holder = struct.unpack('<ff',next_message.data)
                rpm = holder[0]
                current = holder[1]
                mph = rpm*tire_diameter*math.pi*60*1/(12*5280)
                
                
                print("Message From: {}: [RPM = {}; MPH = {}; A = {}]".format(hex(next_message.id),rpm,mph,current))


                
            # Recieve tempetaure from heat sink and motor    
            if next_message.id == 0x40B:
                #unpack and print the message
                holder = struct.unpack('<ff',next_message.data)
                motor_temp = holder[0]
                heatsink_temp = holder[1]
                print("Message From: {}: [Motor Temp = {}; Heat Sink = {}]".format(hex(next_message.id),motor_temp,heatsink_temp))


            if next_message == 0x40C:
                holder = struct.unpack('<ff',next_message.data)
                dsp_temp = holder[0]
            
            if next_message == 0x401:
                DCU_timeout = time.monotonic_ns() - prevDCU_time
                prevDCU_time = time.monotonic_ns()




            if next_message.id == 0x6b0:
                #print("BMS Data")
                #unpack and print the message
                holder = struct.unpack('>hhhh',next_message.data)
                current = holder[1]*.1
                voltage = holder[3]*.01
                
                #print(current,voltage)
                
            if next_message.id == 0x6b1:
                
                #print("Temp Datat")
                holder = struct.unpack('>hhhxx',next_message.data)
                lowTemp = holder[0]
                highTemp = holder[1]
                avgTemp = holder[2]
                
            
            # over/under current protection
            if (current >= 70 or current <= -15):
                 
                # Draw BMS Error
                color_bitmap = displayio.Bitmap(display.width, display.height, 1)
                color_palette = displayio.Palette(1)
                color_palette[0] = 0xFFFFFF  # Black

                bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
                splash.append(bg_sprite)
                text_group = displayio.Group(scale=2, x=3, y=12)
                text = "BMS Fault\n"
                text_area = label.Label(terminalio.FONT, text=text, color=0x000000)
                text_group.append(text_area)  # Subgroup for text scaling
                splash.append(text_group)
                #print("BMS Fault:") #for help with testing
                #print(current)
                while True:
                    pass
                
 
            #General Temperature Protection System (GTPS)
            pico_temp = microcontroller.cpu.temperature
            pico_temp_str = "P:{:04.1f}".format(pico_temp)
            if(pico_temp >= 45): #we're not exactly sure where problems happen but if we keep it below 45 we know everything will be okay
                pico_temp_str = pico_temp_str + "*"
            else:
                pico_temp_str = pico_temp_str + " "
    
            motor_temp_str = "M:{:04.1f}".format(motor_temp)
            if(motor_temp >= 70 or motor_temp <= 4): #problems happen at 85c
                motor_temp_str = motor_temp_str + "*"
            else:
                motor_temp_str = motor_temp_str + " "
                
            heatsink_temp_str = "H:{:04.1f}".format(heatsink_temp)
            if(heatsink_temp >= 70 or heatsink_temp <= 4): #problems at 85c
                heatsink_temp_str = heatsink_temp_str + "*"
            
          
            #temp protection in celsius
            if (highTemp > 45 or lowTemp < 0):
                
                # Draw BMS Error
                color_bitmap = displayio.Bitmap(display.width, display.height, 1)
                color_palette = displayio.Palette(1)
                color_palette[0] =0xFFFFFF  # Black

                bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
                splash.append(bg_sprite)
                text_group = displayio.Group(scale=2, x=3, y=12)
                text = "BMS Fault\n"
                text_area = label.Label(terminalio.FONT, text=text, color=0x000000)
                text_group.append(text_area)  # Subgroup for text scaling
                splash.append(text_group)
                while True:
                    pass
            text_group = displayio.Group(scale = 1, x = 0, y = 60) #set up display area
            text = pico_temp_str + motor_temp_str + heatsink_temp_str
            text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
            text_group.append(text_area)  # Subgroup for text scaling
            splash[-1] = text_group
            

            next_message = listener.receive()
            
### Add the code here to  switch to the screen

### REMEMBER TO MOVE THE NEXT_MESSAGE LINE TO THE BOTTOM ONCE DONE SHANE
'''
            if next_message == x__ :
                
                # Draw BMS Error
                color_bitmap = displayio.Bitmap(display.width, display.height, 1)
                color_palette = displayio.Palette(1)
                color_palette[0] =0x000000  # Black

                    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
                splash.append(bg_sprite)
                text_group = displayio.Group(scale=2, x=3, y=12)
                text = "BMS Fault\n Bitch"
                text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
                text_group.append(text_area)  # Subgroup for text scaling
                splash.append(text_group)
                while True:
                    pass
            


'''
            

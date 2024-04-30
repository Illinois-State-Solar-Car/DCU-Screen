'''
This code is for the DCU Screen (driver control unit)
Last updated: 4/30/24

Updates:
4/30/24
Build output string when receiving can values
I probably broke something so I'll need to test...again
But now at least we get the System for Heating and Internal Temperature monitor

Updates:
3/25/24
Please make sure to include the following in the lib folder:
adafruit_display_text
adafruit_mcp2515
adafruit_ssd1325.py

TODO:
Ask shane if we actually need to grab the current time twice

'''
#DCU Screen V0.4
#4/10/24


#imports
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

#declare our variables
tire_diameter = 22 #don't need this because we shouldn't be calculating a constant every time we display something (see line x for further clarification)
rpm_to_mph = tire_diameter * 0.003
mph = 0
volt = 0
current = 0
heatsink_temp = 0
motor_temp = 0
pico_temp = 0
#DCU_timeout = 0 #not sure if we still use this
#prevDCU_time = time.monotonic_ns() #also not sure if we still use this
_can_queue_size = 300

spd_text = "S: {:04.1f}".format(mph)
amp_text = "A: {:04.1f}".format(current)
heat_text = "P:{:04.1f} H:{:04.1f} M:{:04.1f}".format(pico_temp, heatsink_temp, motor_temp)


#set up the displays
boot_time = time.monotonic()
displayio.release_displays()

#create the SPI bus
spi = busio.SPI(board.GP2, board.GP3, board.GP4)


#setup CANbus on the SPI bus
can_cs = digitalio.DigitalInOut(board.GP9)
can_cs.switch_to_output()
mcp = CAN(spi, can_cs, baudrate = 500000, crystal_freq = 16000000)

#setup OLED screen on the SPI bus
#constants declarations
cs = board.GP22
dc = board.GP23
reset = board.GP21
WIDTH = 128
HEIGHT = 64
BORDER = 0
FONTSCALE = 1
#get the OLED ready for use
display_bus = displayio.FourWire(spi, command=dc, chip_select=cs, reset=reset, baudrate = 1000000)
display = adafruit_ssd1325.SSD1325(display_bus, width=WIDTH, height=HEIGHT)
display.brightness = 1.0

startTime = time.time()


#display 
splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] =0x000000  # Black

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)




# Draw a label
text = "SOLAR CAR ISU\nDCU SCREEN"
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


# Draw Speed/effecency Label
text_group = displayio.Group(scale=3, x=3, y=12)
text = "S: {:04.1f}".format(mph)
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

# Draw Current Label
text_group = displayio.Group(scale=3, x=3, y=41)
text = "A: {:04.1f}".format(current)
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

# Draw pico/motorcontroller/motor temperature labels
text_group = displayio.Group(scale=1, x=15, y=60)
text = "P: {:04.1f}  H: {:04.1f}, M: {:04.1f}".format(pico_temp, heatsink_temp, motor_temp)
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

#if the CAN queue is larger than a set size, we clear it to ensure we are only getting up to date messages
def _can_is_full():
    message_count = listener.in_waiting()
    if message_count > _can_queue_size:
        mcp._unread_message_queue.clear()


#error handling
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

time.sleep(.2)

runTime = time.time()



#our looping code
while True:


    with mcp.listen(timeout = 0) as listener:

        _can_is_full()



        # Draw Speed/effecency Label
        text_group = displayio.Group(scale=3, x=3, y=12)
        text_area = label.Label(terminalio.FONT, text = spd_text, color=0xFFFFFF)
        text_group.append(text_area)  # Subgroup for text scaling
        splash[-3] = text_group

        # Draw Current Label
        text_group = displayio.Group(scale=3, x=3, y=41)
        text_area = label.Label(terminalio.FONT, text = amp_text, color=0xFFFFFF)
        text_group.append(text_area)  # Subgroup for text scaling
        splash[-2] = text_group

        # Draw pico/motorcontroller/motor temperature labels
        text_group = displayio.Group(scale=1, x=0, y=60)
        text_area = label.Label(terminalio.FONT, text = heat_text, color=0xFFFFFF)
        text_group.append(text_area)  # Subgroup for text scaling
        splash[-1] = text_group


        message = Message(id=0x6b4, data=struct.pack('<ff',mph,current), extended=False)
        send_success = mcp.send(message)
        runTime = time.time()
        

        
        #Here starts where we do the CAN things
        message_count = listener.in_waiting()
        #print("message count = {}".format(message_count),end = '\n')
        
        if message_count == 0:

            continue
        
        next_message = listener.receive()
        message_num = 0

        
        while not next_message is None:

            message_num += 1

            # Check the id to properly unpack it
            if next_message.id == 0x402: #amp and voltage data
            #unpack and print the message
                holder = struct.unpack('<ff',next_message.data)
                #voltage = holder[0] #we don't need voltage and we are not displaying it
                current = holder[1]
                #print("Message From: {}: [V = {}; A = {}]".format(hex(next_message.id),voltage,current))
                amp_text = "A: {:04.1f}".format(current)

    
            if next_message.id == 0x403: #speed data
                #unpack and print the message
                holder = struct.unpack('<ff',next_message.data)
                rpm = holder[0]
                #mph = rpm*tire_diameter*math.pi*60*1/(12*5280)
                mph = rpm * rpm_to_mph #did some calculations so we don't need to reinvent the wheel every time we display the speed
                #print("Message From: {}: [rpm = {}; mph = {}]".format(hex(next_message.id),rpm,mph))
                spd_text = "S: {:04.1f}".format(mph)

            # Recieve tempetaure from heat sink and motor    
            if next_message.id == 0x40B:
                #unpack and print the message
                holder = struct.unpack('<ff',next_message.data)
                motor_temp = holder[0]
                heatsink_temp = holder[1]
                pico_temp = microcontroller.cpu.temperature
                #System for Heating and Internal Temperature monitor
                pico_text = "P:{:04.1f}".format(pico_temp)
                heatsink_text = "H:{:04.1f}".format(heatsink_temp)
                motor_text = "M:{:04.1f}".format(motor_temp)

                if(pico_temp > 45):
                    pico_text = pico_text + "*"
                else:
                    pico_text = pico_text + " "

                if(heatsink_temp > 70):
                    heatsink_text = heatsink_text + "*"
                else:
                    heatsink_text = heatsink_text + " "

                if(motor_temp > 70):
                    motor_text = motor_text + "*"
                

                heat_text = "P:{:04.1f} H:{:04.1f} M:{:04.1f}".format(pico_temp, heatsink_temp, motor_temp)

              
                #print("Message From: {}: [Motor Temp = {}; Heat Sink = {}]".format(hex(next_message.id),motor_temp,heatsink_temp))

            if next_message == 0x40C:
                holder = struct.unpack('<ff',next_message.data)
                dsp_temp = holder[0]
            
            if next_message == 0x401:
                DCU_timeout = time.monotonic_ns() - prevDCU_time
                prevDCU_time = time.monotonic_ns()

            


            next_message = listener.receive()    












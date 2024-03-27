'''
This code is for the DCU Screen (driver control unit)
Last updated: 3/25/24
Mason Myre

The current DCU Screen code on the github works, but I wanted to rewrite it a bit to be overall a bit cleaner
This new one has like 50 less lines of code and more comments
Also imo easier to understand because I broke up some stuff into functions

Updates:
deleted dsp_temp because I didn't know what it did and because it wasn't used anywhere else

Please make sure to include the following in the lib folder:
adafruit_display_text
adafruit_mcp2515
adafruit_ssd1325.py

TODO:
Ask shane if we actually need to grab the current time twice
ask shane if we can't make 'while not next_message is None' at least a little bit more readable
We changed the 0x402 can code here, can we change it in the motor controller code too?
'''

#imports
import board
import busio
import math #not going to use this
import struct #for packing the messages
import time #for waiting a little bit
import analogio
import digitalio
import displayio #for displaying to the screen
import terminalio
import adafruit_ssd1325 #the screen we are using
from adafruit_mcp2515       import MCP2515 as CAN #can stuff
from adafruit_mcp2515.canio import RemoteTransmissionRequest, Message, Match, Timer
from adafruit_display_text import label
import adafruit_mcp2515
import microcontroller 



#display setup
boot_time = time.monotonic()
displayio.release_displays()

#create SPI bus
spi = busio.SPI(board.GP2, board.GP3, board.GP4)

#setup MCP2515 on the SPI bus (CANbus stuff)
can_cs = digitalio.DigitalInOut(board.GP9)
can_cs.switch_to_output()
mcp = CAN(spi, can_cs, baudrate = 500000, crystal_freq = 16000000, silent = False,loopback = False)

#OLED Setup on the SPI bus
cs = board.GP22
dc = board.GP23
reset = board.GP21
WIDTH = 128 #declare it here so we don't have to worry about it later
HEIGHT = 64
BORDER = 0
FONTSCALE = 1
#moar display stuffffff
display_bus = displayio.FourWire(spi, command=dc, chip_select=cs, reset=reset, baudrate=1000000)
display = adafruit_ssd1325.SSD1325(display_bus, width=WIDTH, height=HEIGHT)
display.brightness = 1.0


startTime = time.time() #grab the current time

#display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] =0x000000  # Black

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

#draw the text label
text = "SOLAR CAR ISU\nDCU SCREEN\n"
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

#variable declarations
tire_diameter = 22
mph     = 0
voltage = 0
current = 0
eff     = 0
heatsink_temp = 0
motor_temp = 0
DCU_timeout = 0
prevDCU_time = time.monotonic_ns()

#display declarations
pico_temp_str = ""
motor_temp_str = ""
heatsink_temp_str = ""

#BMS stuff
lowTemp = 22
highTemp = 22

#function creation area 
#the 2 following functions will be used to display all three text groups
def init_screen_writing(a, b, c, t):
    text_group = displayio.Group(scale=a, x=b, y=c)
    text_area = label.Label(terminalio.FONT, text=t, color=0xFFFFFF) #black
    text_group.append(text_area)
    splash.append(text_group)

def write_to_screen(a, b, c, t, sp):
    text_group = displayio.Group(scale=a, x=b, y=c)
    text_area = label.Label(terminalio.FONT, text=t, color=0xFFFFFF) #black
    text_group.append(text_area)
    splash[sp] = text_group


#if we are too far behind on the can queue, we clear it
def _can_is_full():
    mcp._unread_message_queue.clear()


#error sending
def send_error(bool, loc):
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

#going to change the name eventually, used for errors
error_dick = {'BMS': "BMS Fault",'pico_temp': "Pico Overheat",'DCU_timeout': "it ain't got no gas in it" }

#create a function because the same thing will happen if current is a problem or if temp is a problem
def draw_bms_error(fail_str):
    if (current >= 70 or current <= -15):
        # Draw BMS Error
        color_bitmap = displayio.Bitmap(display.width, display.height, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF  # Black
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        splash.append(bg_sprite)
        text_group = displayio.Group(scale=2, x=3, y=12)
        text = "BMS Fault\n" + fail_str
        text_area = label.Label(terminalio.FONT, text=text, color=0x000000)
        text_group.append(text_area)  # Subgroup for text scaling
        splash.append(text_group)
        #print("BMS Fault:") #for help with testing
        #print(current)
        while True: #what does this do? nothing, we simply do nothing until the car is manually rebooted
            pass #pretty neat, huh?


#pleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleaseworkpleasework
#draw Speed Label
text = "S: {:04.1f}".format(mph)
init_screen_writing(3, 3, 12, text)

#draw Efficiency Label
text = "A: {:04.1f}".format(current)
init_screen_writing(3, 3, 41, text)

#draw temp labels
temp_str = "S:{:04.1f} M:{:04.1f} H:{:04.1f}".format(microcontroller.cpu.temperature, motor_temp, heatsink_temp)
init_screen_writing(1, 0, 60, temp_str)


time.sleep(0.5) #wait half a second before collecting can info

runTime = time.time() #grab the time the car started running


#our loop that will run while the car is going
while True:

    with mcp.listen(timeout=0) as listener:
        
        message_count = listener.in_waiting()
        if message_count > 300: #I'm doing it like this because it prevents more calls to the reference stack or whatever we talked about in IT327, slightly more efficient now
            _can_is_full() #this function now just clears the can

        #grab next message
        next_message = listener.receive()
        message_num = 0
        #here is where we write out stuff to the screen

        while not next_message is None: 
            message_num += 1

            #print(message_num)


            #get amps and rpm, calculate mph from rpm
            if next_message.id == 0x402:
                holder = struct.unpack('<ff', next_message.data)
                rpm = holder[0]
                current = holder[1]
                mph = rpm * tire_diameter * 0.003 # * 3.14 * 60 * 1/12 * 5280 = 0.002975, I decided to round a little bit just because we run this calculation multiple times a second, also there is no reason to be doing the whole calculation multiple times a second too
                #print("Message From: {}: [RPM = {}; MPH = {}; A = {}]".format(hex(next_message.id),rpm,mph,current))
                #helps with testing
                
                
                
            #get motor and motor controller temp
            if next_message.id == 0x40B:
                holder = struct.unpack('<ff', next_message.data)
                motor_temp = holder[0]
                heatsink_temp = holder[1]
                #print("Message From: {}: [Motor Temp = {}; Heat Sink = {}]".format(hex(next_message.id),motor_temp,heatsink_temp))
                #helps with testing
                
            #motor controller timeout stuff (i think)
            if next_message == 0x401:
                DCU_timeout = time.monotonic_ns() - prevDCU_time
                prevDCU_time = time.monotonic_ns()


            #grab battery temp data (mainly for BMS reasons)
            if next_message.id == 0x6B1:
                holder = struct.unpack('>hhhxx', next_message.data)
                lowTemp = holder[0]
                highTemp = holder[1]

            #over/under current protection
            if (current >= 70 or current <= -15):
                #print("Amperage over/under")
                draw_bms_error("BATT AMPS")

            #battery temp protection
            elif(highTemp > 45 or lowTemp < 0):
                #print("Battery temp over/under")
                draw_bms_error("BATT TEMP")

            #General Temperature Protection System (GPTS)
            #basically if you see a star after one of the temperatures, the driver needs to be aware and take it easy for a bit until everything cools back down
            pico_temp = microcontroller.cpu.temperature
            pico_temp_str = "P:{:04.1f}".format(pico_temp)
            if(pico_temp >= 45): #we're not exactly sure where problems happen but if we keep it below 45 we know everything will be okay
                pico_temp_str = pico_temp_str + "*"
            else:
                pico_temp_str = pico_temp_str + " "

            motor_temp_str = "M:{:04.1f}".format(motor_temp)
            if(motor_temp >= 70 or motor_temp <= 10): #problems happen at 85c
                motor_temp_str = motor_temp_str + "*"
            else:
                motor_temp_str = motor_temp_str + " "

            heatsink_temp_str = "H:{:04.1f}".format(heatsink_temp)
            if(heatsink_temp >= 70 or heatsink_temp <= 10): #problems at 85c
                heatsink_temp_str = heatsink_temp_str + "*"
                
            temp_str = pico_temp_str + motor_temp_str + heatsink_temp_str

            #Actually writing all the data to the screen
            write_to_screen(3, 3, 12, "S: {:04.1f}".format(mph), -3)
            write_to_screen(3, 3, 41, "A: {:04.1f}".format(current), -2)
            write_to_screen(1, 0, 60, temp_str, -1)

            next_message = listener.receive()


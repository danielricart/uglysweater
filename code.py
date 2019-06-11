import board
import audioio
import digitalio
import time
import touchio
import neopixel
from random import randint
from analogio import AnalogIn
from simpleio import map_range


def blink_update_all_pixels(pixel_object, new_color):
    for p in range(0, len(pixel_object)):
        pixel_object[p] = (0,0,0)
    pixel_object.show()
    time.sleep(0.06)
    for p in range(0, len(pixel_object)):
        pixel_object[p] = new_color[p]
    pixel_object.show()
    time.sleep(0.1)

def update_all_pixels(pixel_object, new_color):
    for p in range(0, len(pixel_object)):
        pixel_object[p] = new_color[p]
    pixel_object.show()

def create_array_of_random_colors(elements=10):
    colors = []
    for i in range(0, elements):
        r = randint(0, 255)  # (0, 85)
        g = randint(0, 200)  # (85, 171)
        b = randint(0, 200)  # (172, 255)
        colors.append((r,g,b))
        # print("generated {0},{1},{2}".format(r,g,b))
    return colors

# embeded slide switch
slide = digitalio.DigitalInOut(board.D7)
slide.direction = digitalio.Direction.INPUT
slide.pull = digitalio.Pull.UP


# embedded LED setup
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

# push buttons
switch_a = digitalio.DigitalInOut(board.D4)
switch_a.direction = digitalio.Direction.INPUT
switch_a.pull = digitalio.Pull.DOWN
switch_b = digitalio.DigitalInOut(board.D5)
switch_b.direction = digitalio.Direction.INPUT
switch_b.pull = digitalio.Pull.DOWN
# Capacitive setup
touch1 = touchio.TouchIn(board.A1)
touch2 = touchio.TouchIn(board.A2)
touch3 = touchio.TouchIn(board.A3)
# touch4 = touchio.TouchIn(board.A4)
# touch5 = touchio.TouchIn(board.A5)
# touch6 = touchio.TouchIn(board.A6)
# touch7 = touchio.TouchIn(board.A7)
 
# Used as a quick&dirty debug switch.
# Automatically adjusts brightness to minimum.
# Set brightness to MAX if slider is on
pixels_brightness = 0.1
if slide.value: 
    led.value = False
    pixels_brightness = 1
else:
    led.value = True
    pixels_brightness = 0.1

# Neopixel LED Party
next_led = 0
last_action = time.monotonic()
last_led_action = 0
pixels = neopixel.NeoPixel(board.NEOPIXEL, 3, brightness=pixels_brightness, auto_write=False)
pixels.fill((0, 0, 0))
pixels.show()

stripe = neopixel.NeoPixel(board.A4, 7, brightness=pixels_brightness, auto_write=False)
stripe.fill((0,0,0))
stripe.show() 

onboard_colors = create_array_of_random_colors(len(pixels))
stripe_colors = create_array_of_random_colors(len(stripe))

# Ambient Light sensing
last_light_action = time.monotonic()
light_sensor = AnalogIn(board.LIGHT)


# enable the speaker
speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
speaker_enable.direction = digitalio.Direction.OUTPUT
speaker_enable.value = False

# Audio Play
wave_file = open("xmascarey.wav", "rb")
wave = audioio.WaveFile(wave_file)
audio = audioio.AudioOut(board.SPEAKER)

def read_touch():
    touch_list = {}
    touch_list["A1"] = touch1.value
    touch_list["A2"] = touch2.value
    touch_list["A3"] = touch3.value
    # touch_list["A4"] = touch4.value
    # touch_list["A5"] = touch5.value
    # touch_list["A6"] = touch6.value
    # touch_list["A7"] = touch7.value
    return touch_list

while True:
    now = time.monotonic()
    touch = read_touch()
    light = light_sensor.value

    if touch['A1'] or touch['A2'] or touch['A3'] or switch_a.value or switch_b.value:
        audio.play(wave, loop=False)
    while audio.playing:
        # blink leds 
        stripe_colors = create_array_of_random_colors(len(stripe))
        blink_update_all_pixels(stripe, stripe_colors)
        pixels_colors = create_array_of_random_colors(len(pixels))
        blink_update_all_pixels(pixels, pixels_colors)
        pass
    audio.stop()

    for A,t in touch.items():
        if t:
            #print("%s touched!" % A)
            pass
        time.sleep(0.01)

    if now - last_light_action > 0.5:
        # light value remaped to pixel position
        peak = map_range(light, 500, 1000, 10, 1) * 0.1
        # print(light)
        # print(peak)

    if now - last_led_action > 1.1:
        update_all_pixels(pixels, onboard_colors)
        update_all_pixels(stripe, stripe_colors)

        onboard_colors = create_array_of_random_colors(len(pixels))
        stripe_colors = create_array_of_random_colors(len(stripe))
        # pixels[next_led] = onboard_colors[next_led]
        # next_led +=1
        # if next_led > 9:
        #     onboard_colors = create_array_of_random_colors(10)
        #     next_led = 0
        last_led_action = time.monotonic()

    last_action = time.monotonic()



def update_one_led_at_a_time():
    pixels[next_led] = onboard_colors[next_led]
    print(onboard_colors[next_led])
    next_led +=1
    if next_led > 9:
        onboard_colors = create_array_of_random_colors(10)
        next_led = 0


def waiting(last_time):
    now = time.monotonic()
    time.sleep(0.01)
    print(now-last_time)
    last_action = time.monotonic()
    return last_action
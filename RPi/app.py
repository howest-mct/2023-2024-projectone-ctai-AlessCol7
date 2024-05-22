# import threading
# import queue

# # Bluez gatt uart service (SERVER)
# from bluetooth_uart_server.bluetooth_uart_server import ble_gatt_uart_loop

# # extend this code so the value received via Bluetooth gets printed on the LCD
# # (maybe together with you Bluetooth device name or Bluetooth MAC?)

# def main():
#     i = 0
#     rx_q = queue.Queue()
#     tx_q = queue.Queue()
#     device_name = "Farmer-pi-gatt-uart" # replace with your own (unique) device name
#     threading.Thread(target=ble_gatt_uart_loop, args=(rx_q, tx_q, device_name), daemon=True).start()
#     while True:
#         try:
#             incoming = rx_q.get(timeout=1) # Wait for up to 1 second 
#             if incoming:
#                 print("In main loop: {}".format(incoming))
#         except Exception as e:
#             pass # nothing in Q 

#         # if i%5 == 0: # Send some data every 5 iterations
#         #     tx_q.put("test{}".format(i))
#         # i += 1
# if __name__ == '__main__':
#     main()

import threading
import queue
import time
import smbus
from bluetooth_uart_server.bluetooth_uart_server import ble_gatt_uart_loop

 
LCD_ADDRESS = 0x27
LCD_CHR = 1
LCD_CMD = 0


LCD_WIDTH = 16  
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

E_PULSE = 0.0005
E_DELAY = 0.0005

 

bus = smbus.SMBus(1)

 

def lcd_init():

    lcd_byte(0x33, LCD_CMD)

    lcd_byte(0x32, LCD_CMD)

    lcd_byte(0x06, LCD_CMD)

    lcd_byte(0x0C, LCD_CMD)

    lcd_byte(0x28, LCD_CMD)

    lcd_byte(0x01, LCD_CMD)

    time.sleep(E_DELAY)

 

def lcd_byte(bits, mode):

    bits_high = mode | (bits & 0xF0) | 0x08

    bits_low = mode | ((bits << 4) & 0xF0) | 0x08

 

    bus.write_byte(LCD_ADDRESS, bits_high)

    lcd_toggle_enable(bits_high)

 

    bus.write_byte(LCD_ADDRESS, bits_low)

    lcd_toggle_enable(bits_low)

 

def lcd_toggle_enable(bits):

    time.sleep(E_DELAY)

    bus.write_byte(LCD_ADDRESS, (bits | 0x04))

    time.sleep(E_DELAY)

    bus.write_byte(LCD_ADDRESS, (bits & ~0x04))

    time.sleep(E_DELAY)

 

def lcd_string1(message, line=LCD_LINE_1):

    message = message.ljust(LCD_WIDTH," ")

    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):

        lcd_byte(ord(message[i]),LCD_CHR)

 

def lcd_string2(message, line=LCD_LINE_2):

    message = message.ljust(LCD_WIDTH," ")

    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):

        lcd_byte(ord(message[i]),LCD_CHR)
def main():
    i = 0
    rx_q = queue.Queue()
    tx_q = queue.Queue()
    device_name = "alesscol-pi-gatt-uart"  # TODO: replace with your own (unique) device name
    
    
    threading.Thread(target=ble_gatt_uart_loop, args=(rx_q, tx_q, device_name), daemon=True).start()
    lcd_init()
    while True:
        try:
            incoming = rx_q.get(timeout=1)  # Wait for up to 1 second 
            if incoming:
                # print("In main loop: {}".format(incoming))
                # Display the received message on the LCD
                # lcd_init()
                lcd_string1(f"In main loop {incoming}")
                lcd_string2(f"D8:3A:DD:E1:55:CB")
        except Exception as e:
            pass  # nothing in Q 

        # Uncomment if you want to send data periodically
        # if i % 5 == 0:  # Send some data every 5 iterations
        #     tx_q.put("test{}".format(i))
        # i += 1

if __name__ == '__main__':
    main()



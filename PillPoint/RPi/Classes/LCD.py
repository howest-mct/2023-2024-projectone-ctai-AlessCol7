import time
import smbus

# Constants for LCD control
I2C_ADDR = 0x27  # I2C device address
LCD_WIDTH = 16   # Maximum characters per line
LCD_CHR = 1      # bit value for bit0; sets mode - Sending data
LCD_CMD = 0      # bit value for bit0; bit0 sets mode - Sending command
LCD_LINE_1 = 0x80   # Instruction to go to beginning of line 1
LCD_LINE_2 = 0xC0   # Instruction to go to beginning of line 2
LCD_BACKLIGHT = 0x08  # Data bit value to turn backlight on
ENABLE = 0b00000100   # Enable bit value
E_PULSE = 0.0002   # Adjusted pulse duration for more reliability
E_DELAY = 0.0002    # Adjusted delay between commands for more reliability

class LCD:
    def __init__(self, i2c_addr):
        self.i2c_addr = i2c_addr
        self.bus = smbus.SMBus(1)
        self.init_LCD()

    def init_LCD(self):
        try:
            # Initialization sequence for 4-bit mode
            self.send_instruction(0x33)  # Initialize
            self.send_instruction(0x32)  # Set to 4-bit mode
            self.send_instruction(0x28)  # 2 Lines, 5x8 font
            self.send_instruction(0x0C)  # Display on, cursor off, blink off
            self.send_instruction(0x06)  # Increment cursor (shift cursor to right)
            self.clear_display()          # Clear display

        except Exception as e:
            print("LCD initialization failed:", e)

    def send_byte_with_e_toggle(self, bits):
        # Send data to the LCD with enable toggling
        try:
            self.bus.write_byte(I2C_ADDR, (bits | ENABLE))
            time.sleep(E_PULSE)
            self.bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
            time.sleep(E_DELAY)
        except Exception as e:
            print("Error sending byte with E toggle:", e)

    def set_data_bits(self, bits, mode):
        # Set data bits in 4-bit mode
        upper_nibble = (bits & 0xF0) | mode | LCD_BACKLIGHT
        lower_nibble = ((bits << 4) & 0xF0) | mode | LCD_BACKLIGHT
        self.send_byte_with_e_toggle(upper_nibble)
        self.send_byte_with_e_toggle(lower_nibble)

    def send_instruction(self, byte):
        # Send instruction to the LCD
        self.set_data_bits(byte, LCD_CMD)

    def send_character(self, byte):
        # Send character to the LCD
        self.set_data_bits(byte, LCD_CHR)

    def send_string(self, message, line):
        # Send string to the LCD
        if line == 1:
            self.send_instruction(LCD_LINE_1)
        elif line == 2:
            self.send_instruction(LCD_LINE_2)

        if len(message) <= LCD_WIDTH:
            for char in message:
                self.send_character(ord(char))
        else:
            # Scroll the message
            for i in range(len(message) - LCD_WIDTH + 1):
                self.send_instruction(LCD_LINE_1 if line == 1 else LCD_LINE_2)
                substring = message[i:i + LCD_WIDTH]
                for char in substring:
                    self.send_character(ord(char))
                time.sleep(0.5)  # Adjust scrolling speed

    def clear_display(self):
        # Clear the LCD display
        self.send_instruction(0x01)
        time.sleep(0.002)  # Additional delay after clear display

    def cleanup(self):
        self.clear_display()
        self.bus.close()

# def main():
#     # Initialize display
#     lcd = LCD(I2C_ADDR)

#     try:
#         while True:
#             user_input = input("Enter a message: ")
#             lcd.send_string(user_input, 1)
#             time.sleep(3)
#             lcd.clear_display()
#     except KeyboardInterrupt:
#         print("\nProgram terminated by user.")
#     except Exception as e:
#         print("An error occurred:", e)
#     finally:
#         # Clean up: Clear display and close connection
#         lcd.cleanup()

# if __name__ == '__main__':
#     main()

import time
import argparse
from rpi_hardware_pwm import HardwarePWM

"""
PWM Test Code

Features:
- Customizable PWM on Pin 12 that runs until keyboard interrupt (CTRL C)
- Stops PWM upon clean exit
"""
def pwmLoop():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='PWM Control with User-Specified Duty Cycle')
    parser.add_argument('--duty', type=float, required=True, help='Duty cycle percentage (0-100)')
    args = parser.parse_args()

    # Check if duty arg is within valid range
    if not 0 <= args.duty <= 100:
        raise ValueError("Duty cycle must be between 0 and 100")

    # Initialize PWM
    pwm = HardwarePWM(pwm_channel=0, hz=1000, chip=0)
    pwm.start(args.duty)
    
    # CTRL C to cleanly exit and pwm
    try:
        print(f"Running PWM at {args.duty}% duty cycle. Press CTRL+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pwm.stop()

def main():
    pwmLoop()

if __name__ == "__main__":
    main()
from machine import Pin, PWM
import time


class Servo:

    def __init__(self, pin_num):
        self.pin = pin_num
        self.freq = 50
        self.duty = 0
        self.interval = 50  # ms
        self.servo = PWM(Pin(self.pin), freq=self.freq, duty=self.duty)

    def position(self,angle):
        time.sleep_us(self.interval)
        self.servo.duty(int((angle*2/180+0.5)/20*1023))

    def set_speed(self,_interval):
        self.interval = _interval

def button_control():
  
  servo1 = Servo(26)
  servo2 = Servo(27)
  
  '''button event control'''
  key1=Pin(33,Pin.IN,Pin.PULL_UP) #鏋勫缓 KEY 瀵硅薄  
  key2=Pin(32,Pin.IN,Pin.PULL_UP)
  key3=Pin(35,Pin.IN,Pin.PULL_UP)
  key4=Pin(34,Pin.IN,Pin.PULL_UP)

  angle1 = 0
  angle2 = 0
  dir_flag_1 = 2
  dir_flag_2 = 2

  while True:
      if key1.value()==0:
          time.sleep_ms(10)  
          if key1.value()==0:
              if dir_flag_1 != 1:
                  angle1 = angle1 + 1

      if key2.value()==0:
          time.sleep_ms(10) 
          if key2.value()==0:
              if dir_flag_1 != 0:
                  angle1 = angle1 - 1

      if angle1 == 180:
          dir_flag_1 = 1
      elif angle1 == 0:
          dir_flag_1 = 0
      else:
          dir_flag_1 = 2

      if key3.value()==0:
          time.sleep_ms(10)   
          if key3.value()==0:
              if dir_flag_2 != 1:
                  angle2 = angle2 + 1

      if key4.value()==0:
          time.sleep_ms(10)   
          if key4.value()==0:
              if dir_flag_2 != 0:
                  angle2 = angle2 - 1

      if angle2 == 135:
          dir_flag_2 = 1
      elif angle2 == 0:
          dir_flag_2 = 0
      else:
          dir_flag_2 = 2

      servo1.position(angle1)
      servo2.position(angle2)


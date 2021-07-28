import ubluetooth as bt
from ble.tools import BLETools
from ble.const import BLEConst
from machine import Pin, PWM
import time

__UART_UUID = bt.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
__RX_UUID = bt.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
__TX_UUID = bt.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")

__UART_SERVICE = (
	__UART_UUID,
	(
		(__TX_UUID, bt.FLAG_NOTIFY,),
		(__RX_UUID, bt.FLAG_WRITE,),
	),
)


class BLEUART:
	def __init__(self, ble, rx_callback=None, name="MSTIFIY", rxbuf=100):
		self.__ble = ble
		self.__rx_cb = rx_callback
		self.__conn_handle = None

		self.__write = self.__ble.gatts_write
		self.__read = self.__ble.gatts_read
		self.__notify = self.__ble.gatts_notify

		self.__ble.active(False)
		print("activating ble...")
		self.__ble.active(True)
		print("ble activated")

		self.__ble.config(rxbuf=rxbuf)
		self.__ble.irq(self.__irq)
		self.__register_services()

		self.__adv_payload = BLETools.advertising_generic_payload(
			services=(__UART_UUID,),
			appearance=BLEConst.Appearance.GENERIC_COMPUTER,
		)
		self.__resp_payload = BLETools.advertising_resp_payload(
			name=name
		)

		self.__advertise()

	def __register_services(self):
		(
			(
				self.__tx_handle,
				self.__rx_handle,
			),
		) = self.__ble.gatts_register_services((__UART_SERVICE,))

	def __advertise(self, interval_us=500000):
		self.__ble.gap_advertise(None)
		self.__ble.gap_advertise(interval_us, adv_data=self.__adv_payload, resp_data=self.__resp_payload)
		print("advertising...")

	def __irq(self, event, data):
		if event == BLEConst.IRQ.IRQ_CENTRAL_CONNECT:
			self.__conn_handle, addr_type, addr, = data
			print("[{}] connected, handle: {}".format(BLETools.decode_mac(addr), self.__conn_handle))

			self.__ble.gap_advertise(None)
		elif event == BLEConst.IRQ.IRQ_CENTRAL_DISCONNECT:
			self.__conn_handle, _, addr, = data
			print("[{}] disconnected, handle: {}".format(BLETools.decode_mac(addr), self.__conn_handle))

			self.__conn_handle = None
			self.__advertise()
		elif event == BLEConst.IRQ.IRQ_GATTS_WRITE:
			conn_handle, value_handle = data
      
			if conn_handle == self.__conn_handle and value_handle == self.__rx_handle:
				if self.__rx_cb:
					self.__rx_cb(self.__read(self.__rx_handle))

	def send(self, data):
		"""
		将数据写入本地缓存，并推送到中心设备
		"""
		self.__write(self.__tx_handle, data)

		if self.__conn_handle is not None:
			self.__notify(self.__conn_handle, self.__tx_handle, data)


class Servo:

    def __init__(self, pin_num):
        self.pin = pin_num
        self.freq = 50
        self.duty = 0
        self.interval = 5  # ms
        self.servo = PWM(Pin(self.pin), freq=self.freq, duty=self.duty)

    def position(self,angle):
        time.sleep_us(self.interval)
        self.servo.duty(int((angle*2/180+0.5)/20*1023))

    def set_speed(self,_interval):
        self.interval = _interval


# create servo targets
servo1 = Servo(26)
servo2 = Servo(27)

# define callback method
def rx_callback(data):
  
	# slide bar control angle
	angle_list = [x for x in data]
	# print("X: ",angle_list[1],"   Y : ",angle_list[3])
	servo1.position(angle_list[1])
	servo2.position(angle_list[3])

# create ble target
ble = bt.BLE()
uart = BLEUART(ble, rx_callback)

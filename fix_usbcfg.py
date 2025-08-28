import serial
import serial.tools.list_ports
import time

TARGET_QCFG = '0x2c7c,0x0801,2,1,1,0,0,1,0'

def is_at_port(port):
    try:
        ser = serial.Serial(port.device, 115200, timeout=1)
        ser.write(b'AT\r\n')
        time.sleep(0.3)
        resp = ser.read_all().decode(errors='ignore')
        ser.close()
        return 'OK' in resp
    except:
        return False

def fix_usbcfg(port):
    try:
        print(f"[INFO] 嘗試連接 AT PORT: {port.device}")
        ser = serial.Serial(port.device, 115200, timeout=1)
        ser.write(b'AT+QCFG="usbcfg"\r\n')
        time.sleep(0.5)
        resp = ser.read_all().decode(errors='ignore')
        print(f"[INFO] 目前設定為: {resp.strip()}")

        if TARGET_QCFG not in resp:
            cmd = f'AT+QCFG="usbcfg",{TARGET_QCFG}\r\n'
            print("[INFO] 設定 usbcfg 中...")
            ser.write(cmd.encode())
            time.sleep(1)
            result = ser.read_all().decode(errors='ignore')
            print(f"[回應] {result.strip()}")

            if 'OK' in result:
                print("[INFO] 設定成功，DUT MU310 執行重啟...")
                ser.write(b'AT+CFUN=1,1\r\n')
            else:
                print("[錯誤] 設定失敗，請手動檢查DUT。")
        else:
            print("[INFO] usbcfg 設定正確，無需變更。")

        ser.close()

    except Exception as e:
        print(f"[錯誤] 無法操作 {port.device}，錯誤：{e}")

if __name__ == "__main__":
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if is_at_port(port):
            fix_usbcfg(port)
            break
    else:
        print("[錯誤] 找不到任何可回應的 AT PORT。")

#這個 AT 指令意思是：模組功能開關重啟 (reset and full functionality)

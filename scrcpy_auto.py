# (c) 2019 Moker

import subprocess
from os import path
import re
from sys import argv


def command_execute(dir, com_list, suc_msg, err_msg):
  try:
    output = subprocess.check_output(com_list, shell=True, cwd=dir).decode('cp932')
    print(suc_msg)
  except subprocess.CalledProcessError as e:
    print("[Error] " + err_msg)
    print(e.output.decode('cp932'))
    return -1


def get_cwd():
  return path.dirname(path.abspath(__file__))


def show_help(dir):
  try:
    print("--------")
    print("You can run with options")
    print("Showing scrcpy help below")
    print("--------")
    output = subprocess.check_output(["scrcpy.exe", "--help"], shell=True, cwd=dir).decode('cp932')
  except subprocess.CalledProcessError as e:
    print("[Error] Error occured when disconnecting...")
    print(e.output.decode('cp932'))
    return -1


def get_adb_devices(dir):
    output = subprocess.check_output(["adb.exe", "devices"], shell=True, cwd=dir).decode('cp932')   # TODO: try-except
    return output


def initialize(dir):
  command_execute(dir, ["adb.exe", "kill-server"], "Killing adb server", "Error occured when killing server")
  command_execute(dir, ["adb.exe", "disconnect"], "Disconnecting", "Error o")


def get_ipaddr(dir, serial):
  try:
    output = subprocess.check_output(["adb.exe", "-s", serial, "shell", "ip", "addr", "show", "wlan0"], shell=True, cwd=dir).decode('cp932')
    ipaddr = re.search("192\.168\.[0-9\.]*", output).group()
    return ipaddr
  except subprocess.CalledProcessError as e:
    print("[Error] Error occured when checking ip address...")
    print(e.output.decode('cp932'))
    return -1


def main():
  cwd = get_cwd()

  if ("--help" in argv) or ("-h" in argv):
    show_help(cwd)
    return 0

  output = get_adb_devices(cwd)
  
  if 'offline' in output:
    print("Offline device detected.Initializing...")
    print("--------adb-devices--------")
    print(output)
    print("---------------------------")
    initialize(cwd)
    output = get_adb_devices(cwd)
  
  device_cnt = output.count('device') - 1     #except 'list of "device"s'
  if device_cnt >= 1:
    if device_cnt > 1:
      print("Multiple devices detected.")
      output_ls = output.split("\r\n")[1:-2]
      print("0: Finish the program")
      device_ls = []
      for k, v in enumerate(output_ls):
        tmp_ls = v.split("\t")
        if tmp_ls[1] == 'device':
          device_ls.append(tmp_ls[0])
          print(str(k+1) + ": \"" + tmp_ls[0] + "\"")
      
      while (True):
        answer = input("Choose from above : ")
        try:
          answer = int(answer)
        except:
          continue
        
        if answer in range(device_cnt+1):
          if answer == 0:
            return -1   # 0 means finishing program
          else:
            serial = device_ls[answer-1]
            break
    
    else:
      match = re.search(r"\S+\tdevice", output)
      serial = match.group().split()[0]
      device_ls = [serial]
    
    print("Device \"" + serial + "\" detected")

    if serial.startswith("192.168."):
      do_connect = False
    
    elif get_ipaddr(cwd, serial)+":5555" in device_ls:
      print("The device is already connected via tcpip.")
      while True:
        data = input("Do you want to connect via WiFi?(y/n) : ")
        if data in ['y', 'n']:
          break
      if data == 'y':
        serial = get_ipaddr(cwd, serial)+":5555"
      do_connect = False

    else:
      while True:
        data = input("Do you want to connect via WiFi?(y/n) : ")
        if data in ['y', 'n']:
          if data == 'y':
            do_connect = True
          else:
            do_connect = False
          break
    
    if do_connect == True:
      ipaddr = get_ipaddr(cwd, serial)
      if (ipaddr == -1):
        return -1
      
      if command_execute(cwd, ["adb.exe", "-s", serial, "tcpip", "5555"], "Successfully opened tcpip port", "Error occured when opening tcpip port") == -1:
        return -1
      
      if command_execute(cwd, ["adb.exe", "-s", serial, "connect", ipaddr+":5555"], "Successfully connected", "Error occured when connecting") == -1:
        return -1
      
      serial = ipaddr + ":5555"
    
  else:   # device_cnt == 0
    print("[Error] No device detected.")
    return -1
  
  try:
    if len(argv) == 1:
      output = subprocess.check_output(["scrcpy.exe", "-c", "1000:1000:110:220", "-n", "-s", serial], shell=True, cwd=cwd).decode('cp932')

    else:
      output = subprocess.check_output(["scrcpy.exe"] + argv[1:], shell=True, cwd=cwd).decode('cp932')

  except subprocess.CalledProcessError as e:
    print("[Error] Error occured when executing scrcpy...")
    print(e.output.decode('cp932'))
    return -1


if __name__ == '__main__':
  main()
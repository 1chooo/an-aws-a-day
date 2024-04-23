import os
from datetime import datetime

# 获取 /var 目录下的所有文件和文件夹
var_contents = os.listdir('/tmp')

print(str(var_contents)[0:30])
current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print(current_date)

from datetime import datetime
current_date_and_time = datetime.now()

print("The current year is ", current_date_and_time.year) # Output: The current year is  2022
print("The current month is ", current_date_and_time.month) # Output: The current month is  3 
print("The current day is ", current_date_and_time.day) # Output: The current day is  19
print("The current hour is ", current_date_and_time.hour) # Output: The current hour is  10 
print("The current minute is ", current_date_and_time.minute) # Output: The current minute is  49
print("The current second is ", current_date_and_time.second) # Output: The current second is  18
print("The current second is ", current_date_and_time.microsecond) # Output: The current second is  18
current_date_and_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
print(current_date_and_time)
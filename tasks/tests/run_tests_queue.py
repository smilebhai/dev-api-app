from time import sleep
from tasks import add_numbers
for index in range(50):
    task = add_numbers.delay(index, 1)
    sleep(2)

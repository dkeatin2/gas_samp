#should pull the id of the pico from flash.
#dunno if this is best vs the other way who knows


import machine
s = machine.unique_id()
for b in s:
    print(hex(b)[2:],end=" ")
print()
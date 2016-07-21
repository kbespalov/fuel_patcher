from api import *

patched = [x.strip() for x in open('patched.txt').readlines()]

computes = [node for node in fuel_computes() if node not in patched]
controllers = [node for node in fuel_controllers() if node not in patched]

print 'COMPUTE: ', computes
print 'CONTROLLER:', controllers

copy_patch(controllers)
copy_patch(computes)

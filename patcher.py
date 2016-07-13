from api import *


patched = ['10.20.0.15']

computes = fuel_computes()

'computes':
print computes

controllers = fuel_controllers()

'controllers':
print controllers

'filtered'
print [node for node in controllers if node not in patched]

copy_patch([node for node in controllers if node not in patched])
copy_patch(computes)

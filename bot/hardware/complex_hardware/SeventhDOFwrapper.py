import os, sys
import pprint 
import pyDMCC
from SeventhDOF import Rail_Mover


Position = 0
Rail = Rail_Mover()


while True:
    Input = input("Position:  ")
    if Input == -1:
        break
    elif Input == 0:
        Rail.ResetToHome()
    elif Input <= 4: 
        Position = Input
        Rail.Orientor(Position)
    else:
        RawDisplacement = input("What is the displacement:  ")
        Rail.DisplacementConverter(RawDisplacement)
    
    
    
    


    


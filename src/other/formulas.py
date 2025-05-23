import math

def ease_out_expo(t, b, c, d):
                                                                      
    if t >= d:
        return b + c
    return c * (-math.pow(2, -10 * t / d) + 1) + b
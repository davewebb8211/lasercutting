from scipy import *
from scipy.optimize import *


rr = 2.0
r0 = 10.0
gamma = degrees(50.0)

def func(x):
    beta = x[1]
    c = x[0]
    out = [1.0/cos(gamma/2.0) * (r0 - (r0 - rr) * cos(beta) - rr * sin(gamma/2.0)) - c]
    out.append(1.0/(r0-rr) * (rr * cos(gamma/2.0) - c * sin(gamma/2.0)))
    return out

x02 = fsolve(func, [0, 0])
print(x02)



import numpy as np

points = [(i,j) for i in range(4) for j in range(4)]

Theta = np.array([
    [1,1],
    [0,1]
])

def schedule(p):
    v = np.array([[p[0]],[p[1]]])
    t = Theta @ v
    return (int(t[0,0]), int(t[1,0]))

order = sorted(points, key=schedule)

for p in order:
    print(p, "->", schedule(p))

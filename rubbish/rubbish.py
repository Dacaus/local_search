points = [(i,j) for i in range(4) for j in range(4)]

def sched(i,j):
    return (i+j,j)

order = sorted(points, key=lambda x: sched(x[0],x[1]))

for p in order:
    print(p, "->", sched(p[0],p[1]))
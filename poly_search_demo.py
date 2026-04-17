# poly_search_demo.py
# pip install numpy matplotlib

import numpy as np
import matplotlib.pyplot as plt
import random

N = 8   # iteration space size

# 1. schedule matrix

def schedule(theta, i, j):
    v = np.array([[i], [j]])
    t = theta @ v
    return (int(t[0,0]), int(t[1,0]))


# =========================
# 2. legality check
# dependence:
# (i,j-1) -> (i,j)
# must satisfy:
# theta(i,j-1) < theta(i,j)
# =========================

def legal(theta):
    for i in range(N):
        for j in range(1, N):
            a = schedule(theta, i, j-1)
            b = schedule(theta, i, j)

            if a >= b:   # lexicographic compare
                return False
    return True



# 3. locality score
# reward row-major style
# smaller jump = better

def locality_score(theta):
    points = [(i,j) for i in range(N) for j in range(N)]
    order = sorted(points, key=lambda p: schedule(theta,p[0],p[1]))

    score = 0

    for k in range(len(order)-1):
        x1,y1 = order[k]
        x2,y2 = order[k+1]

        dist = abs(x1-x2) + abs(y1-y2)
        score -= dist

    return score


# 4. random matrix search

results = []

for a in range(-2,3):
    for b in range(-2,3):
        for c in range(-2,3):
            for d in range(-2,3):

                theta = np.array([
                    [a,b],
                    [c,d]
                ])

                if np.linalg.det(theta) == 0:
                    continue

                if legal(theta):
                    score = locality_score(theta)
                    results.append((theta, score))



# 5. top schedules

results.sort(key=lambda x:x[1], reverse=True)

print("Top 10 Legal Schedules:\n")

for i in range(min(10,len(results))):
    print("Rank", i+1)
    print(results[i][0])
    print("Score:", results[i][1])
    print()


# =========================
# 6. heatmap over first row
# fix second row = [0,1]
# =========================

heat = np.zeros((5,5))

for a in range(-2,3):
    for b in range(-2,3):

        theta = np.array([
            [a,b],
            [0,1]
        ])

        if np.linalg.det(theta)==0:
            heat[a+2,b+2] = np.nan
            continue

        if legal(theta):
            heat[a+2,b+2] = locality_score(theta)
        else:
            heat[a+2,b+2] = np.nan

plt.figure(figsize=(8,6))
plt.imshow(heat, origin="lower")
plt.colorbar(label="Locality Score")
plt.xticks(range(5), [-2,-1,0,1,2])
plt.yticks(range(5), [-2,-1,0,1,2])
plt.xlabel("b")
plt.ylabel("a")
plt.title("Schedule Landscape\nTheta=[[a,b],[0,1]]")
# plt.show()
plt.savefig('heatmap.png')
print("Heatmap saved as heatmap.png")
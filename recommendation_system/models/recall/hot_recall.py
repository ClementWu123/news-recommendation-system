import matplotlib.pyplot as plt
import math


def decay_function(alpha=0.01, init=10000, deltaT=100):
    data = []
    for t in range(deltaT):
        if len(data) == 0:
            temp = init / math.pow(t + 1, alpha)  # math.exp(-alpha * math.log(t + 1))
        else:
            temp = data[-1] / math.pow(t + 1, alpha)  # math.exp(-alpha * math.log(t + 1))
        data.append(temp)

    plt.plot([t for t in range(deltaT)], data, label='alpha={}'.format(alpha))


init = 10000
deltaT = 90
plt.figure(figsize=(20, 8))
decay_function(0.001, init, deltaT)

plt.xticks([t for t in range(deltaT)])
plt.grid()
plt.legend()
plt.show()

# task 4: GPS vs VIO plots from log.csv
import numpy as np
import matplotlib.pyplot as plt

d = np.genfromtxt('log.csv', delimiter=',', names=True)
t = d['t'] - d['t'][0]
error = np.hypot(d['vio_n'] - d['gps_n'], d['vio_e'] - d['gps_e'])
rmse = np.sqrt(np.mean(error ** 2))
print('RMSE %.2f m, max %.2f m, final %.2f m' % (rmse, error.max(), error[-1]))

fig, ax = plt.subplots(1, 3, figsize=(16, 5))

ax[0].plot(d['gps_e'], d['gps_n'], 'g', label='GPS')
ax[0].plot(d['vio_e'], d['vio_n'], 'r--', label='VIO')
ax[0].set_xlabel('East (m)')
ax[0].set_ylabel('North (m)')
ax[0].set_title('Top view')
ax[0].axis('equal')

ax[1].plot(t, d['gps_n'], 'g', label='GPS north')
ax[1].plot(t, d['vio_n'], 'r--', label='VIO north')
ax[1].plot(t, d['gps_e'], 'b', label='GPS east')
ax[1].plot(t, d['vio_e'], 'm--', label='VIO east')
ax[1].set_xlabel('time (s)')
ax[1].set_ylabel('position (m)')
ax[1].set_title('Position vs time')

ax[2].plot(t, error)
ax[2].set_xlabel('time (s)')
ax[2].set_ylabel('error (m)')
ax[2].set_title('Distance between VIO and GPS (RMSE %.2f m)' % rmse)

for a in ax:
    a.grid(True)
ax[0].legend()
ax[1].legend()
plt.tight_layout()
plt.savefig('vio_vs_gps.png', dpi=150)
print('saved vio_vs_gps.png')

# makes a ground texture and a gazebo world with the iris + a downward camera
import os
import numpy as np
import cv2

here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, 'world')
os.makedirs(out, exist_ok=True)

# random blobs and boxes so the camera has corners to track
rng = np.random.default_rng(0)
size = 2048
img = np.zeros((size, size, 3), np.float32)
for s in (8, 32, 128):
    noise = rng.random((size // s, size // s, 3)).astype(np.float32)
    img += cv2.resize(noise, (size, size))
img = (255 * img / img.max()).astype(np.uint8)
for i in range(1500):
    x, y = (int(v) for v in rng.integers(0, size, 2))
    color = tuple(int(c) for c in rng.integers(0, 255, 3))
    if i % 2:
        cv2.circle(img, (x, y), int(rng.integers(4, 16)), color, -1)
    else:
        cv2.rectangle(img, (x, y), (x + int(rng.integers(8, 40)), y + int(rng.integers(8, 40))), color, -1)
texture = os.path.join(out, 'ground.png')
cv2.imwrite(texture, img)

world = open(os.path.join(here, 'world_template.sdf')).read().replace('TEXTURE_PATH', texture)
open(os.path.join(out, 'vio_world.sdf'), 'w').write(world)
print('world written to', os.path.join(out, 'vio_world.sdf'))

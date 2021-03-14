This project aims to be able to create Manim animations in python and play and interact with them in real-time with only a web browser.
It uses a python tool named "Transcrypt" to convert all python files to javascript.
However, many libraries need to be implemented in javascript. There is a list below containing all the libraries that couldn't compile, due to not having a javascript implementation (for example numpy, operators, copy...) or just because you couldn't use them in a web browser (for example moderngl, subprocess, os...). Currently, the impossible imports are just commented such that manim can compile to js.
It is important to consider that creating an implementation of numpy in javascript would take many months of hard work, it's important to start creating the functions Manim needs to use. They are listed in the *Numpy functions* section.

For further information about the way libraries are used when they are converted to javascript, please consult the documentation of [*Transcrypt*](https://transcrypt.org/docs/html/index.html)

## Libraries to implement in javascript
- [ ] numpy
- [ ] os (normally not needed in the browser)
- [ ] mapbox_earcut
- [ ] yaml
- [ ] screeninfo (normally not needed in the browser)
- [ ] importlib
- [ ] colour
- [ ] argparse (normally not needed in the browser)
- [ ] urllib.request
- [ ] validators
- [ ] operator
- [x] functools
- [ ] scipy
- [ ] PIL
- [x] copy
- [ ] moderngl
- [ ] matplotlib.cm
- [ ] enum
- [ ] manimpango
- [ ] minidom
- [ ] hashlib
- [ ] Path (normally not needed in the browser)
- [ ] contextlib (to remove from the code, doesn't work in javascript)
- [ ] moderngl_window (normally not needed in the browser)
- [ ] subprocess (normally not needed in the browser)
- [ ] PygletWindowKeys
- [ ] numbers

## Numpy functions
All the lines where numpy functions were called can be found in the file named *numpy-functions.txt*. They can serve as examples for the numpy implementation.
- np.all
- np.dot
- np.repeat
- np.multiply
- np.shape
- np.cross
- np.array
- np.zeros
- np.identity
- np.angle
- np.transpose
- np.abs
- np.arange
- np.arccos
- np.mean
- np.true_divide
- np.logical_or
- np.exp
- np.clip
- np.float32
- np.floor
- np.ceil
- np.linspace
- np.sign
- np.cos
- np.sin
- np.sqrt
- np.vstack
- np.random_seed
- np.hstack
- np.ones
- np.seterr
- np.isclose
- np.linalg.inv
- np.arctan
- np.random.random
- np.random.seed
- np.log
- np.dtype
- np.round
- np.frombuffer
- np.linalg.norm
- np.apply_along_axis
- np.max
- np.full_like

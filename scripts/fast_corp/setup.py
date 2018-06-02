from distutils.core import setup;
from Cython.Build import cythonize;

setup(name = 'fast_corp', ext_modules=cythonize("random_utils.pyx"));

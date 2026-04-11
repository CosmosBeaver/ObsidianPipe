from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "cpp_linker",  # Numele modulului pe care îl imporți în Python
        ["cpp_engine/smart_linker.cpp", "cpp_engine/bindings.cpp"], # Sursele C++
        cxx_std=17,    # Standardul C++ folosit
    ),
]

setup(
    name="cpp_linker",
    version="1.0",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
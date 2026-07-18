FROM python:3.12-slim

#installs system dependencies required for compiling C++ and CMake
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    gcc \
    g++ \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

#set the working directory inside the container
WORKDIR /ObsidianPipe

#install pybind11 before compiling C++ engine
RUN pip install --no-cache-dir pybind11

#copy the C++ engine source code and CMake config
COPY cpp_engine/ /ObsidianPipe/cpp_engine/

#compile the C++ engine into a Linux compatible library
RUN mkdir -p /ObsidianPipe/cpp_engine/build && \
    cd /ObsidianPipe/cpp_engine/build && \
    cmake .. -Dpybind11_DIR=$(python -c "import pybind11; print(pybind11.get_cmake_dir())") && \
    make

#copy the python source code and requirements
COPY requirements.txt /ObsidianPipe/
COPY src/ /ObsidianPipe/src/

#move the newly compiled Linux C++ extension to the src directory
RUN cp /ObsidianPipe/cpp_engine/build/cpp_linker*.so /ObsidianPipe/src/ 2>/dev/null || \
    cp /ObsidianPipe/cpp_engine/build/libcpp_linker.so /ObsidianPipe/src/cpp_linker.so || true

#install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#set environment variables (prevents python from writing pyc files)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#define the default command to run your orchestrator
ENTRYPOINT ["python", "src/main.py"]
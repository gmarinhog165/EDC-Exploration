#!/bin/bash

# Set the source directory and output (class) directory
SRC_DIR="."
OUT_DIR="out"

# Create the output directory if it doesn't exist
mkdir -p "$OUT_DIR"

# Compile the Java files
echo "Compiling Java sources..."
javac -d "$OUT_DIR" $(find "$SRC_DIR" -name "*.java")

# Check if compilation succeeded
if [ $? -ne 0 ]; then
    echo "Compilation failed!"
    exit 1
fi

# Run the main class
echo "Running Benchmark..."
java -cp "$OUT_DIR" pt.uminho.di.Benchmark.Main

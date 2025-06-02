#!/bin/bash

# Variables
MODULE_NAME="foobar_sdec"
DEVICE_PATH="/dev/foobar_sdec"
MODULE_PATH="./foobar_sdec.ko"

# Make
echo "Building the module..."
make clean
make || { echo "Make failed. Please check the output."; exit 1; }   



# Remove the existing module
echo "Removing existing module..."
sudo rmmod $MODULE_NAME 2>/dev/null || echo "Module not loaded."

# Insert the module
echo "Inserting module..."
sudo insmod $MODULE_PATH || { echo "Failed to insert module."; exit 1; }

# Set permissions for the device file
echo "Setting permissions for $DEVICE_PATH..."
sudo chmod 666 $DEVICE_PATH || { echo "Failed to set permissions."; exit 1; }

echo "Driver reloaded successfully!"
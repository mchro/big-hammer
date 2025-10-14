#!/bin/bash
set -e  # Exit on any error
curl -f https://httpstat.us/503
echo "This should not be reached if curl fails"

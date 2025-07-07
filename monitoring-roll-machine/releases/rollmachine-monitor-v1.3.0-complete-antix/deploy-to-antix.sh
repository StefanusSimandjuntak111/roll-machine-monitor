#/bin/bash 
# Deployment helper for antiX systems 
echo "🚀 Deploying Roll Machine Monitor to antiX..." 
echo "1. Extracting package..." 
tar -xzf rollmachine-monitor-v1.3.0-complete-antix.tar.gz 
cd rollmachine-monitor-v1.3.0-complete-antix 
echo "2. Starting installation..." 
sudo ./install-complete-antix.sh 

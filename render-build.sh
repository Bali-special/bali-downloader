#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing python dependencies..."
pip install -r requirements.txt
pip install -U yt-dlp

echo "Downloading and extracting ffmpeg static build for Linux..."
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar xvf ffmpeg-release-amd64-static.tar.xz
mv ffmpeg-*-static/ffmpeg .
mv ffmpeg-*-static/ffprobe .
rm -rf ffmpeg-release-amd64-static.tar.xz ffmpeg-*-static

echo "ffmpeg installation complete."

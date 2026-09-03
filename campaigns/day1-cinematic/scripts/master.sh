#!/usr/bin/env bash
set -euo pipefail
npx remotion render src/index.ts Day1 dist/day1-remotion.mp4 --codec=h264 --crf=18
blender -b blender/luxor9_signal.blend -P blender/blender_scene.py -a
ffmpeg -y -i dist/day1-remotion.mp4 -vf "scale=1080:1920:flags=lanczos" -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart dist/Luxor9_Day1_Master.mp4

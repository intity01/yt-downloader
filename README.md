# Media Downloader Web Application

A streamlined web interface for downloading audio and video content from various platforms, built using Streamlit and yt-dlp.

## Overview

This application provides a user-friendly frontend for media extraction, allowing users to convert and download content efficiently. It handles format conversion via FFmpeg and offers real-time processing feedback.

## Key Features

- **Multi-Platform Support:** Compatible with YouTube, TikTok, Facebook, Twitter (X), and other major media sites.
- **Format Flexibility:** Supports MP3 (Audio) and MP4 (Video) extraction.
- **Quality Control:** Options to select specific audio bitrates and video resolutions.
- **Real-Time Monitoring:** Visual progress bar for download and conversion status.
- **Session History:** Tracks download history within the current active session.

## Installation & Usage

### Prerequisites
- Python 3.8+
- FFmpeg (Required for media conversion and stream merging)

### Local Setup

1. Navigate to the project directory:
   ```bash
   cd web_app

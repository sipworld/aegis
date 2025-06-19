# CryptoVoIP Aegis Dashboard

A lightweight web application for managing and viewing stream recordings and live streams on the same server as CryptoVoIP's Ant Media instance.

## Features
- **Login Page**: Access control with a predefined username/password.
- **Recordings Tab**: Lists stream recordings grouped by stream name and organized by date.
- **Live Streams Tab**: Shows active live streams with ability to play selected streams.

## Assumptions
- Recordings are located at: `/usr/local/antmedia/webapps/LiveApp/streams/<streamName>/`
- Each stream's recording files are named with a timestamp (e.g., `streamName_2024-06-18_14-30.mp4`).
- The app reads from two JSON endpoints:
  - `recordings.json` for the list of recordings
  - `live.json` for current live streams

## To Do
1. Generate backend Python or Node.js scripts:
   - `recordings.json`: Scan recordings directory and return data.
   - `live.json`: Fetch live stream names (from log files or Ant Media REST API).
2. Deploy this dashboard on the same Ubuntu server as Ant Media.
3. Configure Nginx or Apache to reverse proxy to this dashboard.

## Frontend Structure (React or Simple HTML/JS)
- `LoginPage` → sets sessionStorage `loggedIn=true`
- `Dashboard`
  - Tabs: `Recordings`, `Live Streams`
  - `Recordings`: Load `recordings.json`, display per stream
  - `Live Streams`: Load `live.json`, show players

# M3U Editor Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/C0NN0RAD0/m3u-ha?style=for-the-badge)](https://github.com/C0NN0RAD0/m3u-ha/releases)
[![GitHub License](https://img.shields.io/github/license/C0NN0RAD0/m3u-ha?style=for-the-badge)](https://github.com/C0NN0RAD0/m3u-ha/blob/main/LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/C0NN0RAD0/m3u-ha?style=for-the-badge)](https://github.com/C0NN0RAD0/m3u-ha/issues)

**M3U Editor integration for Home Assistant** - Connect to your [M3U Editor](https://github.com/sparkison/m3u-editor) instance and monitor/control your IPTV playlists, EPGs, and channels.

## Features

- **📊 Sensors**: Monitor playlist and EPG statistics (channel count, programme count, last sync time)
- **🔄 Switches**: Enable/disable auto-sync for playlists
- **🔘 Buttons**: Manually trigger playlist and EPG sync operations
- **🎵 Media Players**: Control playlist playback (basic integration)
- **🛠️ Services**: Call services to sync playlists, EPGs, or refresh all data

## Installation

### HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed
2. Go to **HACS > Integrations**
3. Click **➕ Explore & Download Repositories**
4. Search for **"M3U Editor"**
5. Click **Download**
6. Restart Home Assistant
7. Go to **Settings > Devices & Services > Add Integration** and select **M3U Editor**

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/C0NN0RAD0/m3u-ha/releases)
2. Copy the `m3u_editor` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Go to **Settings > Devices & Services > Add Integration** and select **M3U Editor**

## Configuration

When adding the integration, you'll need to provide:

- **Host**: The hostname or IP address of your M3U Editor instance
- **Port**: The port number (default: 36400)
- **Protocol**: http or https
- **Authentication**: You can use either:
  - Username and Password (for Dispatcharr-compatible authentication)
  - API Key (if your M3U Editor instance supports it)
- **SSL Options**: Enable SSL and optionally disable certificate verification for self-signed certificates

## Entities

### Sensors

- **Playlist Sensors**: Show the number of channels in each playlist
- **EPG Sensors**: Show the number of programmes in each EPG
- **System Sensor**: Shows system information from M3U Editor

### Switches

- **Auto Sync Switches**: Enable/disable automatic synchronization for each playlist

### Buttons

- **Sync Buttons**: Manually trigger synchronization for playlists and EPGs

### Media Players

- **Playlist Media Players**: Basic media player integration for playlists

## Services

### `m3u_editor.sync_playlist`

Sync a specific playlist by UUID.

**Parameters:**
- `uuid` (required): The UUID of the playlist to sync

**Example:**
```yaml
automation:
  - alias: "Sync Playlist Daily"
    trigger:
      - platform: time
        at: "03:00:00"
    action:
      - service: m3u_editor.sync_playlist
        data:
          uuid: "your-playlist-uuid"
```

### `m3u_editor.sync_epg`

Sync a specific EPG by UUID.

**Parameters:**
- `uuid` (required): The UUID of the EPG to sync

### `m3u_editor.refresh_data`

Refresh all data from the M3U Editor API.

**Example:**
```yaml
automation:
  - alias: "Refresh M3U Editor Data"
    trigger:
      - platform: time
        at: "02:00:00"
    action:
      - service: m3u_editor.refresh_data
```

## API Endpoints Used

This integration uses the following M3U Editor API endpoints:

- `GET /api/system/info` - System information
- `GET /api/user/playlists` - List all playlists
- `GET /api/user/epgs` - List all EPGs
- `GET /api/channel/get` - List all channels
- `GET /api/playlist/{uuid}/stats` - Playlist statistics
- `GET /api/playlist/{uuid}/sync` - Sync a playlist
- `GET /api/epg/{uuid}/sync` - Sync an EPG
- `POST /api/accounts/token` - Authenticate with username/password
- `POST /api/accounts/token/refresh` - Refresh authentication token

## Troubleshooting

### Connection Issues

- Ensure your M3U Editor instance is running and accessible from Home Assistant
- Check that the host, port, and protocol are correct
- Verify that your firewall allows connections between Home Assistant and M3U Editor

### Authentication Issues

- Make sure your username and password are correct
- If using API key authentication, ensure the key is valid
- For SSL connections, try disabling SSL verification if you're using self-signed certificates

### Data Not Updating

- Check the logs for errors: **Settings > System > Logs**
- Try manually refreshing the data using the `m3u_editor.refresh_data` service
- Ensure your M3U Editor instance has the API enabled

## Development

To contribute to this integration:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This integration is licensed under the MIT License. See the LICENSE file for details.

## Support

- [GitHub Issues](https://github.com/C0NN0RAD0/m3u-ha/issues) - Report bugs and request features
- [Discord](https://discord.gg/rS3abJ5dz7) - Join the M3U Editor Discord for support

## Credits

- [M3U Editor](https://github.com/sparkison/m3u-editor) - The amazing IPTV editor this integration connects to
- [Home Assistant](https://www.home-assistant.io/) - The open-source home automation platform

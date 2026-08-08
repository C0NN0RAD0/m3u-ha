# M3U Editor Home Assistant Integration

This integration connects Home Assistant to the [M3U Editor](https://github.com/sparkison/m3u-editor) API, allowing you to monitor and control your IPTV playlists, EPGs, and channels directly from Home Assistant.

## Features

- **Sensors**: Monitor playlist and EPG statistics (channel count, programme count, last sync time)
- **Switches**: Enable/disable auto-sync for playlists
- **Buttons**: Manually trigger playlist and EPG sync operations
- **Media Players**: Control playlist playback (basic integration)
- **Services**: Call services to sync playlists, EPGs, or refresh all data

## Installation

### Manual Installation

1. Copy the `m3u_editor` folder from `custom_components` to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to **Settings > Devices & Services > Add Integration** and select **M3U Editor**

### HACS Installation (Future)

This integration will be available through HACS once it's published.

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

- **Playlist Media Players**: Basic media player integration for playlists (playback functionality depends on your setup)

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

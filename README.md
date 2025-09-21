# Resy Search

A Python script to search for restaurants on Resy that require deposits for reservations.

## Features

- 🔍 **Multi-page Search**: Searches through multiple pages of Resy results (configurable)
- 💰 **Deposit Filtering**: Finds only venues that require deposits for reservations
- 🌍 **Geographic Search**: Configurable location-based search with radius
- 📊 **Multiple Output Formats**: Results exported to both JSON and text files
- ⚙️ **TOML Configuration**: All settings externalized to configuration file
- 🔒 **Secure**: Authentication tokens kept in gitignored config file
- ⏱️ **Rate Limited**: Built-in delays between API requests to be respectful

## Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install httpx toml
   ```
   Or if using uv:
   ```bash
   uv sync
   ```

## Configuration

1. **Copy the example configuration**:
   ```bash
   cp config.example.toml config.toml
   ```

2. **Edit `config.toml`** with your settings:

### Authentication
Get these values from your browser's developer tools when logged into Resy:
- `auth_token`: Your x-resy-auth-token
- `universal_token`: Your x-resy-universal-auth token
- `api_key`: ResyAPI key (usually `VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5`)

### Search Parameters
```toml
[search]
day = "2025-10-11"          # Date in YYYY-MM-DD format
party_size = 2              # Number of people in your party
total_pages = 20            # Maximum number of pages to search
```

### Geographic Area
```toml
[geo]
latitude = 37.7577          # Latitude of search center
longitude = -122.4376       # Longitude of search center  
radius = 32200              # Search radius in meters
```

**Popular City Coordinates:**
- **San Francisco**: `37.7577, -122.4376`
- **New York**: `40.712941, -74.006393`
- **Los Angeles**: `34.052235, -118.243683`
- **Chicago**: `41.878113, -87.629799`

## Usage

Run the script:
```bash
python main.py
```

The script will:
1. Search through the specified number of pages
2. Filter venues that require deposits
3. Display results in the console
4. Export results to the `results/` folder:
   - `venues_with_deposits.json` - Complete venue data
   - `venues_with_deposits.txt` - Human-readable summary

## Output

### Console Output
```
Searching page 1...
Searching page 2...
...
Search completed!
Total venues found across all pages: 156
Venues WITH deposits: 23

Venues WITH deposits:
============================================================

Name: ITO NYC
Neighborhood: Tribeca
Cuisine: Japanese
Rating: 4.89 (1360 reviews)
Deposit Required: $295
----------------------------------------
```

### File Exports
- **JSON**: Complete venue data for further processing
- **Text**: Formatted summary with venue details and deposit amounts

## Project Structure

```
├── main.py                 # Main script
├── config.toml            # Your configuration (gitignored)
├── config.example.toml    # Configuration template
├── results/               # Output folder (gitignored)
│   ├── venues_with_deposits.json
│   └── venues_with_deposits.txt
├── pyproject.toml         # Dependencies
└── README.md             # This file
```

## How It Works

1. **Configuration Loading**: Reads settings from `config.toml`
2. **API Requests**: Makes paginated requests to Resy's venue search API
3. **Deposit Detection**: Analyzes venue availability templates for deposit requirements
4. **Rate Limiting**: Waits 5 seconds between requests to avoid overwhelming the API
5. **Data Export**: Saves filtered results in multiple formats

## Getting Authentication Tokens

1. **Open Resy** in your browser and log in
2. **Open Developer Tools** (F12 or right-click → Inspect)
3. **Go to Network tab**
4. **Search for restaurants** on Resy
5. **Find the API request** to `venuesearch/search`
6. **Copy the headers**:
   - `x-resy-auth-token`
   - `x-resy-universal-auth`

## Customization

### Search Different Cities
Update the `[geo]` section in `config.toml` with coordinates for your desired city.

### Change Search Criteria
- Modify `day` for different dates
- Adjust `party_size` for different group sizes
- Change `total_pages` to search more or fewer results

### Output Customization
Update the `[output]` section to change folder names or file names.

## Rate Limiting

The script includes a 5-second delay between API requests to be respectful to Resy's servers. This means searching 20 pages will take approximately 1 minute and 35 seconds.

## Security

- `config.toml` is gitignored to protect your authentication tokens
- Use `config.example.toml` as a template for sharing or version control
- Never commit real authentication tokens to version control

## Troubleshooting

### Configuration File Not Found
```
Configuration file config.toml not found!
```
**Solution**: Copy `config.example.toml` to `config.toml` and fill in your values.

### Authentication Errors
**Solution**: Update your tokens in `config.toml` - they may have expired.

### No Results Found
- Check if your search date has available restaurants
- Verify your geographic coordinates are correct
- Try increasing the search radius

## License

This project is for educational and personal use only. Please respect Resy's terms of service and API usage guidelines.

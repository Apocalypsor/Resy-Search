import json
import os
import time

import httpx
import toml


def load_config(config_path="config.toml"):
    """Load configuration from TOML file."""
    try:
        with open(config_path, "r") as f:
            config = toml.load(f)
        return config
    except FileNotFoundError:
        print(f"Configuration file {config_path} not found!")
        raise
    except Exception as e:
        print(f"Error loading configuration: {e}")
        raise


def extract_venue_info(venue):
    """Extract and format venue information from venue data."""
    name = venue.get("name", "Unknown")
    neighborhood = venue.get("neighborhood", "Unknown")
    cuisine = ", ".join(venue.get("cuisine", []))
    rating = venue.get("rating", {})
    avg_rating = rating.get("average", 0)
    rating_count = rating.get("count", 0)
    deposit_amount = venue.get("deposit_amount", "Unknown")

    return {
        "name": name,
        "neighborhood": neighborhood,
        "cuisine": cuisine,
        "avg_rating": avg_rating,
        "rating_count": rating_count,
        "deposit_amount": deposit_amount,
    }


def search_resy_page(
    auth_token, universal_token, api_key, day, party_size, geo, page=1
):
    """
    Search a single page of Resy venues with the given parameters.

    Args:
        auth_token (str): The x-resy-auth-token value
        universal_token (str): The x-resy-universal-auth value
        api_key (str): The ResyAPI api_key value
        day (str): Date in format "YYYY-MM-DD"
        party_size (int): Number of people in the party
        geo (dict): Dictionary with latitude, longitude, and radius
        page (int): Page number to search (default: 1)

    Returns:
        dict: API response containing search results
    """
    url = "https://api.resy.com/3/venuesearch/search"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "authorization": f'ResyAPI api_key="{api_key}"',
        "cache-control": "no-cache",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://resy.com",
        "priority": "u=1, i",
        "referer": "https://resy.com/",
        "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36",
        "x-origin": "https://resy.com",
        "x-resy-auth-token": auth_token,
        "x-resy-universal-auth": universal_token,
    }

    data = {
        "availability": True,
        "page": page,
        "per_page": 20,
        "slot_filter": {"day": day, "party_size": party_size},
        "types": ["venue"],
        "order_by": "availability",
        "geo": geo,
    }

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()


def search_resy_venues():
    """
    Search for venues on Resy and show only those WITH deposits across pages 1-20.
    """
    # Load configuration
    config = load_config()

    # Extract configuration values
    auth_token = config["auth"]["auth_token"]
    universal_token = config["auth"]["universal_token"]
    api_key = config["auth"]["api_key"]
    day = config["search"]["day"]
    party_size = config["search"]["party_size"]
    total_pages = config["search"]["total_pages"]
    geo = {
        "latitude": config["geo"]["latitude"],
        "longitude": config["geo"]["longitude"],
        "radius": config["geo"]["radius"],
    }
    results_folder = config["output"]["results_folder"]
    json_filename = config["output"]["json_filename"]
    txt_filename = config["output"]["txt_filename"]

    # Ensure results folder exists
    os.makedirs(results_folder, exist_ok=True)

    all_venues_with_deposits = []
    total_venues_found = 0

    try:
        # Search through pages 1 to total_pages
        for page in range(1, total_pages + 1):
            print(f"Searching page {page}...")

            # Use the extracted search function
            result = search_resy_page(
                auth_token, universal_token, api_key, day, party_size, geo, page
            )

            # Get the search hits
            hits = result.get("search", {}).get("hits", [])
            total_venues_found += len(hits)

            # If no hits, we've reached the end
            if not hits:
                print(f"No more results found at page {page}")
                break

            # Filter for venues WITH deposits
            for venue in hits:
                has_deposit = False
                deposit_amount = None

                # Check availability templates for deposit fees
                availability = venue.get("availability", {})
                templates = availability.get("templates", {})

                for template_id, template in templates.items():
                    deposit_fee = template.get("deposit_fee")
                    if deposit_fee is not None:
                        has_deposit = True
                        deposit_amount = deposit_fee
                        break

                # Only include venues WITH deposits
                if has_deposit:
                    venue["deposit_amount"] = deposit_amount
                    all_venues_with_deposits.append(venue)

            # Sleep for 5 seconds between requests (except for the last page)
            if page < total_pages:
                print(f"Waiting 5 seconds before next request...")
                time.sleep(5)

        print(f"\nSearch completed!")
        print(f"Total venues found across all pages: {total_venues_found}")
        print(f"Venues WITH deposits: {len(all_venues_with_deposits)}")
        print("\nVenues WITH deposits:")
        print("=" * 60)

        for venue in all_venues_with_deposits:
            info = extract_venue_info(venue)

            print(f"\nName: {info['name']}")
            print(f"Neighborhood: {info['neighborhood']}")
            print(f"Cuisine: {info['cuisine']}")
            print(f"Rating: {info['avg_rating']:.2f} ({info['rating_count']} reviews)")
            print(f"Deposit Required: ${info['deposit_amount']}")
            print("-" * 40)

        # Export to JSON file
        json_path = os.path.join(results_folder, json_filename)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_venues_with_deposits, f, indent=2, ensure_ascii=False)
        print(f"\nResults exported to {json_path}")

        # Export to text file
        txt_path = os.path.join(results_folder, txt_filename)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"Search Results: Venues WITH Deposits\n")
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total venues found across all pages: {total_venues_found}\n")
            f.write(f"Venues WITH deposits: {len(all_venues_with_deposits)}\n")
            f.write("=" * 60 + "\n\n")

            for i, venue in enumerate(all_venues_with_deposits, 1):
                info = extract_venue_info(venue)

                f.write(f"{i}. {info['name']}\n")
                f.write(f"   Neighborhood: {info['neighborhood']}\n")
                f.write(f"   Cuisine: {info['cuisine']}\n")
                f.write(
                    f"   Rating: {info['avg_rating']:.2f} ({info['rating_count']} reviews)\n"
                )
                f.write(f"   Deposit Required: ${info['deposit_amount']}\n")
                f.write("-" * 40 + "\n\n")

        print(f"Results exported to {txt_path}")

        return all_venues_with_deposits

    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


if __name__ == "__main__":
    venues = search_resy_venues()

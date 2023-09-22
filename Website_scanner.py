 import requests
import logging
import time
from concurrent.futures import ThreadPoolExecutor

# Initialize logging to capture important events and errors
logging.basicConfig(level=logging.INFO)

# Shared variables to track performance and results
total_checked = 0  # Count of URLs checked
total_found = 0    # Count of URLs found (non-404)
found_urls = []    # List to store found URLs

# Configuration settings
wordlist = "/usr/share/wordlists/dirb/common.txt"  # Wordlist for directories and files
file_extensions = [".txt", ".php", ".html"]  # Common file extensions to check
url = "http://localhost/"  # Base URL to scan
threads = 10  # Number of threads for concurrent scanning

# Calculate the total number of URLs to scan
with open(wordlist) as f:
    total_lines = len(f.readlines())
total_urls = total_lines * (1 + len(file_extensions))  # Total for directories and files

# Function to check a single URL
def check_url(path):
    global total_checked, total_found, found_urls
    try:
        r = requests.get(url + path)  # Send HTTP GET request
        total_checked += 1  # Increment count of URLs checked
        if r.status_code != 404:  # Check if URL exists (status code other than 404)
            total_found += 1  # Increment count of URLs found
            found_urls.append(url + path)  # Add the found URL to the list
            logging.info(f'Found at {url + path}')
    except Exception as e:
        logging.error(f"Error checking {url + path}: {e}")

# Function to print performance information in real-time
def print_performance():
    global total_checked, total_found, total_urls
    while total_checked < total_urls:  # Loop until all URLs are checked
        remaining = total_urls - total_checked  # Calculate remaining URLs
        percentage_completed = (total_checked / total_urls) * 100  # Calculate percentage completed
        print(f"Total URLs Checked: {total_checked}, Total Found: {total_found}, Remaining: {remaining}, Percentage Completed: {percentage_completed:.2f}%")
        time.sleep(5)  # Pause for 5 seconds before next update

# Function to perform multithreaded scanning
def multithreaded_scan(wordlist, extensions=None):
    with ThreadPoolExecutor(max_workers=threads) as executor:
        with open(wordlist) as f:
            for item in f.readlines():  # Loop through each line in the wordlist
                item = item.strip()
                if extensions:
                    for ext in extensions:  # Loop through file extensions if provided
                        executor.submit(check_url, item + ext)  # Submit URL for checking
                else:
                    executor.submit(check_url, item)  # Submit URL for checking

# Start real-time performance printing in a separate thread
from threading import Thread
performance_thread = Thread(target=print_performance)
performance_thread.daemon = True  # Make thread daemon so it exits when main program exits
performance_thread.start()

# Start the scanning process
multithreaded_scan(wordlist)  # Scan for directories
multithreaded_scan(wordlist, file_extensions)  # Scan for files

# Wait for all threads to complete
performance_thread.join()

# Print found URLs after scanning is complete
print("\nFound URLs:")
for url in found_urls:
    print(url)

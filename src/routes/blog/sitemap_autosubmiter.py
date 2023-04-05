import requests

# Set your Search Console API credentials
access_token = 'YOUR_ACCESS_TOKEN'
site_url = 'https://www.example.com/'

# Set the URL of your sitemap.xml file
sitemap_url = 'https://www.example.com/sitemap.xml'

# Define the API endpoint for submitting sitemaps
api_endpoint = f'https://www.googleapis.com/webmasters/v3/sites/{site_url}/sitemaps/'

# Define the request headers
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Define the request body with the sitemap URL
data = {
    'action': 'add',
    'content': [
        {
            'type': 'SITEMAP',
            'source': sitemap_url
        }
    ]
}

# Send the POST request to submit the sitemap
response = requests.post(api_endpoint, headers=headers, json=data)

# Check the response status code
if response.status_code == 200:
    print('Sitemap submitted successfully.')
else:
    print('Error submitting sitemap:', response.text)

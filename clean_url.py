from urllib.parse import urlparse, parse_qs, unquote

linkedin_redirect = "https://www.linkedin.com/redir/redirect?url=https%3A%2F%2Fwww%2Esophos%2Ecom%2Fen-us&urlhash=JG5B&trk=about_website"

# Parse the query string
parsed_url = urlparse(linkedin_redirect)
query_params = parse_qs(parsed_url.query)

# Extract and decode the 'url' parameter
clean_url = unquote(query_params.get('url', [''])[0])

print(clean_url)

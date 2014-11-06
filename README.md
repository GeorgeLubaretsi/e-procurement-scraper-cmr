# e-procurement-scraper-cmr

A scraper for simplified, direct tenders. The site requires a valid login to access these data.

## Execution

	cd e-procurement-scraper-cmr
	scrapy crawl CMRSpider -o out_folder/out_file.json

## Requirements

The scraper requires a valid login to function.
The login and password should be in a file

	$HOME/.crmcreds

The file format:

	[cmr]
	username = 
	password = 



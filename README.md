# e-procurement-scraper-cmr

A scraper for simplified, direct procurements. 

### Execution

	cd e-procurement-scraper-cmr
	scrapy crawl CMRSpider -o out_folder/out_file.json -a attachments=folder_name -a mode=scrape_mode
	
	[Defaults: attachments = None (not downloading attachments, scrape_mode = FULL]

### Requirements

The scraper requires a valid login to function.
The login and password should be in a file

	$HOME/.cmrcreds

The file format:

	[cmr]
	username = 
	password = 

### TO DO


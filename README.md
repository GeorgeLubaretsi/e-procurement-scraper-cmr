# e-procurement-scraper-cmr
## Current Version: 1.0.xx

***

A scraper for simplified, direct procurements. 

### Execution

	cd e-procurement-scraper-cmr
	scrapy crawl CMRSpider -o out_folder/out_file.json -a attachments=folder_name -a mode=scrape_mode
	
	[Defaults: attachments = None (not downloading attachments), scrape_mode = FULL]

### Requirements

The scraper requires a valid login to function.
The login and password should be in a file

	$HOME/.cmrcreds

The file format:

	[cmr]
	username = 
	password = 

### TO DO

* Verify why after session time-out the scraper has problems logging back in.
* Implement re-scrape for a list of indicated procurements for which the data should be refreshed


### License

E-procurement CMR scraper is released under the terms of [GNU General Public License (V2)](http://www.gnu.org/licenses/gpl-2.0.html).

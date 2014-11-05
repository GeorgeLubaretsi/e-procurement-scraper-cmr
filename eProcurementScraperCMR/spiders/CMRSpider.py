# -*- coding: utf-8 -*-

from scrapy.http.request.form import FormRequest
from CMRCredentials import CMRCredentials
from scrapy.spider import Spider
from time import time
from scrapy import Request
import re


class CMRSpider(Spider):
    name = 'CMRSpider'
    
    allowed_domains = ['tenders.procurement.gov.ge']
    
    # logging in
    login_url = 'https://tenders.procurement.gov.ge/login.php?lang=en'

    # one of the links below points to the site with CMR listing
    
    # this gives the menu on the left-hand side of the page
    #start_urls = ['https://tenders.procurement.gov.ge/engine/controller.php?action=ssp&org_id=0&_=1415169723815']
    # last 5 changes in tender status
    #start_urls = ['https://tenders.procurement.gov.ge/engine/controller.php?action=lastevents&_=1415176297611']
    
    # CORRECT listing of simplified direct tenders
    #start_urls = ['https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=ssp_list&search=start&ssp_page=1&_=1415176557559']
    
    start_urls = ['https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=ssp_list&search=start&ssp_page=1&_=%d' % int( time() * 1000)]
    

    '''
    within the page details are shown calling ShowSSP(id) function, the number is used in the calls below for detailed view ssp_id=id
    the _= parameter is not sure for now, looks like a proxy timestamp: int( time.time() * 1000), this for jquery/php combo serves as a request 
    to provide non-cached data, I can probably generate it
    ''' 

    '''
    an actual link to a detailed tender information, need to figure out where to take the sources from
    https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=view&ssp_id=707942&_=1415177825531
    https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=view&ssp_id=708013&_=1415181166565
    '''
    
    # start_urls = ['https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=view&ssp_id=708013&_=%d']
    
    def __init__(self):
        super( CMRSpider, self).__init__()
        self.base_url_list = 'https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=ssp_list&search=start&ssp_page=1&_=%d'
        
        self.page_numbers_regex = re.compile( r'page: (\d+)/(\d+)')
        self.tender_id_regex = re.compile( r'ShowSSP\((\d+)\)')

    # before any crawling we need to log in to the site
    def start_requests(self):
        # CMR data is only available to logged in users
        siteCreds = CMRCredentials().load_credentials()
        loginResponse = FormRequest( self.login_url,
                                     formdata = {'user' : siteCreds['username'], 
                                                 'pass' : siteCreds['password']},
                                     callback = self.verify_login)

        # scrapy needs a list of responses here to iterate
        return [loginResponse]
        
    # checking whether we have succeeded logging in        
    def verify_login(self, response):
        # need to think about a more reliable check
        if not 'Exit' in response.body:
            raise Exception( "Couldn't log in to the site")
        if "Sign in" in response.body:
            raise Exception( "Couldn't log in to the site")
        
        return self.make_requests_from_url( self.start_urls[0])

    # mandatory, we're already logged in and can start extracting data
    def parse(self, response):
        
        '''
        so I need to read the list and yield a request for each ssp_id I find in the list
        finally, I need to yield a request for the next page
        '''
        
        '''
        the request for the next page of listing
        
        what's missing now is figuring out that we are processing a listing, not a single tender, or we'll be over our heads with repeated listings
        we check if we have button ssp_btn_next and check if it's enabled (aria-disabled attribute), if not it's the last page 
        '''
        pageNumbers = self.page_numbers_regex.findall( response.body)
        
        # check if we're on a listing page
        if len( pageNumbers) > 0: 
            
            # counting pages so we stop when last page has been processed    
            if int( pageNumbers[0][0]) <  int( pageNumbers[0][1]): # this is the case on listings
                nextPageUrl = self.base_url_list.replace( 'search=start&ssp_page=1', 'ssp_page=next') % int( time() * 1000)
                yield Request( nextPageUrl, callback = self.parse)
            
            ''' 
            since we're on a listing page we need to find all the tender id's and yield related requests so tenders can be collected
            '''
            tenderIDList = self.tender_id_regex.findall( response.body)
            # we trigger map instead of looping here
        
    
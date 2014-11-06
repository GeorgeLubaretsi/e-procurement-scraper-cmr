# -*- coding: utf-8 -*-

from scrapy.http.request.form import FormRequest
from CMRCredentials import CMRCredentials
from scrapy.spider import Spider
from scrapy import Request
import re, time
from eProcurementScraperCMR.items import Procurement


class CMRSpider( Spider):
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
    
    start_urls = ['https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=ssp_list&search=start&ssp_page=1&_=%d' % int( time.time() * 1000)]
    

    '''
    within the page details are shown calling ShowSSP(id) function, the number is used in the calls below for detailed view ssp_id=id
    the _= parameter is not sure for now, looks like a proxy timestamp: int( time.time() * 1000), this for jquery/php combo serves as a request 
    to provide non-cached data, I can probably generate it

    an actual link to a detailed tender information, need to figure out where to take the sources from
    https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=view&ssp_id=707942&_=1415177825531
    https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=view&ssp_id=708013&_=1415181166565
    '''
    # note %s and %d near the end of the string, these are later replaced with actual values
    tender_url = 'https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=view&ssp_id=%s&_=%d'
    
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
    def parse( self, response):
        
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
        
        '''
        check if we are on a listing, if yes, we generate (or not) a request for the next page
        and generate requests for the listed tenders
        
        tender details are handled directly by their callback function, this one is then skipped
        '''
        
        if len( pageNumbers) == 0: 
            return
        
        # counting pages so we stop creating new calls when we're on the last page
        if int( pageNumbers[0][0]) <  int( pageNumbers[0][1]): 
            # TEMP comment out to limit to a single tender for development
            #yield None
            nextPageUrl = self.base_url_list.replace( 'search=start&ssp_page=1', 'ssp_page=next') % int( time.time() * 1000)
            yield Request( nextPageUrl, callback = self.parse)
        
        ''' 
        since we're on a listing page we need to find all the tender id's and yield related requests so tenders can be collected
        '''
        tenderIDList = self.tender_id_regex.findall( response.body)
        
        # TEMP, limit to one tender for development
        #for tenderID in tenderIDList[0:1]:
        for tenderID in tenderIDList:
            tenderUrl = self.tender_url % ( tenderID, int( time.time() * 1000))
            # print tenderUrl
            
            yield Request( tenderUrl, callback = self._process_tender)
            # I have to do that in order not to send the same timestamp with many requests
            time.sleep( 0.002)
           
        
    def _process_tender( self, response):
        ''' Tender parser, yields a Procurement item '''
        iProcurement = Procurement()
        
        siteBody = response.body.replace('\n', '').replace( '\r', '').replace('`', '')
        
        # Procurement status
        iProcurement['pStatus'] =  re.findall( r'Status:.*?\>(.*?)\<', siteBody)[0]
        
        # Procuring Entities
        iProcurement['pProcuringEntities'] = re.findall( r'Procuring\s+entities.*?\<td\>(.*?)\s*(\#\d+)*\s*\((\d+)\)\<br\>.*?\<strong\>(.*?)\<', siteBody)[0]
        
        # Supplier
        iProcurement['pSupplier'] = re.findall( r'Supplier.*?\<td\>(.*?)\s*(\#\d+)*\s*\((\d+)\)\<br\>.*?\<strong\>(.*?)\<', siteBody)[0]
        
        # Amounts
        dAmounts = re.findall( r'Amounts.*?contract\s+value.*?\>(\d{2}\.\d{2}\.\d{4})\<.*?(\d+\.*\d+\s*GEL).*?actually\s+paid\s+amount.*?\>(\d{2}\.\d{2}\.\d{4})\<.*?(\d+\.*\d+\s*GEL)', siteBody)[0]
        iProcurement['pValueDate'] = dAmounts[0]
        iProcurement['pValueContract'] = dAmounts[1]
        iProcurement['pAmountPaidDate'] = dAmounts[2]
        iProcurement['pAmountPaid'] = dAmounts[3]

        # Financing source
        iProcurement['pFinancingSource'] = re.findall( r'Financing\s+source.*?\<td\>(.*?)\s*\<br\>.*?\<strong\>(.*?)\<', siteBody)[0]
        
        # Procurement Base
        iProcurement['pProcurementBase'] = re.findall( r'Procurement\s+Base.*?\<td\>[&quot;]?(.*?)[&quot;]?\s*\<', siteBody)[0]
        
        # Document
        iProcurement['pDocument'] = re.findall( r'Document.*?\<td.*?\>(.*?)\s*\<br.*?\>(#\s*.*?)\<br.*?(\d{2}\.\d{2}\.\d{4}).*?(\d{2}\.\d{2}\.\d{4}).*?(\d{2}\.\d{2}\.\d{4})\<', siteBody)[0]
        
        # Attachments (A single one for now?)
        #     Problem for now with unicode characters in file names 
        iProcurement['pAttachments'] = re.findall( r'Attached\s+Files.*?href.*?"(.*?)".*?\<i\>(.*?)\<.*?(\d{2}\.\d{2}\.\d{4}\s+\d{2}\:\d{2})\<', siteBody)[0]
        
        # Contract Type
        iProcurement['pContractType'] = re.findall( r'Contract\s+type.*?\<div.*?\>(.*?)\<', siteBody)[0]
        
        # Agreement Amount
        iProcurement['pAgreementAmount'] = re.findall( r'Agreement\s+Amount.*?\<div.*?\>(\d+\.*\d* GEL)\<', siteBody)[0]
        
        # Agreement Done
        iProcurement['pAgreementDone'] = re.findall( r'Agreement\s+Done.*?\<div.*?\>(.*?)\<', siteBody)[0]
        
        # CPV Codes (main)
        allCodes = re.findall(  r'CPV\s+Codes\s+\(main\)\<\/div\>(.*?\<\/div\>)&nbsp;', siteBody)[0]
        iProcurement['pCPVCodesMain'] = re.findall( r'(\d+\s+.*?)\<\/div', allCodes)
        
        # CPV Codes( detailed)
        allCodes = re.findall(  r'CPV\s+Codes\s+\(detailed\)\<\/div\>(.*?\<\/div\>)&nbsp;', siteBody)[0]
        iProcurement['pCPVCodesDetailed'] = re.findall( r'(\d+\s+.*?)\<\/div', allCodes)

        
        # TEMP
        print iProcurement
        print
        
  
        
        
        
        
        
        
        
    
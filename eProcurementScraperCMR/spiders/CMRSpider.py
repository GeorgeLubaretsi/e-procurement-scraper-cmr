# -*- coding: utf-8 -*-

from scrapy.http.request.form import FormRequest
from CMRCredentials import CMRCredentials
from scrapy.spider import Spider
from scrapy import Request
import re, time, os, urllib
from eProcurementScraperCMR.items import Procurement


class CMRSpider( Spider):
    name = 'CMRSpider'
    
    allowed_domains = ['tenders.procurement.gov.ge']
    
    # logging in
    login_url = 'https://tenders.procurement.gov.ge/login.php?lang=en'

    # this gives the menu on the left-hand side of the page
    #start_urls = ['https://tenders.procurement.gov.ge/engine/controller.php?action=ssp&org_id=0&_=1415169723815']
    # last 5 changes in tender status
    #start_urls = ['https://tenders.procurement.gov.ge/engine/controller.php?action=lastevents&_=1415176297611']
    
    # CORRECT listing of simplified direct tenders
    #start_urls = ['https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=ssp_list&search=start&ssp_page=1&_=1415176557559']
    
    start_urls = ['https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=ssp_list&search=start&ssp_page=1&_=%d' % int( time.time() * 1000)]
    
    '''
    within the page details are shown calling ShowSSP(id) function, the number is used in the calls below for detailed view ssp_id=id
    the _= parameter is a proxy timestamp: int( time.time() * 1000), for jquery/php combo, serves as a request 
    to provide non-cached data, I can probably generate it

    an actual link to a detailed tender information
    https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=view&ssp_id=707942&_=1415177825531
    https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=view&ssp_id=708013&_=1415181166565
    '''
    # note %s and %d near the end of the string, these are later replaced with actual values
    tender_url = 'https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=view&ssp_id=%s&_=%d'
        
    def __init__(self, attachments_folder = None, *args, **kwargs):
        super( CMRSpider, self).__init__( *args, **kwargs)
        self.base_url_list = 'https://tenders.procurement.gov.ge/engine/ssp/ssp_controller.php?action=ssp_list&search=start&ssp_page=1&_=%d'
        
        self.page_numbers_regex = re.compile( ur'page: (\d+)/(\d+)')
        self.tender_id_regex = re.compile( ur'ShowSSP\((\d+)\)')
        
        self.attachments_folder = attachments_folder
     
       
        # setting up attachment saving
        if self.attachments_folder is None:
            return 
        
        # create folder if does not exist
        try:
            os.stat( self.attachments_folder)
        except OSError:
            os.mkdir( self.attachments_folder)
        




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
        I need to read the list and yield a request for each ssp_id I find in the list
        finally, I need to yield a request for the next page
        '''
        
        pageNumbers = self.page_numbers_regex.findall( response.body)
        
        '''
        check if we are on a listing, if yes, we generate (or not) a request for the next page
        and generate requests for the listed tenders
        
        tender details are handled directly by their callback
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
           
    # saving the attachments
    def _save_attachment(self, response, out_filename):
        
        if self.attachments_folder is None:
            return 
        
        # filename is the last component of the url    
        out_filename = self.attachments_folder + '/' + out_filename 
        
        out_file = open( out_filename, 'wb')
        out_file.write( response.body)
        out_file.close()
        
    def _process_tender( self, response):
        
        # later on these regex's should be compiled before the download
        
        #f = open( 'tender.html', 'wb')
        #f.write( response.body)
        #f.close()
        
        try:
            # Tender parser, yields a Procurement item
            iProcurement = Procurement()

            siteBody = response.body.replace('\n', '').replace( '\r', '').replace('`', '')
            
            # Procurement status
            iProcurement['pStatus'] =  re.findall( ur'Status:.*?\>(.*?)\<', siteBody, re.UNICODE)[0]
            
            # Procuring Entities
            iProcurement['pProcuringEntities'] = re.findall( ur'Procuring\s+entities.*?\<td\>(.*?)\s*(\#\d+)*\s*\((\d+)\)\<br\>.*?\<strong\>(.*?)\<', siteBody, re.UNICODE)[0]
            
            # Supplier
            iProcurement['pSupplier'] = re.findall( ur'Supplier.*?\<td\>(.*?)\s*(\#\d+)*\s*\((\d+)\)\<br\>.*?\<strong\>(.*?)\<', siteBody, re.UNICODE)[0]
            
            # Amounts
            dAmounts = re.findall( ur'Amounts.*?contract\s+value.*?\>(\d{2}\.\d{2}\.\d{4})\<.*?(\d+\.*\d+\s*\w+)\<.*?actually\s+paid\s+amount.*?\>(\d{2}\.\d{2}\.\d{4})\<.*?(\d+\.*\d+\s*\w+)\<', siteBody, re.UNICODE)[0]
            iProcurement['pValueDate'] = dAmounts[0]
            iProcurement['pValueContract'] = dAmounts[1]
            iProcurement['pAmountPaidDate'] = dAmounts[2]
            iProcurement['pAmountPaid'] = dAmounts[3]
    
            # Financing source
            iProcurement['pFinancingSource'] = re.findall( ur'Financing\s+source.*?\<td\>(.*?)\s*\<br\>.*?\<strong\>(.*?)\<', siteBody, re.UNICODE)[0]
            
            # Procurement Base
            iProcurement['pProcurementBase'] = re.findall( ur'Procurement\s+Base.*?\<td\>[&quot;]?(.*?)[&quot;]?\s*\<', siteBody, re.UNICODE)[0]
            
            # Document
            iProcurement['pDocument'] = re.findall( ur'Document.*?\<td.*?\>(.*?)\s*\<br.*?\>(#\s*.*?)\<br.*?(\d{2}\.\d{2}\.\d{4}).*?(\d{2}\.\d{2}\.\d{4}).*?(\d{2}\.\d{2}\.\d{4})\<', siteBody, re.UNICODE)[0]
            
            # Attachments 
            '''
            TODO
            
            Modify so multiple attachments can be downloaded
            '''
            
            #     Problem for now with unicode characters in file names 
            try:
                iProcurement['pAttachments'] = re.findall( ur'Attached\s+Files.*?href.*?"(.*?)".*?\<i\>(.*?)\<.*?(\d{2}\.\d{2}\.\d{4}\s+\d{2}\:\d{2})\<', siteBody, re.UNICODE)[0]
            except IndexError:
                #sometimes there is no link to the attachment, need to deal with this case
                iProcurement['pAttachments'] = re.findall( ur'Attached\s+Files.*?\<i\>(.*?)\<.*?(\d{2}\.\d{2}\.\d{4}\s+\d{2}\:\d{2})\<', siteBody, re.UNICODE)[0]
                
            
            if len( iProcurement['pAttachments']) < 3:
                iProcurement['pAttachments'] = 'Not available'
            else:
                yield Request( 'https://' + self.allowed_domains[0] + '/' + iProcurement['pAttachments'][0], 
                               callback = lambda data, filename = iProcurement['pAttachments'][1]: self._save_attachment( data, filename))
            
            # Contract Type
            iProcurement['pContractType'] = re.findall( ur'Contract\s+type.*?\<div.*?\>(.*?)\<', siteBody, re.UNICODE)[0]
            
            # Agreement Amount
            iProcurement['pAgreementAmount'] = re.findall( ur'Agreement\s+Amount.*?\<div.*?\>(\d+\.*\d* \w+)\<', siteBody, re.UNICODE)[0]
            
            # Agreement Done
            iProcurement['pAgreementDone'] = re.findall( ur'Agreement\s+Done.*?\<div.*?\>(.*?)\<', siteBody, re.UNICODE)[0]
            
            # CPV Codes (main)
            allCodes = re.findall(  ur'CPV\s+Codes\s+\(main\)\<\/div\>(.*?\<\/div\>)&nbsp;', siteBody, re.UNICODE)[0]
            iProcurement['pCPVCodesMain'] = re.findall( ur'(\d+\s+.*?)\<\/div', allCodes, re.UNICODE)
            
            # CPV Codes( detailed)
            allCodes = re.findall(  ur'CPV\s+Codes\s+\(detailed\)\<\/div\>(.*?\<\/div\>)&nbsp;', siteBody, re.UNICODE)[0]
            iProcurement['pCPVCodesDetailed'] = re.findall( ur'(\d+\s+.*?)\<\/div', allCodes, re.UNICODE)
            
            yield iProcurement
            
        # error thrown by ex.findall when extracting beyond the end of the string 
        except IndexError:        
            # TEMP
            print 'Error scraping url:'
            print response.url
        
  
        
        
        
        
        
        
        
    
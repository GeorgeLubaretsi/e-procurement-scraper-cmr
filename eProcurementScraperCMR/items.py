# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Procurement(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pCMR = scrapy.Field()
    pStatus = scrapy.Field()
    pProcuringEntities = scrapy.Field()
    pSupplier = scrapy.Field()
    pValueContract = scrapy.Field()
    pValueDate = scrapy.Field()
    pAmountPaid = scrapy.Field()
    pAmountPaidDate = scrapy.Field()
    pFinancingSource = scrapy.Field()
    pProcurementBase = scrapy.Field()
    pDocument = scrapy.Field()
    pAttachments = scrapy.Field()
    pContractType = scrapy.Field()
    pAgreementAmount = scrapy.Field()
    pAgreementDone = scrapy.Field()
    pCPVCodesMain = scrapy.Field()
    pCPVCodesDetailed = scrapy.Field()
    pWebID = scrapy.Item()
    

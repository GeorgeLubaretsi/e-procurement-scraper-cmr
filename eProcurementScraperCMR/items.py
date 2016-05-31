# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class Procurement(Item):
    # define the fields for your item here like:
    # name = Field()
    pCMR = Field()
    pStatus = Field()
    pProcuringEntities = Field()
    pSupplier = Field()
    pValueContract = Field()
    pValueDate = Field()
    pAmountPaid = Field()
    pAmountPaidDate = Field()
    pFinancingSource = Field()
    pProcurementBase = Field()
    pDocument = Field()
    pAttachments = Field()
    pContractType = Field()
    pAgreementAmount = Field()
    pAgreementDone = Field()
    pCPVCodesMain = Field()
    pCPVCodesDetailed = Field()
    pWebID = Field()
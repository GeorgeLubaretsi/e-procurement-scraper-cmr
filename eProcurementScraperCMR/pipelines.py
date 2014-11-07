# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

class CMRProcurementPipeline(object):
    
    # we use the pipeline to download files attached to procurements
    # the output folder is spider.attachments_folder
    
    def process_item(self, item, spider):
 
        return item


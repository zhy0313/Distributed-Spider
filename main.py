# -*- coding: utf-8 -*-
__author__ = 'pengtuo'


import sys
import os
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(['scrapy', 'crawl', 'jobbole'])
# execute(['scrapy', 'crawl', 'zhihu'])
execute(['scrapy', 'crawl', 'lagou'])

#!/usr/bin/env bash
scrapy crawl food -o'eleme%(time)s.json' -s FEED_EXPORT_ENCODING=UTF-8
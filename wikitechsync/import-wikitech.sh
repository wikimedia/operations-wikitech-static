#!/bin/bash
#
# This should be called from a cron on wikitech-static

DATE=$(date '+%Y%m%d')

wget https://wikitech.wikimedia.org/dumps/labswiki-${DATE}.xml.gz -O /srv/imports/labswiki-${DATE}.xml.gz -4
cd /srv/mediawiki/w
php maintenance/importDump.php /srv/imports/labswiki-${DATE}.xml.gz
php maintenance/rebuildrecentchanges.php
php maintenance/rebuildImages.php --missing

rm /srv/imports/labswiki-${DATE}.xml.gz

/wikitech-static/wikitechsync/get_images.py --wiki wikitech --config /wikitech-static/wikitechsync/dump_images.conf.wikitech-static --verbose
wget https://wikitech.wikimedia.org/dumps/labswiki-${DATE}-images.tar.gz -O /srv/imports/labswiki-${DATE}-images.tar.gz -4
cd /srv/mediawiki
tar -xzvf /srv/imports/labswiki-${DATE}-images.tar.gz
rm /srv/imports/labswiki-${DATE}-images.tar.gz



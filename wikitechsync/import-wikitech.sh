#!/bin/bash
#
# This should be called from a cron on wikitech-static

DATE=$(date '+%Y%m%d')

wget https://wikitech.wikimedia.org/dumps/labswiki-${DATE}.xml.gz -O /srv/imports/labswiki-${DATE}.xml.gz -4
cd /srv/mediawiki/w

# Do this once without --uploads in case --uploads crashes:
php maintenance/importDump.php /srv/imports/labswiki-${DATE}.xml.gz

# Now try to get images if we can:
php maintenance/importDump.php --uploads /srv/imports/labswiki-${DATE}.xml.gz

php maintenance/rebuildrecentchanges.php
php maintenance/rebuildImages.php --missing

rm /srv/imports/labswiki-${DATE}.xml.gz

/wikitech-static/wikitechsync/get_images.py --wiki wikitech --config /wikitech-static/wikitechsync/dump_images.conf.wikitech-static --verbose
chown -R www-data /srv/mediawiki/images/wikitech
chgrp -R www-data /srv/mediawiki/images/wikitech

php maintenance/rebuildImages.php --missing
/usr/sbin/service apache2 graceful
/usr/sbin/service memcached restart

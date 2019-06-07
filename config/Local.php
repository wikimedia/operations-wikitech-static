<?php

$wgDebugLogFile = "/var/log/debug-wikitech.log";
$wgDBserver         = "localhost";
$wgDBname           = "wikitech";
$wgCookieDomain     = "wikitech-static.wikimedia.org";
$wgLogo             = "https://wikitech-static.wikimedia.org/w/images/labswiki.png";

$wgSitename         = "Wikitech";
$wgPasswordSenderName = "Wikitech-static Mail";

$wgUploadDirectory = '/srv/mediawiki/images/wikitech';
$wgUploadPath = '/w/images/wikitech';

$wgGroupPermissions['*']['createaccount'] = false;

$wgExtraNamespaces[110] = 'Obsolete';
$wgExtraNamespaces[111] = 'Obsolete_talk';
$wgNamespacesWithSubpages[110] = true;

$wgInterwikiCache = include_once( "/srv/mediawiki/config/interwiki.php" );
wfLoadSkins( [ 'Vector' ] );

$wgDebugComments = true;
$wgLoadFileinfoExtension = true;

$wgSiteNotice = "You are browsing a read-only backup copy of Wikitech. The live site can be found at [https://wikitech.wikimedia.org wikitech.wikimedia.org]";

<?php

$wgDebugLogFile = "/var/log/debug-wikitech.log";
$wgDBserver         = "localhost";
$wgDBname           = "wikitech";
$wgCookieDomain     = "wikitech-static.wikimedia.org";
$wgLogo             = "https://wikitech-static.wikimedia.org/w/images/labswiki.png";

$wgSitename         = "Wikitech";
$wgPasswordSenderName = "Wikitech-static Mail";

#$wgUploadDirectory = '/srv/mediawiki/images';
$wgUploadDirectory = '/srv/mediawiki/imagedumps/wikitech';

$wgGroupPermissions['*']['createaccount'] = false;

$wgExtraNamespaces[110] = 'Obsolete';
$wgExtraNamespaces[111] = 'Obsolete_talk';
$wgNamespacesWithSubpages[110] = true;

require_once "$IP/skins/Vector/Vector.php";

$wgInterwikiCache = include_once( "/srv/mediawiki/config/interwiki.php" );

$wgDebugComments = true;

<?php

#$wgDebugLogFile = "/var/log/debug-wikitech.log";
$wgDBserver         = "localhost";
$wgDBname           = "wikitech";
$wgCookieDomain     = "wikitech-static.wikimedia.org";
//$wgLogo             = "https://wikitech-static.wikimedia.org/w/images/labswiki.png";
//$wgFavicon          = "https://wikitech-static.wikimedia.org/w/images/favicon.ico";

$wgLogos = [
	'1x' => 'https://wikitech-static.wikimedia.org/w/images/wikitech.png',
	'1.5x' => 'https://wikitech-static.wikimedia.org/w/images/wikitech-1.5x.png',
	'2x' => 'https://wikitech-static.wikimedia.org/w/images/wikitech-2x.png',
];

$wgSitename         = "Wikitech-static";
$wgPasswordSenderName = "Wikitech-static Mail";

$wgUploadDirectory = '/srv/mediawiki/images/wikitech';
$wgUploadPath = '/w/images/wikitech';

$wgGroupPermissions['*']['createaccount'] = false;

$wgExtraNamespaces[110] = 'Obsolete';
$wgExtraNamespaces[111] = 'Obsolete_talk';
$wgNamespacesWithSubpages[110] = true;

$wgInterwikiCache = require "/srv/mediawiki/config/interwiki.php";
wfLoadSkins( [ 'Vector' ] );

$wgDebugComments = true;
$wgLoadFileinfoExtension = true;

$wgSiteNotice = "You are browsing a read-only backup copy of Wikitech. The live site can be found at [https://wikitech.wikimedia.org wikitech.wikimedia.org]";

$wgServer = "https://wikitech-static.wikimedia.org";
$wgCanonicalServer = "https://wikitech-static.wikimedia.org";
$wgInternalServer = "https://wikitech-static.wikimedia.org";

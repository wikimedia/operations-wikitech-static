<?php

$wgScriptPath       = "/w";
$wgScriptExtension  = ".php";
$wgArticlePath = '/wiki/$1';

$wgStylePath        = "$wgScriptPath/skins";

$wgEnableEmail      = true;
$wgEnableUserEmail  = true;

$wgEmergencyContact = "noc@wikimedia.org";
$wgPasswordSender   = "noc@wikimedia.org";

$wgEnotifUserTalk      = true;
$wgEnotifWatchlist     = true;
$wgEmailAuthentication = true;

$wgEnableUploads  = true;
$wgUseImageMagick = true;
$wgImageMagickConvertCommand = "/usr/bin/convert";

$wgUseInstantCommons  = true;

$wgShellLocale = "en_US.utf8";

$wgUseTeX           = false;

$wgLanguageCode = "en";

$wgDefaultSkin = "vector";

$wgEnableCreativeCommonsRdf = true;
$wgRightsPage = "";
$wgRightsUrl  = "http://creativecommons.org/licenses/by-sa/3.0/";
$wgRightsText = "Creative Commons Attribution Share Alike";
$wgRightsIcon = "{$wgStylePath}/common/images/cc-by-sa.png";

$wgDiff3 = "/usr/bin/diff3";

$wgDBtype           = "mysql";
$wgDBprefix         = "";
$wgDBTableOptions   = "ENGINE=InnoDB, DEFAULT CHARSET=binary";
$wgDBmysql5 = false;

$wgJobRunRate = 0;

$wgCacheDirectory = "$IP/cache";

$wgMainCacheType    = CACHE_MEMCACHED;
$wgParserCacheType = CACHE_MEMCACHED;
$wgMessageCacheType = CACHE_MEMCACHED; 
$wgSessionsInMemcached = true;
$wgMemCachedServers = array( '127.0.0.1:11211' );

$wgInterwikiCache = "$wgCacheDirectory/interwiki.cdb";

$wgCacheEpoch = "20160209022930";

$wgCookieSecure = true;
# 7 days max login token. Keystone is set to 7.1 days. If either changes
# then both need to be adjusted
$wgCookieExpiration = 604800;

$wgShowIPinHeader = false;
$wgDisableCounters = true;

$wgAllowUserCss = true;
$wgAllowUserJs = true;

// $wgAppleTouchIcon = '/Wikitech-apple-touch-icon.png'; -- removed by AM 2016-02-09 per https://phabricator.wikimedia.org/T102699

# Anons can't edit
$wgGroupPermissions['*']['edit'] = false;

# Give another group import rights
$wgGroupPermissions['importers']['import'] = true;
$wgGroupPermissions['importers']['importupload'] = true;

#$wgGroupPermissions['accountcreators']['createaccount'] = true;

$wgGroupPermissions['contentadmin']['protect'] = true;
$wgGroupPermissions['contentadmin']['editprotected'] = true;
$wgGroupPermissions['contentadmin']['bigdelete'] = true;
$wgGroupPermissions['contentadmin']['delete'] = true;
$wgGroupPermissions['contentadmin']['undelete'] = true;
$wgGroupPermissions['contentadmin']['block'] = true;
$wgGroupPermissions['contentadmin']['blockemail'] = true;
$wgGroupPermissions['contentadmin']['patrol'] = true;
$wgGroupPermissions['contentadmin']['autopatrol'] = true;
$wgGroupPermissions['contentadmin']['import'] = true;
$wgGroupPermissions['contentadmin']['importupload'] = true;
$wgGroupPermissions['contentadmin']['upload_by_url'] = true;
$wgGroupPermissions['contentadmin']['movefile'] = true;
$wgGroupPermissions['contentadmin']['suppressredirect'] = true;
$wgGroupPermissions['contentadmin']['rollback'] = true;
$wgGroupPermissions['contentadmin']['browsearchive'] = true;
$wgGroupPermissions['contentadmin']['deletedhistory'] = true;
$wgGroupPermissions['contentadmin']['deletedtext'] = true;
$wgGroupPermissions['contentadmin']['autoconfirmed'] = true;

$wgNamespacesWithSubpages[NS_MAIN] = true;
$wgNamespacesWithSubpages[NS_TEMPLATE] = true;

$wgEmailConfirmToEdit = true;
# Disabling SVG for now
$wgFileExtensions = array( 'png', 'gif', 'jpg', 'jpeg', 'xcf', 'pdf', 'mid', 'ogg', 'ogv', 'svg', 'djvu', 'tiff', 'tif', 'ogg', 'ogv', 'oga', 'webm' );
$wgMaxShellMemory = 302400;
$wgSVGConverters['rsvg-secure'] = '$path/rsvg-convert -w $width -h $height -o $output < $input';
$wgSVGConverter = 'rsvg-secure';

$wgDefaultUserOptions['usebetatoolbar'] = 1;
$wgDefaultUserOptions['usebetatoolbar-cgd'] = 1;

require_once( "$IP/extensions/Echo/Echo.php" );
require_once( "$IP/extensions/Scribunto/Scribunto.php" );
$wgScribuntoDefaultEngine = 'luastandalone';
$wgScribuntoUseGeSHi = true;
$wgScribuntoUseCodeEditor = true;

wfLoadExtension( "ConfirmEdit" );
wfLoadExtension( "ConfirmEdit/FancyCaptcha" );
$wgCaptchaClass = 'FancyCaptcha';
$wgCaptchaDirectory = '/srv/org/wikimedia/controller/wikis/captcha';
$wgCaptchaDirectoryLevels = 0;
$wgCaptchaWhitelist = '#^(https?:)?//([.a-z0-9-]+\\.)?((wikidata|wikimedia|wikipedia|wiktionary|wikiquote|wikibooks|wikisource|wikispecies|mediawiki|wikimediafoundation|wikinews|wikiversity|wikivoyage)\.org|dnsstuff\.com|completewhois\.com|wikimedia\.de|toolserver\.org)(/|$)#i';
$wgGroupPermissions['accountcreators']['skipcaptcha'] = true;
$wgGroupPermissions['bots']['skipcaptcha'] = true;
$wgCaptchaTriggers['addurl']        = false;

require_once( "$IP/extensions/Renameuser/Renameuser.php" );

require_once( "$IP/extensions/DynamicSidebar/DynamicSidebar.php" );

require_once( "$IP/extensions/SyntaxHighlight_GeSHi/SyntaxHighlight_GeSHi.php" );

wfLoadExtension( "Cite" );

//require_once( "$IP/extensions/Vector/Vector.php" );
//$wgDefaultUserOptions['vector-collapsiblenav'] = 1;
//$wgVectorUseSimpleSearch = true;

wfLoadExtension( "Gadgets" );
wfLoadExtension( "CategoryTree" );
wfLoadExtension( "ParserFunctions" );
wfLoadExtension( "TitleBlacklist" );

$wgTitleBlacklistSources = array(
	array(
		'type' => 'localpage',
		'src'  => 'MediaWiki:Titleblacklist',
	),
);

require_once( "$IP/extensions/PdfHandler/PdfHandler.php" );

require_once( "$IP/extensions/TitleKey/TitleKey.php" );

require_once( "$IP/extensions/EventLogging/EventLogging.php" );

wfLoadExtension( 'TemplateStyles' );

require_once( "Local.php" );
require_once( "Private.php" );
require_once( "Debug.php" );

$wgDebugLogGroups["dynamic-sidebar"] = "/tmp/sidebar-debug.txt";
$wgDebugLogGroups["T125695"] = "/tmp/T125695-debug.txt";

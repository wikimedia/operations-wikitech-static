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
$wgMemCachedServers = [ '127.0.0.1:11211' ];

$wgCacheEpoch = "20160209022930";

$wgCookieSecure = true;
# 7 days max login token. Keystone is set to 7.1 days. If either changes
# then both need to be adjusted
$wgCookieExpiration = 604800;

$wgShowIPinHeader = false;
$wgDisableCounters = true;

$wgAllowUserCss = true;
$wgAllowUserJs = true;

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
$wgFileExtensions = [ 'png', 'gif', 'jpg', 'jpeg', 'xcf', 'pdf', 'mid', 'ogg', 'ogv', 'svg', 'djvu', 'tiff', 'tif', 'ogg', 'ogv', 'oga', 'webm' ];
$wgMaxShellMemory = 302400;
$wgSVGConverters['rsvg-secure'] = '$path/rsvg-convert -w $width -h $height -o $output < $input';
$wgSVGConverter = 'rsvg-secure';

$wgDefaultUserOptions['usebetatoolbar'] = 1;
$wgDefaultUserOptions['usebetatoolbar-cgd'] = 1;

wfLoadExtension( 'Echo' );
wfLoadExtension( 'Scribunto' );
$wgScribuntoDefaultEngine = 'luastandalone';
$wgScribuntoUseGeSHi = true;
$wgScribuntoUseCodeEditor = true;

wfLoadExtension( 'Renameuser' );

wfLoadExtension( 'DynamicSidebar' );

wfLoadExtension( 'SyntaxHighlight_GeSHi' );

wfLoadExtension( 'Cite' );

wfLoadExtension( 'Gadgets' );
wfLoadExtension( 'CategoryTree' );
wfLoadExtension( 'ParserFunctions' );
wfLoadExtension( 'TitleBlacklist' );

$wgTitleBlacklistSources = [
	[
		'type' => 'localpage',
		'src'  => 'MediaWiki:Titleblacklist',
	],
];

wfLoadExtension( 'PdfHandler' );

wfLoadExtension( 'TitleKey' );

wfLoadExtension( 'EventLogging' );
wfLoadExtension( 'TemplateStyles' );

// https://www.mediawiki.org/w/index.php?title=Manual:Hooks/SkinTemplateNavigation::Universal&oldid=5531640#Add_a_link_to_a_menu
$wgHooks['SkinTemplateNavigation::Universal'][] = function ( $skinTemplate, &$links ) {
	unset( $links['user-menu']['createaccount'] );
	unset( $links['user-menu']['login'] );
	unset( $links['user-menu']['login-private'] );
	unset( $links['user-menu']['anoncontribs'] );
};

require_once( 'Local.php' );
require_once( 'Private.php' );
require_once( 'Debug.php' );

$wgDebugLogGroups['dynamic-sidebar'] = '/tmp/sidebar-debug.txt';
$wgDebugLogGroups['T125695'] = '/tmp/T125695-debug.txt';

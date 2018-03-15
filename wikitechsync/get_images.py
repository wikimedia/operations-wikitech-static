#!/usr/bin/python

"""
retrieve all the images in the specified wiki that weren't
retrieved during the last run or have been uploaded more
recently
"""
import ConfigParser
import os
import sys
import getopt
import json
import glob
import hashlib
import logging
from subprocess import Popen, PIPE
import shutil
import re
import time
import requests


# TODO:
# * should write a status file 'done' that must exist if
#   dump completes without errors, and dump script can
#   whine at the end if this does not exist
# * should exit if $num failed image retrievals in a row
# * this works fine for wikis with a small number of images
#   where the entire list can fit in memory. should we make it
#   work for large ones?
# * does not retrieve images from commons used on the wiki
# * needs a lot more logging on error, but how much?
#   images can go away at any time and no longer be
#   available for retrieval, for a big wiki this could
#   be thousands


class ImageRetriever(object):
    """
    retrieve all images for a wiki uploaded/updated
    later than the specified date in YYYYMMDD format
    """
    def __init__(self, wiki, config, later_than, verbose):
        self.wiki = wiki
        self.config = config
        # image timestamps are YYYYMMDDHHMMSS so convert ours by padding
        if later_than is None:
            later_than = "00000000"
        self.later_than = later_than + "000000"
        self.verbose = verbose
        self.today = time.strftime("%Y%m%d", time.gmtime())
        self.fixup_db_creds()
        self.conn = requests.Session()
        self.conn.max_redirects = 5
        self.conn.headers.update(
            {"User-Agent": "get_images.py/0.0 (WMF image retriever testing, T188915)"})
        if 'baseurl' in self.config:
            self.baseurl = self.config['baseurl']
        else:
            self.baseurl = self.get_baseurl()
        if self.verbose:
            print("base url for image retrieval is %s" % self.baseurl)

    @staticmethod
    def make_hashdirs(path):
        '''
        given a path, make all missing directories if any
        FIXME this does rather more. also this is inefficient,
        should we make all hash dirs once and be done with it,
        instead of doing a stat for every image retrieval?
        '''
        dirs = os.path.dirname(path)
        if not os.path.exists(dirs):
            os.makedirs(dirs)

    def get_mw_script_cmd(self, maintenance_script):
        '''
        return the full command to run the specified maintenance script, with
        the MWScript command stuffed in front if needed
        '''
        mw_script_location = os.path.join(self.config['mediawiki'], 'multiversion', 'MWScript.php')
        if os.path.exists(mw_script_location):
            return [mw_script_location, maintenance_script]
        elif maintenance_script.startswith('extensions'):
            return ["%s/%s" % (self.config['mediawiki'], maintenance_script)]
        else:
            return ["%s/maintenance/%s" % (self.config['mediawiki'], maintenance_script)]

    def get_db_info(self):
        """
        get db info for the wiki so we can get a mysql connection later
        """
        command = " ".join(self.get_mw_script_cmd("getSlaveServer.php"))
        command = "{php} {command} --wiki={dbname}".format(
            php=self.config['php'], command=command, dbname=self.wiki)
        dumpcommand = command + " --group=dump"
        if self.verbose:
            print("running command %s" % dumpcommand)
        proc = Popen(command, shell=True, stdout=PIPE, bufsize=-1)
        output, _error = proc.communicate()
        if output is None:
            if self.verbose:
                print("failed, trying command %s" % command)
                proc = Popen(command, shell=True, stdout=PIPE, bufsize=-1)
                output, _error = proc.communicate()
        if output is None:
            raise RuntimeError("Failed to get db information for wiki {wiki}\n".format(
                wiki=self.wiki))
        db_server = output
        if db_server is not None:
            db_server = db_server.rstrip('\n')
        db_port = None
        if ':' in db_server:
            db_server, _, db_port = db_server.rpartition(':')
        if db_server is None or not re.match(r'[a-z0-9\-\.]+$', db_server):
            logging.error("Failed to get db server for %s", self.wiki)
            return None, None
        return db_server, db_port

    def run_query(self, server, port, query):
        '''
        assumes that the query passed in is not toxic
        '''
        echocmd = ["/bin/echo", query]
        mysqlcmd = [self.config['mysql'], '-h', server]
        if port is not None:
            mysqlcmd.extend(['-P', port])
        mysqlcmd.extend(['-u', self.config['db_user'], '-p' + self.config['db_password'],
                         '--max_allowed_packet', self.config['maxpacket'], self.wiki,
                         '-r', '--silent'])
        command = " ".join(echocmd) + " | " + " ".join(mysqlcmd)
        if self.verbose:
            print ("running command %s" % command)
        proc = Popen(command, shell=True, stdout=PIPE, bufsize=-1)
        output, _error = proc.communicate()
        if output is None:
            raise RuntimeError("Failed to run query {query} for wiki {wiki}\n".format(
                query=query, wiki=self.wiki))
        return output

    def get_image_list(self):
        """
        get list of image name, timestamp from the image table on
        the wiki
        """
        try:
            db_server, db_port = self.get_db_info()
            if db_server is None:
                return None
            query = '"SELECT img_name, img_timestamp from image"'
            results = self.run_query(db_server, db_port, query)
            return results.splitlines()
        except Exception:
            logging.warn("failed to retrieve image list from %s", self.wiki)
            return None

    def get_images_used(self):
        """
        get list of image names used on the wiki, from the imagelinks table
        """
        try:
            db_server, db_port = self.get_db_info()
            if db_server is None:
                return None
            query = '"SELECT il_to from imagelinks"'
            results = self.run_query(db_server, db_port, query)
            return list(set(results.splitlines()))
        except Exception:
            logging.warn("failed to retrieve image list from %s", self.wiki)
            return None

    def get_image_hashpath(self, name):
        '''
        given the image name, generate the relative path where the
        image should be stored, including the hash directory components,
        and return it
        '''
        dirs = []
        md5_hash = hashlib.md5(name).hexdigest()
        for i in range(0, self.config['hashlevels']):
            dirs.append(md5_hash[0:i + 1])
        dirs.append(name)
        return os.path.join(*dirs)

    def get_image_path(self, name, date=None):
        '''
        get the local path where the image should live, for
        the given image name and date
        date should be YYYYMMDD, anything longer will be tossed
        '''
        hashpath = self.get_image_hashpath(name)
        if self.config['in_place']:
            return os.path.join(self.config['basedir'], self.wiki, hashpath)
        else:
            if date is None:
                date = self.today
            return os.path.join(self.config['basedir'], self.wiki, date[0:8], hashpath)

    def get_mw_setting(self, setting, failok=False):
        '''
        get the value for a mediawiki setting via mw maintenance script
        '''
        script = " ".join(self.get_mw_script_cmd("getConfiguration.php"))
        command = '{php} {script} --wiki={wiki} --group=dump --format=json --regex={setting}'
        command = command.format(php=self.config['php'], script=script,
                                 wiki=self.wiki, setting=setting)
        if self.verbose:
            print("running command: %s" % command)
        proc = Popen(command, shell=True, stdout=PIPE, bufsize=-1)
        output, _error = proc.communicate()
        if output is None:
            if not failok:
                raise RuntimeError("Failed to get {setting} for wiki {wiki}\n".format(
                    setting=setting, wiki=self.wiki))
        if output:
            return json.loads(output.decode('utf8'))
        return None

    def get_baseurl(self):
        '''
        get the base url (https://lang.wikitype.org/)
        from the wikiname. we have to ask mediawiki to do this
        for us.
        '''
        url = self.get_mw_setting('wgUploadPath')['wgUploadPath']
        if url.startswith('//'):
            # prefer https if we have a choice
            return 'https:' + url
        elif url.startswith('/'):
            servername = self.get_mw_setting('wgCanonicalServer')['wgCanonicalServer']
            return servername + url

    def get_db_user(self):
        '''
        get the db user for the specific wiki. we have to
        ask mediawiki to do this for us.
        '''
        user = self.get_mw_setting('wgDBadminuser', failok=True)
        if user and 'wgDBadminuser' in user:
            user = user['wgDBadminuser']
        if not user:
            user = self.get_mw_setting('wgDBuser')['wgDBuser']
        return user

    def get_db_password(self):
        '''
        get the db password for the specific wiki. we have to
        ask mediawiki to do this for us.
        '''
        password = self.get_mw_setting('wgDBadminpassword', failok=True)
        if password and 'wgDBadminpassword' in password:
            password = password['wgDBadminpassword']
        if not password:
            password = self.get_mw_setting('wgDBpassword')['wgDBpassword']
        return password

    def fixup_db_creds(self):
        '''
        ask mediawiki for db credentials if they weren't
        set in the config file
        '''
        if self.config['db_user'] is None:
            self.config['db_user'] = self.get_db_user()
        if self.config['db_password'] is None:
            self.config['db_password'] = self.get_db_password()
        if self.verbose:
            if self.config['db_user'] and self.config['db_password']:
                print("db credentials acquired")

    def get_image_url(self, baseurl, name):
        '''
        given the name of an image, retrieve and return the url
        that could be used to download it
        '''
        path = self.get_image_hashpath(name)
        return baseurl + u"/" + path.decode('utf-8')

    def get_url_with_retries(self, url, descr):
        '''
        get response object for a url with retries
        up to the configured amount, 0 means no retries
        '''
        count = 0
        response = None
        while ((response is None or response.status_code >= 500) and
               count <= self.config['retries']):
            try:
                response = self.get_url(url, descr, count)
            except Exception:
                # timeout of some sort probably
                # but it could be too many redirects too, who knows
                del response
                response = None
            if response and response.status_code == 200:
                return response
            if (count < self.config['retries']):
                time.sleep(self.config['retry_wait'])
            count += 1

        del response
        return None

    def get_url(self, url, descr, count):
        '''
        get and return a response object for a url, or None on error
        exceptions are not caught, the caller should do that
        '''
        response = self.conn.get(
            url, stream=True, timeout=(self.config['conn_timeout'], self.config['read_timeout']))

        if response.status_code >= 400 and response.status_code < 500:
            response.read()
            logging.error("failed to get %s for %s (%s:%s) retry %d",
                          descr, self.wiki, response.status_code, response.reason, count)
            del response
            return None
        return response

    def update_image(self, name, commons=False):
        '''
        given the name of an image as it appears in the image table,
        get a copy of it and stash in the right place
        '''
        output_path = self.get_image_path(name)
        if not os.path.exists(output_path):
            # image might exist if we are rerunning today's dump
            self.make_hashdirs(output_path)
            if commons:
                url = self.get_image_url(self.config['commonsurl'], name)
            else:
                url = self.get_image_url(self.baseurl, name)
            #print("Getting image with url %s" % url)
            response = self.get_url_with_retries(url, "image {name}".format(name=name))

            if response is not None:
                with open(output_path, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response

    def copy_image(self, name):
        '''
        copy existing image to new location
        '''
        old_path = self.get_image_path(name, self.later_than)
        new_path = self.get_image_path(name)
        if not os.path.exists(new_path):
            # image might exist if we are rerunning today's dump
            self.make_hashdirs(new_path)
            shutil.copyfile(old_path, new_path)

    def image_dumpdir(self):
        if self.config['in_place']:
            dumpdir = os.path.join(self.config['basedir'], self.wiki)
        else:
            dumpdir = os.path.join(self.config['basedir'], self.wiki, self.today)
        return dumpdir

    def make_image_dumpdir(self):
        '''
        make the directory where the image dump for the current
        wiki and date will live, making parent directories too
        if needed. Perms will be 755 for all.
        '''
        dumpdir = self.image_dumpdir()
        if not os.path.isdir(dumpdir):
            if self.verbose:
                print("making image dump dir {dumpdir}".format(dumpdir=dumpdir))
            try:
                os.makedirs(dumpdir)
            except Exception:
                logging.error("Failed to create directory %s", dumpdir)
                raise

    def get_existingfiles(self):
        allfiles = []
        for path, subdirs, files in os.walk(self.image_dumpdir()):
            for name in files:
                allfiles.append(os.path.join(path, name))
        return allfiles

    def run(self):
        '''
        get list of images, for each one see if we have one
        that's current from the previous dump and copy it over,
        otherwise get it via the web
        '''
        self.make_image_dumpdir()

        if self.config['in_place']:
            prerunfiles = self.get_existingfiles()

        for count in range(0, self.config['retries'] + 1):
            image_list = self.get_image_list()
            if image_list is not None:
                break
            if count < self.config['retries']:
                time.sleep(self.config['retry_wait'])
        if image_list is None:
            return

        if self.config['used_only']:
            for count in range(0, self.config['retries'] + 1):
                images_used = self.get_images_used()
                if images_used is not None:
                    break
                if count < self.config['retries']:
                    time.sleep(self.config['retry_wait'])
            if image_list is None:
                if self.verbose:
                    print("no images are used")
                return

        if self.verbose:
            if not image_list:
                print("image list is empty")
            else:
                print("processing image list")

        for entry in image_list:
            name, timestamp = entry.split('\t', 1)

            if self.config['in_place']:
                # Each time we see a file, remove it from prerunfiles.
                # At the end, prerunfiles will contain only files that
                #  are no longer present in the db.
                imagepath = self.get_image_path(name)
                if imagepath in prerunfiles:
                    prerunfiles.remove(imagepath)

            if not self.config['used_only'] or name in images_used:
                images_used.remove(name)
                if self.later_than is None or timestamp > self.later_than:
                    # the new version is more recent that whatever we would have
                    self.update_image(name)
                elif not os.path.exists(self.get_image_path(name, self.later_than)):
                    # some insurance in case of a bad run
                    self.update_image(name)
                else:
                    # the old image is great. re-use.
                    self.copy_image(name)

        if self.config['all_used']:
            # We've been marking off images in images_used, so now
            # it contains only the used images that we haven't already downloaded.
            # We don't have timestamps for these, so just grab them all.
            for name in images_used:
                imagepath = self.get_image_path(name)
                if imagepath in prerunfiles:
                    prerunfiles.remove(imagepath)

                self.update_image(name, commons=True)

        if self.config['in_place']:
            for abandoned in prerunfiles:
                if '/thumb/' not in abandoned:
                    print("Cleaning up abandoned file %s" % abandoned)
                    os.remove(abandoned)


def usage(message=None):
    '''
    display a helpful usage message with
    an optional introductory message first
    '''

    if message is not None:
        sys.stderr.write(message)
        sys.stderr.write("\n")
    usage_message = """
Usage: get_images.py --wiki <dbname> --configfile <path> | --help

Options:
  --wiki       (-w):  db name for wiki
  --configfile (-c):  path to config file
  --verbose    (-v):  display a few progress messages
  --help       (-h):  display this help message
"""
    sys.stderr.write(usage_message)
    sys.exit(1)


def get_opts():
    """
    read and parse command line options, returning
    the desired values
    """
    wiki = None
    configfile = None
    verbose = 0

    try:
        (options, remainder) = getopt.gnu_getopt(
            sys.argv[1:], "c:w:vh", ["configfile=", "wiki=", "verbose", "help"])
    except getopt.GetoptError as err:
        usage("Unknown option specified: " + str(err))

    for (opt, val) in options:
        if opt in ["-c", "--configfile"]:
            configfile = val
        elif opt in ["-w", "--wiki"]:
            wiki = val
        elif opt in ["-v", "--verbose"]:
            verbose += 1
        elif opt in ["-h", "--help"]:
            usage("Help for this script")

    if len(remainder) > 0:
        usage("Unknown option(s) specified: <%s>" % remainder[0])
    return wiki, configfile, verbose


def check_opts(wiki, configfile):
    """
    check options and whine if missing/bad
    """
    if wiki is None:
        usage("Missing mandatory argument 'wiki'")
    if configfile is None:
        usage("Missing mandatory argument 'configfile'")
    if not os.path.exists(configfile):
        usage("No such file exists: {cfile}".format(cfile=configfile))
    return


def config_whine(conf, setting, section):
    '''
    whine if a setting is missing from a section
    '''
    if not conf.has_option(section, setting):
        sys.stderr.write(
            "The mandatory setting '{setting}' in the section '{section}' was not defined.".format(
                setting=setting, section=section))
        raise ConfigParser.NoOptionError(section, setting)


def get_config(configfile):
    '''
    process the config file, stash setting names/values into
    a dict and return it
    '''
    conf = ConfigParser.SafeConfigParser()
    conf.read(configfile)
    if not conf.has_section("images"):
        sys.stderr.write("The mandatory configuration section 'images' was not defined.\n")
        raise ConfigParser.NoSectionError('images')

    settings = {}
    for name in ['basedir', 'mediawiki', 'php', 'mysql', 'hashlevels', 'maxpacket']:
        config_whine(conf, name, 'images')
        settings[name] = conf.get("images", name)

    settings['hashlevels'] = int(settings['hashlevels'])

    if not os.path.exists(settings['mysql']):
        raise RuntimeError("mysql command {cmd} not found".format(cmd=settings['mysql']))
    if not os.path.exists(settings['php']):
        raise RuntimeError("php command {cmd} not found".format(cmd=settings['php']))

    settings['db_user'] = None
    settings['db_password'] = None
    if conf.has_option('images', 'user'):
        settings['db_user'] = conf.get("images", "user")
    if conf.has_option('images', 'password'):
        settings['db_password'] = conf.get("images", "password")

    settings['conn_timeout'] = 0
    settings['read_timeout'] = 0
    if conf.has_option('images', 'conn_timeout'):
        settings['conn_timeout'] = int(conf.get("images", "conn_timeout"))
    if conf.has_option('images', 'read_timeout'):
        settings['read_timeout'] = int(conf.get("images", "read_timeout"))

    settings['retries'] = 0
    settings['retry_wait'] = 10
    if conf.has_option('images', 'retries'):
        settings['retries'] = int(conf.get("images", "retries"))
    if conf.has_option('images', 'retry_wait'):
        settings['retry_wait'] = int(conf.get("images", "retry_wait"))

    settings['used_only'] = False
    if conf.has_option('images', 'used_only'):
        used_only = conf.get("images", "used_only")
        if used_only != 'false' and used_only != 'False' and used_only != "0":
            settings['used_only'] = bool(used_only)

    # in_place will update images in a given basedir rather than
    #  creating a new date-stamped subdir on each run.
    settings['in_place'] = False
    if conf.has_option('images', 'in_place'):
        in_place = conf.get("images", "in_place")
        if in_place != 'false' and in_place != 'False' and in_place != "0":
            settings['in_place'] = bool(in_place)

    # all_used will look on commons for images that are linked but
    #  not present locally
    settings['all_used'] = False
    if conf.has_option('images', 'all_used'):
        all_used = conf.get("images", "all_used")
        if all_used != 'false' and all_used != 'False' and all_used != "0":
            settings['all_used'] = bool(all_used)
            if conf.has_option('images', 'commonsurl'):
                settings['commonsurl'] = conf.get("images", "commonsurl")
            else:
                raise RuntimeError("commonsurl must be specified if all_used is set.")

    settings['baseurl'] = None
    if conf.has_option('images', 'baseurl'):
        settings['baseurl'] = conf.get("images", "baseurl")

    return settings


def get_last_run_date(config, wiki):
    '''
    find and return the date (YYYYMMDD) of the last run of this script
    for the given wiki, or return None on error/no previous run

    date is based on the name in the dump directory path,
    not timestamps, and this is fine for us.

    may raise exception if the base directory
    exists but is not readable, etc.
    '''
    output_basedir = os.path.join(config['basedir'], wiki)
    if not os.path.exists(output_basedir):
        return None
    dirs = os.listdir(output_basedir)
    today = time.strftime("%Y%m%d", time.gmtime())
    dates = [dirname for dirname in dirs if dirname.isdigit() and
             len(dirname) == 8 and dirname != today]
    if not dates:
        return None
    dates = sorted(dates)
    return dates[-1]


def do_main():
    """
    main entry point
    """
    logging.basicConfig(level=logging.WARNING)
    wiki, configfile, verbose = get_opts()
    check_opts(wiki, configfile)
    config = get_config(configfile)

    last_run_date = get_last_run_date(config, wiki)
    if verbose:
        print("last image dump for {wiki} was: {date}".format(
            wiki=wiki, date=(last_run_date if last_run_date else "never")))
    image_retriever = ImageRetriever(wiki, config, last_run_date, verbose)
    image_retriever.run()


if __name__ == '__main__':
    do_main()

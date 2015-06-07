#!/usr/bin/env python2.7

import logging
import os
import time
import threading
import argparse
from functools import wraps
from os.path import join, getsize, splitext, basename, abspath
import titlecase
from mutagen.easyid3 import EasyID3
from pyechonest import config as en_config
from pyechonest import artist as en_artist


genre_case_override = {
    "r&b": "R&B",
}


def genre_case(genre):
    def callback(word, **kwargs):
        if word.lower() in genre_case_override:
            return genre_case_override[word.lower()]
    return titlecase.titlecase(genre, callback)


def rate_limited(max_per_second):
    """
    Limits the number of times a function can be called per second.

    Sourced from https://gist.github.com/gregburek/1441055
    """
    lock = threading.Lock()
    min_interval = 1.0 / float(max_per_second)

    def decorate(func):
        last_time_called = [0.0]

        @wraps(func)
        def rate_limited_function(*args, **kwargs):
            lock.acquire()
            elapsed = time.clock() - last_time_called[0]
            left_to_wait = min_interval - elapsed

            if left_to_wait > 0:
                time.sleep(left_to_wait)

            lock.release()

            ret = func(*args, **kwargs)
            last_time_called[0] = time.clock()
            return ret

        return rate_limited_function

    return decorate


class SongInfo(object):
    """
    Holds information about an audio file.
    """

    tag_keys = ('artist', 'author', 'title', 'album', 'genre', 'date', 'performer', 'composer', 'conductor', 
             'lyricist', 'arranger', 'tracknumber', 'discnumber', 'discsubtitle', 'language')

    def __init__(self, pathname, **kwargs):
        self.pathname = pathname
        self.__dict__.update(dict.fromkeys(self.tag_keys))
        self.__dict__.update(kwargs)

    def __str__(self):
        return str(self.__dict__)


class ID3Reader(object):
    """
    Reads tag data from ID3 tags.
    """

    def populate(self, info):
        audio = EasyID3(info.pathname)
        for k in SongInfo.tag_keys:
            try:
                setattr(info, k, audio[k])
            except KeyError, e: pass


class ID3Writer(object):
    """
    Writes ID3 tag data.
    """

    def write(self, pathname, info):
        audio = EasyID3(pathname)
        for k in SongInfo.tag_keys:
            value = getattr(info, k)
            if value:
                audio[k] = value
        audio.save()


class EchoNestTerms(object):
    """
    Applies EchoNest term information based on a simple artist search.

    Artist and title information must already be available.
    """

    def populate(self, info):
        if info.artist and not info.genre:
            self._populate(info)

    @rate_limited(1.5)
    def _populate(self, info):
        artist = en_artist.Artist(info.artist[0])
        genre = []
        for term in artist.get_terms(sort='weight', cache=True):
            if term['weight'] >= 0.5:
                genre.append(genre_case(term['name']))
        info.genre = genre


class GenreCaseFixer(object):
    """
    Fixes genre casing.
    """

    def populate(self, info):
        if info.genre:
            info.genre = [genre_case(s) for s in info.genre]


class TagUpdater(object):
    """
    Updates tags in audio files.
    """

    def __init__(self):
        self.populators = []
        self.writers = []
        self.dry_run = False

    def tag_dir(self, path, accepted_exts):
        """
        Tag all the files within a directory.
        """
        for root, dirs, files in os.walk(path):
            for f in files:
                name, ext = splitext(f)
                if ext.lower() in accepted_exts:
                    try:
                        self.tag(join(root, f))
                    except Exception, e:
                        logging.warning("Failed to tag {}".format(abspath(join(root, f))), exc_info=True)

    def tag(self, pathname):
        """
        Updates tags within a specific file.
        """
        info = SongInfo(pathname)
        self.populate(info)
        logging.info("Tagging {} (artist: {}, title: {}, album: {}, genre: {})".format(abspath(pathname), info.artist, info.title, info.album, info.genre))
        if not self.dry_run:
            for w in self.writers:
                w.write(pathname, info)

    def populate(self, info):
        for p in self.populators:
            p.populate(info)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="* %(message)s")

    parser = argparse.ArgumentParser(description='Update tags in audio files')
    parser.add_argument('--dry-run', action='store_true', help='don\'t change files')
    parser.add_argument('--echonest-key', required=True, help='your EchoNest API key')
    parser.add_argument('dir', help='the directory to scan')

    args = parser.parse_args()

    u = TagUpdater()
    if args.dry_run:
        u.dry_run = True

    u.populators.append(ID3Reader()) # read artist and title from ID3 data
    u.populators.append(EchoNestTerms()) # fetch terms and add as genre

    u.writers.append(ID3Writer()) # write ID3 data

    en_config.ECHO_NEST_API_KEY = args.echonest_key
    u.tag_dir(args.dir, ('.mp3',))
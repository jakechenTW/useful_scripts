import re
import sys
import time

import opencc

from plexapi.server import PlexServer

# plex
BASE_URL = 'https://your-plex-url.com'
TOKEN = 'your-token'
SECTION_MOVIE = ['movie']
SECTION_TV_SHOW = ['tv show', 'animation']

# opencc
OPENCC_CONFIG = 's2twp.json'


def is_containing_chinese(texts):
    if re.search("[\u4e00-\u9FFF]", texts):
        return True
    return False


def translate_video(video, converter):
    print('\nProcessing [{0}]'.format(video.title))
    title = video.title
    is_title_locked = False
    title_sort = video.titleSort
    is_title_sort_locked = False
    summary = video.summary
    is_summary_locked = False
    obj = {}

    # check whether the field are locked
    for field in video.fields:
        if field.name == 'title' and field.locked:
            is_title_locked = True
        elif field.name == 'titleSort' and field.locked:
            is_title_sort_locked = True
        elif field.name == 'summary' and field.locked:
            is_summary_locked = True

    # title
    if not is_title_locked and is_containing_chinese(title):
        translated_title = converter.convert(title)
        if title != translated_title:
            obj['title.value'] = translated_title
            obj['title.locked'] = 1
            print('\ttitle: [{0}]\n\t-> [{1}]'.format(title, translated_title))
    # titleSort
    if not is_title_sort_locked and is_containing_chinese(title_sort):
        translated_title_sort = converter.convert(title_sort)
        if title_sort != translated_title_sort:
            obj['titleSort.value'] = translated_title_sort
            obj['titleSort.locked'] = 1
            print(
                '\ttitleSort: [{0}]\n\t-> [{1}]'.format(
                    title_sort,
                    translated_title_sort
                )
            )
    # summary
    if not is_summary_locked and is_containing_chinese(summary):
        translated_summary = converter.convert(summary)
        if summary != translated_summary:
            obj['summary.value'] = translated_summary
            obj['summary.locked'] = 1
            print(
                '\tsummary: [{0}] -> [{1}]'.format(summary,
                                                   translated_summary)
            )
    if obj:
        video.edit(**obj)
        print('changes applied')
    else:
        print('nothing to change')


def translate_movie(section_name, plex, converter):
    movies = plex.library.section(section_name).search()
    for video in movies:
        translate_video(video, converter)


def translate_tv_show(section_name, plex, converter):
    shows = plex.library.section(section_name).search()
    for show in shows:
        # translate the show itself
        translate_video(show, converter)
        # translate all the episodes belong to the show
        episodes = plex.library.section(section_name).get(show.title).episodes()
        for episode in episodes:
            translate_video(episode, converter)


def main():
    plex = PlexServer(BASE_URL, TOKEN)
    converter = opencc.OpenCC(OPENCC_CONFIG)

    # movie
    for section in SECTION_MOVIE:
        translate_movie(section, plex, converter)
    # tv show
    for section in SECTION_TV_SHOW:
        translate_tv_show(section, plex, converter)


if __name__ == '__main__':
    main()
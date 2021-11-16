# coding: utf-8
from __future__ import unicode_literals

import random

from .common import InfoExtractor
from ..compat import (
    compat_str,
)
from ..utils import (
    ExtractorError,
    try_get,
)


class CamsodaIE(InfoExtractor):
    _VALID_URL = r'https?://www\.camsoda\.com/(?P<id>[0-9A-Za-z-]+)'
    _TEST = {
        'url': 'https://camsoda.com/shyjennifer',
        'info_dict': {
            'id': 'shyjennifer',
            'ext': 'mp4',
            'title': 're:^shyjennifer [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}$',
            'description': 're:^.*$',
            'is_live': True,
        },
        'params': {
            'skip_download': True,
        },
        'skip': 'Room is offline',
    }

    _ROOM_OFFLINE = 'Model is offline.'
    _ROOM_PRIVATE = 'Model is in private show.'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        user_id = 'guest_%u' % random.randrange(10000, 99999)
        data = self._download_json(
            'https://camsoda.com/api/v1/video/vtoken/%s?username=%s' % (video_id, user_id), video_id,
            headers=self.geo_verification_headers())
        if not data:
            raise ExtractorError('Unable to find configuration for stream.')

        stream_name = try_get(data, lambda x: x['stream_name'], compat_str)
        if not stream_name:
            raise ExtractorError(self._ROOM_OFFLINE, expected=True)

        private_servers = try_get(data, lambda x: x['private_servers'], list)
        if private_servers:
            raise ExtractorError(self._ROOM_PRIVATE, expected=True)

        servers = try_get(data, lambda x: x['edge_servers'], list)
        token = try_get(data, lambda x: x['token'], compat_str)

        # Randomly select one of the available edge servers
        server_index = random.randrange(len(servers))
        server = servers[server_index]

        m3u8_url = 'https://%s/%s_v1/index.m3u8?token=%s' % (server, stream_name, token)

        formats = self._extract_m3u8_formats(
            m3u8_url, video_id,
            ext='mp4',
            fatal=False,
            live=True)

        return {
            'id': video_id,
            'title': video_id,
            'is_live': True,
            'formats': formats,
        }

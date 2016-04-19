# twitter_markov - Create markov chain ("_ebooks") accounts on Twitter
# Copyright 2014-2016 Neil Freeman contact@fakeisthenewreal.org

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from os import path
from twitter_markov import checking
from twitter_bot_utils import archive

import tweepy

try:
    basestring
except NameError:
    basestring = str

TWEET = {
    "source": "\u003Ca href=\"http:\/\/twitter.com\/download\/iphone\" rel=\"nofollow\"\u003ETwitter for iPhone\u003C\/a\u003E",
    "entities": {
        "user_mentions": [{
            "name": "John Doe",
            "screen_name": "twitter",
            "indices": [0, 8],
            "id_str": "1",
            "id": 1
        }],
        "media": [],
        "hashtags": [],
        "urls": []
    },
    "in_reply_to_status_id_str": "318563540590010368",
    "id_str": "318565861172600832",
    "in_reply_to_user_id": 14155645,
    "text": "@twitter example tweet example tweet example tweet",
    "id": 318565861172600832,
    "in_reply_to_status_id": 318563540590010368,
    "in_reply_to_screen_name": "twitter",
    "in_reply_to_user_id_str": "14155645",
    "retweeted": None,
    "user": {
        "name": "Neil Freeman",
        "screen_name": "fitnr",
        "protected": False,
        "id_str": "6853512",
        "profile_image_url_https": "https:\/\/pbs.twimg.com\/profile_images\/431817496350314496\/VGgzYAE7_normal.jpeg",
        "id": 6853512,
        "verified": False
    }
}


class tweeter_markov_tests(unittest.TestCase):

    def setUp(self):
        api = tweepy.API()
        self.status = tweepy.Status.parse(api, TWEET)

        with open(path.join(path.dirname(__file__), 'data', 'tweets.txt')) as f:
            self.txt = f.readlines()

        self.archive = archive.read_csv(path.join(path.dirname(__file__), 'data'))

    def test_mention_filter(self):
        mention_filter = checking.construct_tweet_filter(no_mentions=True)
        assert mention_filter(self.status) == u' example tweet example tweet example tweet'

    def test_rt_filter(self):
        retweet_filter = checking.construct_tweet_checker(no_retweets=True)
        assert retweet_filter(self.status)

    def testLinkFilter(self):
        link_filter = checking.construct_tweet_filter(no_urls=True)

        assert link_filter('http://happiness.com/ is https://illusory.co') == ' is '

    def testHashFilter(self):
        hash_filter = checking.construct_tweet_filter(no_hashtags=True)

        assert hash_filter('#happiness is #illusory') == ' is '

    def test_reply_filter(self):
        reply_filter = checking.construct_tweet_checker(no_replies=True)
        assert reply_filter(self.status) is False

    def test_reply_filtering_txtfile(self):
        generator = checking.generator(self.txt, txt=1, no_replies=1)
        self.assertEqual(len(list(generator)), 99)

    def test_reply_filtering_archive(self):
        generator = checking.generator(self.archive, no_replies=1)
        self.assertEqual(len(list(generator)), 98)

    def test_rt_filtering(self):
        generator = checking.generator(self.txt, txt=1, no_retweets=1)
        self.assertEqual(len(list(generator)), 99)

    def test_rt_filtering_archive(self):
        generator = checking.generator(self.archive, no_retweets=1)
        lis = list(generator)
        self.assertEqual(len(lis), 98)

    def test_rt_checking(self):
        checker = checking.construct_tweet_checker(no_retweets=True)
        assert checker('RT @hello There') is False
        assert checker('@hello There') is True

    def test_reply_checking(self):
        checker = checking.construct_tweet_checker(no_replies=True)
        assert checker('RT @hello There') is True
        assert checker('@hello There') is False

        lst = list(self.archive)
        rt = [t for t in lst if t['tweet_id'] == '651607152713433089'][0]

        assert checker(rt) is True

    def testCheckingReturnStatus(self):
        generator = checking.generator([self.status] * 2, return_status=True)
        assert isinstance(next(generator), tweepy.Status)

        generator = checking.generator([self.status] * 2, return_status=False)
        self.assertTrue(isinstance(next(generator), basestring))

        generator = checking.generator(self.archive, return_status=True)
        self.assertTrue(isinstance(next(generator), dict))


if __name__ == '__main__':
    unittest.main()

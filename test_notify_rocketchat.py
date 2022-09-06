import unittest
import unittest.mock as mock
import json

import importlib.machinery
import importlib.util

loader = importlib.machinery.SourceFileLoader('notify', 'notify_rocketchat.py')
spec = importlib.util.spec_from_loader('notify', loader)
notify = importlib.util.module_from_spec(spec)
loader.exec_module(notify)

class Args(object):
    pass

class Testing(unittest.TestCase):

    def test_create_ctx(self):
        actual = notify.create_ctx()
        self.assertFalse(actual.check_hostname)

    def test_create_request(self):
        actual = notify.create_request('http://localhost')
        self.assertEqual(actual.full_url, 'http://localhost')

    @mock.patch('urllib.request.urlopen')
    def test_chat_login(self, mock_urlopen):

        # Mocking urlopen Return Value
        data = '{"status": "success", "data": "foobar"}'
        resp = mock.MagicMock()
        resp.read.return_value = data
        mock_urlopen.return_value = resp

        # Mocking parsed Args
        args = Args()
        args.url =  'http://localhost'
        args.user = 'jonsnow'
        args.password = 'Ygritte123'

        actual = notify.chat_login(args)
        expected = 'foobar'
        self.assertEqual(actual, expected)

    @mock.patch('urllib.request.urlopen')
    def test_chat_message(self, mock_urlopen):

        # Mocking urlopen Return Value
        data = '{"success": true}'
        resp = mock.MagicMock()
        resp.read.return_value = data
        mock_urlopen.return_value = resp

        # Mocking parsed Args
        args = Args()
        args.url =  'http://localhost'
        args.user = 'jonsnow'
        args.password = 'Ygritte123'
        args.channel = 'nightswatch'
        args.message = 'Winter is Coming'

        user = {'authToken': 'foo', 'userId': 'bar'}
        actual = notify.chat_message(user, args)
        expected = json.loads(data)

        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()

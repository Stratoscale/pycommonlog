import unittest
import fakeuser
import log2textwrapper


class Test(unittest.TestCase):
    def setUp(self):
        fakeuser.setUp()

    def tearDown(self):
        fakeuser.tearDown()

    def test_simpleManifest_OneProjectDependsOnTwoOthers_RequirementsFetched(self):
        user = fakeuser.FakeUser("write this message")
        self.assertTrue('write this message' in user.readLogContents())
        self.assertTrue('write this message' in log2textwrapper.run())

if __name__ == '__main__':
    unittest.main()

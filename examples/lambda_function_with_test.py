def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello, World!'
    }


import unittest


class TestLambdaFunction(unittest.TestCase):

    def test_lambda_handler(self):
        event = {}
        context = {}
        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], 'Hello, World!')

if __name__ == '__main__':
    unittest.main()

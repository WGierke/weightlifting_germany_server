import json
from test_main_server import ServerTestCase


class AnalyticsServerTestCase(ServerTestCase):
    def test_filter_adding(self):
        response = self.get_authenticated("/get_filters")
        self.assertEqual(response.normal_body, '{"result": []}')

        response = self.post_authenticated("/add_filter", params={"userId": "1", "filterSetting": "all"})
        self.assertEqual(response.normal_body, 'Added filter successfully')
        response = self.get_authenticated("/get_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userId"], "1")
        self.assertEqual(result[0]["filterSetting"], "all")

        response = self.post_authenticated("/add_filter", params={"userId": "1", "filterSetting": "schwedt"})
        self.assertEqual(response.normal_body, 'Filter was updated successfully')
        response = self.get_authenticated("/get_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userId"], "1")
        self.assertEqual(result[0]["filterSetting"], "schwedt")

        response = self.post_authenticated("/add_filter", params={"userId": "2", "filterSetting": "schwedt"})
        self.assertEqual(response.normal_body, 'Added filter successfully')
        response = self.get_authenticated("/get_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["userId"], "1")
        self.assertEqual(result[0]["filterSetting"], "schwedt")
        self.assertEqual(result[1]["userId"], "2")
        self.assertEqual(result[1]["filterSetting"], "schwedt")

    def test_filter_deleting(self):
        response = self.get_authenticated("/get_filters")
        self.assertEqual(response.normal_body, '{"result": []}')

        response = self.post_authenticated("/add_filter", params={"userId": "1", "filterSetting": "all"})
        response = self.post_authenticated("/add_filter", params={"userId": "2", "filterSetting": "schwedt"})
        response = self.get_authenticated("/get_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["userId"], "1")
        self.assertEqual(result[0]["filterSetting"], "all")
        self.assertEqual(result[1]["userId"], "2")
        self.assertEqual(result[1]["filterSetting"], "schwedt")

        response = self.post_authenticated("/delete_filter", params={"userId": "1", "filterSetting": "all"})
        self.assertEqual(response.normal_body, 'Deleted filter successfully')
        response = self.get_authenticated("/get_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userId"], "2")
        self.assertEqual(result[0]["filterSetting"], "schwedt")

        response = self.post_authenticated("/delete_filter", params={"userId": "1", "filterSetting": "all"})
        self.assertEqual(response.normal_body, 'No filter found')
        response = self.get_authenticated("/get_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userId"], "2")
        self.assertEqual(result[0]["filterSetting"], "schwedt")

        self.post_authenticated("/delete_filter", params={"userId": "2", "filterSetting": "schwedt"})
        response = self.get_authenticated("/get_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 0)

    def test_blog_filter_adding(self):
        response = self.get_authenticated("/get_blog_filters")
        self.assertEqual(response.normal_body, '{"result": []}')

        response = self.post_authenticated("/add_blog_filter", params={"userId": "1", "blogFilterSetting": "all"})
        self.assertEqual(response.normal_body, 'Added blog filter successfully')
        response = self.get_authenticated("/get_blog_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userId"], "1")
        self.assertEqual(result[0]["blogFilterSetting"], "all")

        response = self.post_authenticated("/add_blog_filter", params={"userId": "1", "blogFilterSetting": "schwedt"})
        self.assertEqual(response.normal_body, 'Blog filter was updated successfully')
        response = self.get_authenticated("/get_blog_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userId"], "1")
        self.assertEqual(result[0]["blogFilterSetting"], "schwedt")

        response = self.post_authenticated("/add_blog_filter", params={"userId": "2", "blogFilterSetting": "schwedt"})
        self.assertEqual(response.normal_body, 'Added blog filter successfully')
        response = self.get_authenticated("/get_blog_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["userId"], "1")
        self.assertEqual(result[0]["blogFilterSetting"], "schwedt")
        self.assertEqual(result[1]["userId"], "2")
        self.assertEqual(result[1]["blogFilterSetting"], "schwedt")

    def test_blog_filter_deleting(self):
        response = self.get_authenticated("/get_blog_filters")
        self.assertEqual(response.normal_body, '{"result": []}')

        self.post_authenticated("/add_blog_filter", params={"userId": "1", "blogFilterSetting": "all"})
        self.post_authenticated("/add_blog_filter", params={"userId": "2", "blogFilterSetting": "schwedt"})
        response = self.get_authenticated("/get_blog_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["userId"], "1")
        self.assertEqual(result[0]["blogFilterSetting"], "all")
        self.assertEqual(result[1]["userId"], "2")
        self.assertEqual(result[1]["blogFilterSetting"], "schwedt")

        response = self.post_authenticated("/delete_blog_filter", params={"userId": "1", "blogFilterSetting": "all"})
        self.assertEqual(response.normal_body, 'Deleted blog filter successfully')
        response = self.get_authenticated("/get_blog_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userId"], "2")
        self.assertEqual(result[0]["blogFilterSetting"], "schwedt")

        response = self.post_authenticated("/delete_blog_filter", params={"userId": "1", "blogFilterSetting": "all"})
        self.assertEqual(response.normal_body, 'No blog filter found')
        response = self.get_authenticated("/get_blog_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userId"], "2")
        self.assertEqual(result[0]["blogFilterSetting"], "schwedt")

        response = self.post_authenticated("/delete_blog_filter", params={"userId": "2", "blogFilterSetting": "schwedt"})
        response = self.get_authenticated("/get_blog_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 0)

    def test_protocol_adding(self):
        response = self.get_authenticated("/get_protocols")
        self.assertEqual(response.normal_body, '{"result": []}')

        response = self.post_authenticated("/add_protocol", params={"competitionParties": "MyParty"})
        self.assertEqual(response.normal_body, 'Added protocol successfully')
        response = self.get_authenticated("/get_protocols")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["parties"], "MyParty")

        response = self.post_authenticated("/add_protocol", params={"competitionParties": "MyParty"})
        self.assertEqual(response.normal_body, 'This protocol is already saved')
        response = self.get_authenticated("/get_protocols")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["parties"], "MyParty")

        response = self.post_authenticated("/add_protocol", params={"competitionParties": "MyParty2"})
        self.assertEqual(response.normal_body, 'Added protocol successfully')
        response = self.get_authenticated("/get_protocols")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["parties"], "MyParty")
        self.assertEqual(result[1]["parties"], "MyParty2")

    def test_protocol_deleting(self):
        response = self.get_authenticated("/get_protocols")
        self.assertEqual(response.normal_body, '{"result": []}')

        response = self.post_authenticated("/add_protocol", params={"competitionParties": "MyParty"})
        self.assertEqual(response.normal_body, 'Added protocol successfully')
        response = self.post_authenticated("/add_protocol", params={"competitionParties": "MyParty2"})
        self.assertEqual(response.normal_body, 'Added protocol successfully')
        response = self.get_authenticated("/get_protocols")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["parties"], "MyParty")
        self.assertEqual(result[1]["parties"], "MyParty2")

        response = self.post_authenticated("/delete_protocol", params={"competitionParties": "MyParty2"})
        self.assertEqual(response.normal_body, 'Deleted protocol successfully')
        response = self.get_authenticated("/get_protocols")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["parties"], "MyParty")

        response = self.post_authenticated("/delete_protocol", params={"competitionParties": "MyParty2"})
        self.assertEqual(response.normal_body, 'No protocol found')
        self.get_authenticated("/get_protocols")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["parties"], "MyParty")

        response = self.post_authenticated("/delete_protocol", params={"competitionParties": "MyParty"})
        self.assertEqual(response.normal_body, 'Deleted protocol successfully')
        response = self.get_authenticated("/get_protocols")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 0)

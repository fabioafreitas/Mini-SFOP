from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from datetime import datetime
import asyncio
import logging
from os import getenv


class GetUniProdHistoryReportTests(APITestCase):
    def setUp(self):
        # Create a test user
        pass
    
    @classmethod
    def setUpClass(cls):
        """Run once at the beginning of the test suite."""
        super().setUpClass()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(cls.async_setup())

        cls.user = User.objects.create_user(username='testuser', password='testpassword')
        cls.token = str(AccessToken.for_user(cls.user))
        cls.headers = {'HTTP_AUTHORIZATION': f'Bearer {cls.token}'}
        cls.url = reverse('get_uni_prod_history_report')
        cls.valid_timestamp = int(datetime.now().timestamp())

    @classmethod
    def tearDownClass(cls):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(cls.async_teardown())
        super().tearDownClass()

    @classmethod
    async def async_setup(cls):
        cls.smart_tb_data = None
        # cls.smart_tb_data = SmartruralThingsboardDataStructure(
        #     url=getenv('TB_URL'),
        #     username=getenv('TB_USERNAME'),
        #     password=getenv('TB_PASSWORD')
        # )
        cls.smart_tb_data.logger.setLevel(logging.CRITICAL) # disable the logs
        await cls.smart_tb_data.create_aviquality_env()

    @classmethod
    async def send_fake_data(cls, device_access_token, telemetry_params, total_days=1):
        await cls.smart_tb_data.send_fake_data(
            access_token=device_access_token,
            telemetry_params=telemetry_params,
            total_days=total_days
        )

    @classmethod
    async def async_teardown(cls):
        await cls.smart_tb_data.delete_entities()
        
    def test_01_missing_query_parameters(self):
        """
        Ensure the endpoint returns 400 when required query parameters are missing.
        """
        response = self.client.get(self.url, {}, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
    
    def test_02_invalid_unix_timestamp(self):
        """
        Ensure the endpoint returns 400 when invalid UNIX timestamps are provided.
        """
        invalid_timestamp = "invalid-timestamp"
        response = self.client.get(
            self.url,
            {
                'unix_timestamp_ini': invalid_timestamp,
                'unix_timestamp_end': str(self.valid_timestamp),
                'unit_id': self.smart_tb_data.uni_prod_uuid
            },
            **self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
    
    def test_03_invalid_output_type(self): # TODO: fix this, the return is currently 204
        """
        Ensure the endpoint returns 400 when an invalid output_type is provided.
        """
        response = self.client.get(
            self.url,
            {
                'unix_timestamp_ini': str(self.valid_timestamp),
                'unix_timestamp_end': str(self.valid_timestamp + 1000),
                'unit_id': self.smart_tb_data.uni_prod_uuid,
                'output_type': 'invalid-format'
            },
            **self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
    
    def test_04_start_date_greater_than_end_date(self):
        """
        Ensure the endpoint returns 400 when the start date is greater than or equal to the end date.
        """
        response = self.client.get(
            self.url,
            {
                'unix_timestamp_ini': str(self.valid_timestamp + 1000),
                'unix_timestamp_end': str(self.valid_timestamp),
                'unit_id': self.smart_tb_data.uni_prod_uuid
            },
            **self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)






from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from io import BytesIO
from datetime import datetime
from os import getenv
from pandas import ExcelWriter
import asyncio
import aiohttp
import json
from .utils.utils import is_valid_unixtime_seconds_precision, run_async_tasks

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'unix_timestamp_ini',
            openapi.IN_QUERY,
            description="Start date as a UNIX timestamp (seconds precision).",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            'unix_timestamp_end',
            openapi.IN_QUERY,
            description="End date as a UNIX timestamp (seconds precision).",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            'unit_id',
            openapi.IN_QUERY,
            description="ThingsBoard UNI.PROD asset ID (UUID).",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(
            description="File successfully retrieved, with a download link for the generated PDF.",
            examples={
                'application/json': {
                    'download_url': "https://example.com/downloads/chicken_week_report.pdf"
                }
            }
        ),
        204: openapi.Response(description="No telemetry data available for the specified parameters."),
        400: openapi.Response(description="Invalid query parameters."),
        500: openapi.Response(description="Server-side error, such as ThingsBoard authentication failure, undefined attributes, or other unexpected errors."),
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Enforces JWT authentication
def get_uni_prod_details(request):
    """
    Fetches details of a production unit, including its installation date.

    Parameters:
        - unit_id (str): Production unit ID (UUID).

    Returns:
        - 200 OK: JSON with unit details.
        - 400 Bad Request: Missing parameters.
        - 500 Internal Server Error: Unexpected errors.
    """
    unit_id = request.query_params.get('unit_id')
    if not all([unit_id]):
        return Response(
            {"error": "Missing required query parameters"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    async def run_async_method():
        tb_client = SmartruralThingsboardDataDownloader(
            url=getenv('TB_URL'),
            username=getenv('TB_USERNAME'),
            password=getenv('TB_PASSWORD')
        )
        try:
            async with aiohttp.ClientSession(headers=tb_client.headers) as session:
                tasks = [
                    session.get(url=tb_client.url+f'/api/asset/{unit_id}'),
                    session.get(url=tb_client.url+f'/api/plugins/telemetry/ASSET/{unit_id}/values/attributes/SERVER_SCOPE?keys=installation_date'),
                ]
                results = await run_async_tasks(tasks)
                asset_details = results[0]
                attr_details = results[1]
                if attr_details == []:
                    raise ValueError('thingsboard_attr_config_undefined')
                json_output = {
                    'id':asset_details['id']['id'],
                    'name':asset_details['name'],
                    'installation_date':attr_details[0]['value']
                }
                return json_output
        except Exception as e:
            return ValueError('thingsboard_uni_prod_details_failed')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        json_output = loop.run_until_complete(run_async_method())
    except Exception as e:
        error = e.args[0]
        if error == 'thingsboard_uni_prod_details_failed':
            return Response({"error": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": 'unexpected error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    return Response(json_output, status=status.HTTP_200_OK)


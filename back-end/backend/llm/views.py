from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from os import getenv
import requests, json
from ollama import Client


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["tasks", "workers"],
        properties={
            "tasks": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=["id", "description"],
                properties={
                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "description": openapi.Schema(type=openapi.TYPE_STRING),
                    "location": openapi.Schema(type=openapi.TYPE_STRING),
                },
            )),
            "workers": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=["name", "skills"],
                properties={
                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                    "skills": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_STRING)
                    ),
                },
            )),
        },
    ),
    responses={
        200: openapi.Response(
            description="Successful task-to-worker assignment",
            examples={
                "application/json": {
                    "Alice": [1],
                    "Bob": [2]
                }
            }
        ),
        400: openapi.Response(description="Missing or invalid input"),
        502: openapi.Response(description="Error connecting to or parsing response from the LLM"),
    }
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_tasks(request):
    """
    Assigns tasks to workers based on skills using an LLM (via Ollama).
    Expects JSON input:
    {
        "tasks": [
            {"id": 1, "description": "...", "location": "..."}
        ],
        "workers": [
            {"name": "Alice", "skills": ["irrigation", "sensor"]}
        ]
    }
    """
    data = request.data
    tasks = data.get("tasks", [])
    workers = data.get("workers", [])

    if not tasks or not workers:
        return Response(
            {"error": "Missing 'tasks' or 'workers' in request body."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Format tasks and workers for prompt
    task_lines = [f"{t['id']}. {t['description']} in {t.get('location', 'Unknown')}" for t in tasks]
    worker_lines = [f"- {w['name']}: {', '.join(w.get('skills', []))}" for w in workers]

    prompt = f"""
    You are an AI assistant. Assign the following tasks to the most suitable worker based on their skills.
    Return only the JSON.

    Tasks:
    {chr(10).join(task_lines)}

    Workers:
    {chr(10).join(worker_lines)}

    Return the result in JSON format like:
    {{ "Alice": [1], "Bob": [2] }}
    """
    
    try:
        # Set up Ollama SDK client
        client = Client(host=getenv("OLLAMA_URL", "http://localhost:11434"))
        response = client.chat(
            model=getenv("OLLAMA_MODEL", "gemma3:1b"),
            messages=[{"role": "user", "content": prompt}],
            stream=False,
        )

        # Extract the raw response text
        llm_reply = response["message"]["content"].strip('`\n')[5:]

        try:
            assignments = json.loads(llm_reply)
            return Response(assignments, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON returned by LLM", "raw": llm_reply},
                status=status.HTTP_502_BAD_GATEWAY
            )

    except Exception as e:
        return Response(
            {"error": "LLM connection failed", "details": str(e)},
            status=status.HTTP_502_BAD_GATEWAY
        )
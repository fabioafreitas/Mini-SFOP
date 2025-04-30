from datetime import datetime
import asyncio

def is_valid_unixtime_seconds_precision(timestamp):
    try:
        # Ensure it's an integer
        timestamp = int(timestamp)

        # Ensure it has 10 digits (seconds precision)
        if len(str(timestamp)) != 10:
            return False

        # Validate by converting to a datetime object
        datetime.fromtimestamp(timestamp)
        return True
    except (ValueError, OverflowError):
        return False



async def run_async_tasks(task_list: list) -> list:
        """
        Runs a list of asynchronous tasks concurrently, processes their JSON responses, 
        and handles exceptions gracefully.

        Args:
            task_list (list): A list of asynchronous tasks to execute.

        Returns:
            list: A list containing the results of the processed tasks. 
                  Each result is either the parsed JSON response or an exception.
        """
        async def get_json_from_task(task):
            try:
                response = await task
                # Attempt to parse JSON if available
                if response.headers.get("Content-Type") == "application/json":
                    return await response.json()
                else:
                    return {}
            except Exception as e:
                return e  # Return the exception for later processing

        # Process all tasks concurrently
        results = await asyncio.gather(*(get_json_from_task(task) for task in task_list), return_exceptions=True)
        return results
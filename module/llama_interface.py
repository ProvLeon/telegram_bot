import asyncio
import json
import logging

class LlamaInterface:
    def __init__(self, model_name="llama3"):
        self.model_name = "llama3:latest"

    async def generate_response(self, prompt, max_tokens=100):
        command = [
            "ollama",
            "--format", "json",
            "run",
            self.model_name,
            prompt
        ]

        logging.info(f"Executing command: {' '.join(command)}")

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        logging.info(f"Stdout: {stdout.decode()}")
        logging.info(f"Stderr: {stderr.decode()}")

        try:
            output = json.loads(stdout.decode())
            response = output['response']
            logging.info(f"Generated response: {response}")
            return response
        except json.JSONDecodeError:
            logging.error("Failed to parse JSON output")
            return stdout.decode().strip()
        except KeyError:
            logging.error("'response' key not found in output")
            return str(output)

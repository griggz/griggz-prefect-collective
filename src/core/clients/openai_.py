import os
import openai
from azure.identity import DefaultAzureCredential
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class AzureOpenAIClient:
    def __init__(self, azure_openai_key, azure_openai_endpoint):
        self.azure_openai_key = azure_openai_key
        self.azure_openai_endpoint = azure_openai_endpoint
        # Assuming the environment variable is set for authentication
        self.credential = DefaultAzureCredential()
        self.client = self.authenticate()

    def authenticate(self):
        """
        Authenticates with Azure OpenAI using the provided API key and endpoint.
        """
        # For Azure OpenAI specific SDK, authentication would be handled here
        # This is a placeholder for actual authentication logic
        # Currently, OpenAI Python client is used as an example
        openai.api_key = self.azure_openai_key
        return openai

    def analyze_log(self, log_message):
        """
        Analyzes a log message using Azure OpenAI Service.
        """
        response = self.client.Completion.create(
            engine="davinci",
            prompt=f"Analyze the following log and determine if the pipeline succeeded or failed:\n\n{log_message}",
            temperature=0.7,
            max_tokens=150,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        result = response.choices[0].text.strip()
        return result


class OpenAIClient:
        def __init__(self):
            self.openai_api_key = os.getenv("OPENAI_API_KEY")

        def chat_open_ai(self): 
             return ChatOpenAI(openai_api_key=self.openai_api_key)
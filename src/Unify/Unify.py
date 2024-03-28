import openai
import os
from typing import Generator, AsyncGenerator, Union, Optional, List 
from Exceptions import *

def validate_api_key(api_key):
        if api_key is None:
            api_key = os.environ.get("UNIFY_KEY")
        if api_key is None:
            raise KeyError("UNIFY_KEY is missing. Please make sure it is set correctly!")
        return api_key

class Unify:
    """Class for interacting with the Unify API."""
    def __init__(
            self,
            api_key: Optional[str] = None,
    ) -> None:
        """Initialize the Unify client.

        Args:
            api_key (str, optional): API key for accessing the Unify API. If None, it attempts to retrieve the API key from the environment variable UNIFY_KEY.
              Defaults to None.

        Raises:
            UnifyError: If the API key is missing.
        """
        self.api_key = validate_api_key(api_key)
        try:
            self.client = openai.OpenAI(base_url="https://api.unify.ai/v0/", api_key=self.api_key)
        except openai.OpenAIError as e:
            raise UnifyError(f"Failed to initialize Unify client: {str(e)}")

    def generate(self, messages: Union[str, List[dict]], model: str = "llama-2-13b-chat", provider: str = "anyscale", stream: bool = False) -> Union[Generator[str, None, None], str]:
        """Generate content using the Unify API.

        Args:
            messages (Union[str, List[dict]]): A single prompt as a string or a dictionary containing the conversation history.
            model (str): The name of the model. Defaults to "llama-2-13b-chat".
            provider (str): The provider of the model. Defaults to "anyscale".
            stream (bool): If True, generates content as a stream. If False, generates content as a single response. Defaults to False.

        Returns:
            Union[Generator[str, None, None], str]: If stream is True, returns a generator yielding chunks of content. If stream is False, returns a single string response.

        Raises:
            UnifyError: If an error occurs during content generation.
        """
        if isinstance(messages, str):
            contents = [{"role": "user", "content": messages}]
        else: 
            contents = messages
        
        if stream:
            return self._generate_stream(contents, model, provider)
        else:
            return self._generate_non_stream(contents, model, provider)

    def _generate_stream(self, messages: List[dict], model: str, provider: str) -> Generator[str, None, None]:
        """Generate content as a stream using the Unify API.
        Args:
            messages (List[dict]): A list of dictonaries containing the conversation history.
            model (str): The name of the model.
            provider (str): The provider of the model.

        Yields:
            Generator[str, None, None]: A generator yielding chunks of generated content.

        Raises:
            UnifyError: If an error occurs during content generation.
        """
        try:
            chat_completion = self.client.chat.completions.create(
                model='@'.join([model, provider]),
                messages=messages,
                stream=True
            )
            for chunk in chat_completion:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except openai.OpenAIError as e:
            raise status_error_map[e.status_code](e.message) from None


    def _generate_non_stream(self, messages: List[dict], model: str, provider: str) -> str:
        """Generate content as a single response using the Unify API.

        Args:
            messages (List[dict]): A list of dictonaries containing the conversation history.
            model (str): The name of the model.
            provider (str): The provider of the model.

        Returns:
            str: The generated content as a single response.

        Raises:
            UnifyError: If an error occurs during content generation.
        """
        try:
            chat_completion = self.client.chat.completions.create(
                model='@'.join([model, provider]),
                messages=messages,
                stream=False
            )
            return chat_completion.choices[0].message.content.strip(" ")
        except openai.OpenAIError as e:
            raise status_error_map[e.status_code](e.message) from None

class AsyncUnify:
    """Class for interacting asynchronously with the Unify API."""

    def __init__(
            self,
            api_key: Optional[str] = None,
    ) -> None:
        """Initialize the AsyncUnify client.

        Args:
            api_key (str, optional): API key for accessing the Unify API. If None, it attempts to retrieve the API key from the environment variable UNIFY_KEY.
              Defaults to None.

        Raises:
            UnifyError: If the API key is missing.
        """
        self.api_key = validate_api_key(api_key)
        try:
            self.client = openai.AsyncOpenAI(base_url="https://api.unify.ai/v0/", api_key=self.api_key)
        except openai.OpenAIError as e:
            raise UnifyError(f"Failed to initialize Unify client: {str(e)}")

    async def generate(self, messages: Union[str, List[dict]], model: str = "llama-2-13b-chat", provider: str = "anyscale", stream: bool = False) -> Union[AsyncGenerator[str, None], List[str]]:
        """Generate content asynchronously using the Unify API.

        Args:
            messages (Union[str, List[dict]]): A single prompt as a string or a dictionary containing the conversation history.
            model (str): The name of the model.
            provider (str): The provider of the model.
            stream (bool): If True, generates content as a stream. If False, generates content as a single response. Defaults to False.

        Returns:
            Union[AsyncGenerator[str, None], List[str]]: If stream is True, returns an asynchronous generator yielding chunks of content.
              If stream is False, returns a list of string responses.

        Raises:
            UnifyError: If an error occurs during content generation.
        """
        if isinstance(messages, str):
            contents = [{"role": "user", "content": messages}]
        else: 
            contents = messages

        if stream:
            return self._generate_stream(contents, model, provider)
        else:
            return await self._generate_non_stream(contents, model, provider)

    async def _generate_stream(self, messages: List[dict], model: str,  provider:str) -> AsyncGenerator[str, None]:
        """Generate content as a stream asynchronously using the Unify API.

        Args:
            messages (List[dict]): A list of dictonaries containing the conversation history.
            model (str): The name of the model.
            provider (str): The provider of the model.

        Yields:
            AsyncGenerator[str, None]: An asynchronous generator yielding chunks of generated content.

        Raises:
            UnifyError: If an error occurs during content generation.
        """
        try:
            async with self.client as async_client:
                async_stream = await async_client.chat.completions.create(
                    model='@'.join([model, provider]),
                    messages=messages,
                    stream=True,
                )
                async for chunk in async_stream:
                    yield chunk.choices[0].delta.content or ""
        except openai.OpenAIError as e:
            raise status_error_map[e.status_code](e.message) from None

    async def _generate_non_stream(self, messages: List[dict], model: str, provider: str) -> List[str]:
        """Generate content as a single response asynchronously using the Unify API.

        Args:
            messages (List[dict]): A list of dictonaries containing the conversation history.
            model (str): The name of the model.
            provider (str): The provider of the model.

        Returns:
            List[str]: The generated content as a list of string responses.

        Raises:
            UnifyError: If an error occurs during content generation.
        """
        try:
            async with self.client as async_client:
                async_response = await async_client.chat.completions.create(
                    model='@'.join([model, provider]),
                    messages=messages,
                    stream=False,
                )
            return async_response.choices[0].message.content.strip(" ")
        except openai.OpenAIError as e:
            raise status_error_map[e.status_code](e.message) from None
import unittest
from llm.llm_utils import setup_agent
import os
from dotenv import load_dotenv, find_dotenv
from openai import AzureOpenAI as OpenAIAzureOpenAI

class TestLLMGenerates(unittest.TestCase):

    def test_agent_setup(self):
        agent = setup_agent("GPT4o")
        self.assertIsNotNone(agent)
        self.assertEqual(agent.get_all_prompts(), [])
    
    def test_add_message(self):
        agent = setup_agent("GPT4o")
        agent.add_message({"role": 'user', "content": 'What is the capital of France?'})
        self.assertEqual(agent.get_all_prompts(), [{"role": 'user', "content": 'What is the capital of France?'}])

    
    def test_generation(self):
        agent = setup_agent("GPT4o")
        agent.add_message({"role": 'user', "content": 'Hi'})
        print(agent.get_all_prompts())
        response = agent.get_chat_completion()
        print(response)
        self.assertIsNotNone(response)
        print(f"test_generation response: {response.choices[0].message.content}")


    def test_no_agent(self):
        
        model_name = "GPT4o"

        _ = load_dotenv(find_dotenv())
        deployment_model = os.getenv(f"{model_name}_MODEL_DEPLOYMENT_NAME")

        print("deployment: ", deployment_model)

        azure_endpoint = os.getenv(f"{model_name}_AZURE_OPENAI_ENDPOINT")
        api_key=os.getenv(f"{model_name}_AZURE_OPENAI_KEY")
        api_version=os.getenv(f"{model_name}_AZURE_API_VERSION")
        
        print("azure_endpoint: ", azure_endpoint)
        print("api_key: ", api_key)
        print("api_version:", api_version)

        gpt_client = OpenAIAzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version
            )
        
        messages = [{"role": "user", "content": "say only hello"}]
        print(gpt_client.chat.completions.create(messages=messages, model=deployment_model))

if __name__ == '__main__':
    unittest.main()

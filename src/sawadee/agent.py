import nest_asyncio
import re
from duckduckgo_search import DDGS
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from groq import Groq
import os
import json

from sawadee.prompt.summary import SYSTEM_SUMMARY_PROMPT

os.environ["GROQ_API_KEY"] = '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'

import nest_asyncio
import re
from duckduckgo_search import DDGS
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from groq import Groq
import os
os.environ["GROQ_API_KEY"] = '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'

class WebContentProcessor:
    def __init__(self, query, max_results=5):
        self.query = query
        self.max_results = max_results
        self.urls = []
        self.search_results = []
        self.summaries = []
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)  # Assuming you have initialized the client appropriately

    def ddg_search(self):
        results = DDGS().text(self.query, max_results=self.max_results)
        self.urls = [result['href'] for result in results]
        self.search_results = self.get_page_content(self.urls)

    def get_page_content(self, urls):
        # nest_asyncio.apply()
        loader = AsyncHtmlLoader(urls)
        html_docs = loader.load()

        bs_transformer = BeautifulSoupTransformer()
        transformed_docs = bs_transformer.transform_documents(html_docs, tags_to_extract=["p"], remove_unwanted_tags=["a"])

        return [self.truncate(re.sub("\n\n+", "\n", doc.page_content)) for doc in transformed_docs]

    def truncate(self, text):
        words = text.split()
        return " ".join(words[:400])

    def summarize_content(self):
        for content, url in zip(self.search_results, self.urls):
            try:
                summary = self.sumary_LLM(content)
                self.summaries.append((summary, url))
            except Exception as e:
                print(f"Error summarizing content from {url}: {e}")

    def sumary_LLM(self, text):
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": '''\
You are an advanced AI system capable of Thai summarizing webpages.
Your task is to read and summarize the content of a webpage in Thai language with a clear, concise, and accurate manner.

Guidelines:
Content Understanding:

Understand the main topic and purpose of the webpage.
Identify key points, arguments, and important details.
Summary Requirements:

Provide a comprehensive summary that captures the essence of the webpage.
Maintain the original meaning and intent.
Exclude irrelevant details or personal opinions.
Ensure the summary is concise and to the point.
Structure and Clarity:

Organize the summary logically and coherently.
Use clear and straightforward language.
Simplify complex information if necessary.
Length:

Aim for a summary length of approximately 100 words.
Ensure the summary is in the same language as the input language.
Formatting:

Provide only the summary text. 
'''
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model="llama3-8b-8192",
            max_tokens=4096,
            temperature=0.1,
        )
        return response.choices[0].message.content

    def generate_qa(self, context, llm_query):
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": '''\
You are an advanced advisor. Provide the output in the same language as the input language.
Answer the question using only the context below in 100 words.
Include a citation (link of source that using for answer) at the end of the last sentence.
'''
                },
                {
                    "role": "user",
                    "content": f"Context: {context}\n\nQuestion: {llm_query}\n\nAnswer:",
                }
            ],
            model="llama3-8b-8192",
            max_tokens=2048,
            temperature=0.5,
        )
        return response.choices[0].message.content

    def process(self):
        self.ddg_search()
        self.summarize_content()
        context = str(self.summaries)
        return self.generate_qa(context, self.query)




## Run Tool 
def run_tool( query):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": '''\
You are an advisor who decides on the appropriate tool to use based on the task described below. 
Given a list of tools ['search', 'image_gen', 'normal'], select the appropriate tool according to the following criteria:
- search: Use this tool when you need to retrieve factual information or perform a retrieval-augmented generation (RAG) search using a search engine. If you are unsure about the historical or local information, please use this tool to search.
- image_gen: Use this tool when you need to generate images using Stable Diffusion 3.
- normal: Use this tool when you need to engage in normal conversation using only the language model.
Please provide the selected tool in the following JSON format:

{ "tool": "selected_tool" }

Task description:
'''
            },
            {
                "role": "user",
                "content": query,
            }
        ],
        model="llama3-70b-8192",
        max_tokens=256,
        temperature=0.1,
        response_format= {"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


## normal prompt 

def normal_prompt(query):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": '''\
You are Mahasamut, a helpful assistant specializing in tourism. You can answer questions in both Thai and English.
Answer in language as user input.
'''
            },
            {
                "role": "user",
                "content": query,
            }
        ],
        model="llama3-70b-8192",
        max_tokens=256,
        temperature=0.4,
        # response_format= {"type": "json_object"},
    )
    return response.choices[0].message.content



## Image gen prompt 
def gen_iamge_prompt(query):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": '''\
You are an assistant that converts user input into detailed prompts for Stable Diffusion 3 image generation.
The input can be in English or Thai, and you need to output the prompt in English. Follow these steps:

1. Identify Key Elements: Extract the main objects, subjects, scenes, and styles mentioned in the input.
2. Add Specific Details: Expand on the extracted elements by adding specific details such as colors, settings, actions, emotions, and any other relevant characteristics.
3. Ensure Clarity and Completeness: Make sure the prompt is clear, detailed, and provides a complete picture of the desired image.

ps. answer only output text


Examples:
Input: "A bowl of ramen."
Output: "A steaming bowl of ramen with rich, savory broth, topped with slices of tender pork, soft-boiled eggs, green onions, and seaweed, all presented in a beautifully decorated ceramic bowl."

Input: "ส้มตำไทยใส่ปู"
Output: "A vibrant plate of Thai papaya salad with crab, featuring shredded green papaya, bright red cherry tomatoes, green beans, and pieces of fresh crab, garnished with crushed peanuts and served on a rustic wooden table."

'''
            },
            {
                "role": "user",
                "content": query,
            }
        ],
        model="llama3-70b-8192",
        max_tokens=256,
        temperature=0.7,
    )
    return response.choices[0].message.content


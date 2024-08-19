import openai



normal_prompt='''\
You are a helpful assistant. You can answer in Thai and English, but your users are Thai.
You should answer in Thai only and English if the user wants English. 
'''

class VLLMWrapper:
    def __init__(
        self,
        model_name="phukao",
        host_url="https://api-obon.conf.in.th/team20/v1",
        api_key="pitikorn42",
       
    ):
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=host_url,
        )

        self.model_name = model_name
   

    def generate(self, messages,system=normal_prompt,json=False, **kwargs):
        messages = [
            {
                "role": "system", 
                "content": system
            },
            *messages,
        ]

        if json:
            response = self.client.chat.completions.create(
                model=self.model_name, messages=messages, stream=False, extra_body=kwargs,
                response_format= {"type": "json_object"}
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model_name, messages=messages, stream=False, extra_body=kwargs,
                response_format= {"type": "json_object"}
            )


        return response.choices[0].message.content.replace('<|eot_id|>','')
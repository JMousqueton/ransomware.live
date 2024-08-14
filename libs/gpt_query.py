import openai
import os,re
from dotenv import load_dotenv

class GPTQuery:
    """
    A class to query OpenAI's GPT-4 model for information about company activity sectors.
    
    Methods
    -------
    __init__():
        Initializes the class by loading the API key.
        
    query(prompt, max_tokens=150):
        Sends a prompt to the GPT-4 model and returns the response.
    """


    def __init__(self):
        """Initializes the GPTQuery class by loading the API key from the .env file."""
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.gptmodel = os.getenv('OPENAI_MODEL', 'gpt-4')  # Default to 'gpt-4' if not specified
        openai.api_key = self.api_key

    def clean_activity(sentence):
        colon_position = sentence.find(':')
        hyphen_position = sentence.find('-') 
        # Determine which character occurs first, if any
        if colon_position == -1:
            position = hyphen_position
        elif hyphen_position == -1:
            position = colon_position
        else:
            position = min(colon_position, hyphen_position)
        
        # Extract text after the first occurrence of the character
        text_after = sentence[position + 1:].lstrip()
        text_after = text_after.replace('\"','')

        if text_after.endswith('.'):
            text_after = text_after[:-1]

        return text_after


    def query(self, prompt, max_tokens=150,topic='activity'):
        """
        Sends a prompt to the GPT-4 model and returns the main activity sector of the company.
        
        Parameters
        ----------
        prompt : str
            The prompt to send to the GPT-4 model.
        max_tokens : int, optional
            The maximum number of tokens to generate in the response (default is 150).
            
        Returns
        -------
        str
            The main activity sector of the company.
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.gptmodel,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                n=1,
                stop=None,
                temperature=0.7,
            )
            result = response.choices[0].message['content'].strip()
            if topic == 'activiy':
                keywords = [
                    "sorry",
                    "the website",
                    "not available",
                    "as an ai",
                    "the domain",
                    "the website",
                    " isic ",
                    "without",
                    "not possible"
                ]
                if any(keyword in result.lower() for keyword in keywords):
                    result = "Not found"
                pattern = r"\b\w\s-\s"
                result = re.sub(pattern, "", result)
            return result
        except Exception as e:
            errlog("API GPT : An error occurred: " + e)
            return "Not found"

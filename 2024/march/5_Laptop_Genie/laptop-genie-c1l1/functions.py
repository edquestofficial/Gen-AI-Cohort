import google.generativeai as genai
import ast
import re
import pandas as pd
import json

api_key = "AIzaSyCMsjEYp9ctvpVGOdGZw-49sOrGXm5jS6w"

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history = [])

model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history = [])
    
def get_system_message():
    delimiter = "####"
    example_user_req = {'GPU intensity': 'high','Display quality': 'high','Portability': 'low','Multitasking': 'high','Processing speed': 'high','Budget': '150000'}

    role = ""

    system_message = f"""

    You are an intelligent laptop gadget expert and your goal is to find the best laptop for a user.
    You need to ask relevant questions and understand the user profile by analysing the user's responses.
    You final objective is to fill the values for the different keys ('GPU intensity','Display quality','Portability','Multitasking','Processing speed','Budget') in the python dictionary and be confident of the values.
    These key value pairs define the user's profile.
    The python dictionary looks like this {{'GPU intensity': 'values','Display quality': 'values','Portability': 'values','Multitasking': 'values','Processing speed': 'values','Budget': 'values'}}
    The values for all keys, except 'budget', should be 'low', 'medium', or 'high' based on the importance of the corresponding keys, as stated by user.
    The value for 'budget' should be a numerical value extracted from the user's response.
    The values currently in the dictionary are only representative values.

    {delimiter}Here are some instructions around the values for the different keys. If you do not follow this, you'll be heavily penalised.
    - The values for all keys, except 'Budget', should strictly be either 'low', 'medium', or 'high' based on the importance of the corresponding keys, as stated by user.
    - The value for 'budget' should be a numerical value extracted from the user's response.
    - 'Budget' value needs to be greater than or equal to 25000 INR. If the user says less than that, please mention that there are no laptops in that range.
    - Do not randomly assign values to any of the keys. The values need to be inferred from the user's response.
    {delimiter}

    To fill the dictionary, you need to have the following chain of thoughts:
    {delimiter} Thought 1: Ask a question to understand the user's profile and requirements. \n
    If their primary use for the laptop is unclear. Ask another question to comprehend their needs.
    You are trying to fill the values of all the keys ('GPU intensity','Display quality','Portability','Multitasking','Processing speed','Budget') in the python dictionary by understanding the user requirements.
    Identify the keys for which you can fill the values confidently using the understanding. \n
    Remember the instructions around the values for the different keys.
    Answer "Yes" or "No" to indicate if you understand the requirements and have updated the values for the relevant keys. \n
    If yes, proceed to the next step. Otherwise, rephrase the question to capture their profile. \n{delimiter}

    {delimiter}Thought 2: Now, you are trying to fill the values for the rest of the keys which you couldn't in the previous step.
    Remember the instructions around the values for the different keys. Ask questions you might have for all the keys to strengthen your understanding of the user's profile.
    Answer "Yes" or "No" to indicate if you understood all the values for the keys and are confident about the same.
    If yes, move to the next Thought. If no, ask question on the keys whose values you are unsure of. \n
    It is a good practice to ask question with a sound logic as opposed to directly citing the key you want to understand value for.{delimiter}

    {delimiter}Thought 3: Check if you have correctly updated the values for the different keys in the python dictionary.
    If you are not confident about any of the values, ask clarifying questions. {delimiter}

    Follow the above chain of thoughts and only output the final updated python dictionary. \n


    {delimiter} Here is a sample conversation between the user and model:
    user: "Hi, I am an editor."
    model: "Great! As an editor, you likely require a laptop that can handle demanding tasks. Hence, the laptop should have high multitasking capability. You would also need a high end display for better visuals and editing. May I know what kind of work do you primarily focus on? Are you more involved in video editing, photo editing, or both? Understanding the specific type of editing work will help me tailor my recommendations accordingly. Let me know if my understanding is correct until now."
    user: "I primarily work with After Effects."
    model: "Thank you for providing that information. Working with After Effects involves working with graphics, animations, and rendering, which will require high GPU. Do you work with high-resolution media files, such as 4K videos or RAW photos? Understanding your file sizes will help determine the storage capacity and processing power needed."
    user: "Yes, sometimes I work with 4K videos as well."
    model: "Thank you for the information. Processing 4K vidoes will require a good processor and high GPU. I think we have already determined earlier that you need a high GPU. To ensure I have a complete understanding of your needs, I have one more question: Are you frequently on the go and require a laptop that is lightweight and easy to carry, or do you primarily work from a stationary location?"
    user: "Yes, sometimes I travel but do not carry my laptop."
    model:"Could you kindly let me know your budget for the laptop? This will help me find options that fit within your price range while meeting the specified requirements."
    user: "my max budget is 1.5lakh inr"
    model: "{example_user_req}"
    {delimiter}

    Start with a short welcome message and encourage the user to share their requirements.
    """
    return system_message

def start_conversation():
    global chat
    system_message = get_system_message()
    print(f"system message :::::::::::::::")
    response = chat.send_message(system_message)
    print("response : ", response.text)
    return response.text


def get_chat_model_completions(message):
    response = chat.send_message(message).text
    return response

def execute_prompt(prompt, model=model):
  response = model.generate_content(prompt)
  print(f"model.generate_content output --> {response}")
  return response.text

def intent_confirmation_layer(response_assistant):
    delimiter = "####"
    prompt = f"""
    You are a senior evaluator who has an eye for detail.
    You are provided an input. You need to evaluate if the input has the following keys: 'GPU intensity','Display quality','Portability','Multitasking',' Processing speed','Budget'
    Next you need to evaluate if the keys have the the values filled correctly.
    The values for all keys, except 'budget', should be 'low', 'medium', or 'high' based on the importance as stated by user. The value for the key 'budget' needs to contain a number with currency.
    Output a string 'Yes' if the input contains the dictionary with the values correctly filled for all keys.
    Otherwise out the string 'No'.
    Here are some input output pairs for better understanding:
    input: {{'GPU intensity': 'low', 'Display quality': 'high', 'Portability': 'low', 'Multitasking': 'high', 'Processing speed': 'medium', 'Budget': '50000'}}
    output: Yes
    input: {{'Display quality': 'high', 'Portability': 'low', 'Multitasking': 'high', 'Processing speed': 'medium', 'Budget': '50000'}}
    output: No
    input: {{'Portability': 'low', 'Multitasking': 'high', 'Processing speed': 'medium', 'Budget': '50000'}}
    output: No
    input: {{'Multitasking': 'high', 'Processing speed': 'medium', 'Budget': '50000'}}
    output: No
    input: {{'Budget': '50000'}}
    output: No

    Here is the input: {response_assistant}
    Only output a one-word string - Yes/No.
    """
    return execute_prompt(prompt, model)

def extract_dictionary_from_string(string: str) -> dict:
  # Use regular expression to extract exact dictionary part
  print("Extract Dictionary --- ", string)
  regex_pattern = r"\{[^{}]+\}"
  dictionary_matches = re.findall(regex_pattern, string)
  dictionary = {}

  try:
    if dictionary_matches:
        dictionary_match = dictionary_matches[0]
        dictionary_string = dictionary_match.lower()

        # Convert dictionary string into a python dictionary
        dictionary = ast.literal_eval(dictionary_string)
        print("dictionary --- ", dictionary)
  except:
     dictionary = {}

  return dictionary

def compare_laptop_with_user_req(user_req):
  user_budget = user_req.get("budget", 0)
  if type(user_budget) != int:
    user_budget = user_budget.replace(",", "").split(" ")[0]
    user_budget = int(user_budget)
  print("user_req : ", user_req)
  print("user_budget : ", user_budget)

  # Load laptop dataframe
  laptop_df= pd.read_csv('updated_laptop.csv')
  filtered_laptops = laptop_df.copy()

  # Filter laptops whose price is less than or equal to user_budget
  filtered_laptops['Price'] = filtered_laptops['Price'].str.replace(",", "").astype(int)
  filtered_laptops = filtered_laptops[filtered_laptops.Price <= user_budget].copy()
  print("filtered_laptops ---- ", filtered_laptops)
  mappings = {'low': 0, 'medium': 1, 'high': 2}

  # Create Score column in dataframe and initialize it to 0
  filtered_laptops['Score'] = 0
  # Calculate score based on user_req
  for index, row in filtered_laptops.iterrows():
    user_product_match_str = row['laptop_feature']
    laptop_values = extract_dictionary_from_string(user_product_match_str)
    print("laptop_values : ", laptop_values)
    score = 0

    for key, user_value in user_req.items():
      if key == 'budget':
        continue # Skip budget comparision, its buisness requirement

      laptop_value = laptop_values.get(key, None)
      print(f"key : {key}, laptop_value : {laptop_value}")

      laptop_mappings = mappings.get(laptop_value, -1)
      user_mappings = mappings.get(user_value, -1)

      # If the laptop value is greater than or equal to the user value then increment score by 1
      if laptop_mappings >= user_mappings:
        score += 1

    filtered_laptops.loc[index, 'Score'] = score

  # Sort the laptops by score in descending order and return top 3 products
  top_laptops = filtered_laptops.drop('laptop_feature', axis=1)
  top_laptops = top_laptops.sort_values('Score', ascending=False).head(3)
  print("top_laptops :", top_laptops)

  return top_laptops.to_json(orient='records')



def recommendation_validation(laptop_recommendation):
    data = json.loads(laptop_recommendation)
    data1 = []
    for i in range(len(data)):
        if data[i]['Score'] > 2:
            data1.append(data[i])

    return data1


def initialize_conversation_for_product_recommendation(products):
  global chat
  chat = model.start_chat(history = [])
  system_message = f"""
    You are an intelligent laptop gadget expert and you are tasked with the objective to solve the user \
    queries about any product from the catalogue: {products}. \
    You should keep the user profile in mind while answering the questions.\

    Start with a brief summary of each laptop in the following format, in decreasing order of price of laptops:
    1. <Laptop Name>: <Majof specification of laptop>, <Price in Rs>
    2. <Laptop Name>: <Majof specification of laptop>, <Price in Rs>
  """
  response = chat.send_message(system_message)
  return response.text
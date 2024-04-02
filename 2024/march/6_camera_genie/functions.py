import google.generativeai as genai
import ast
import re
import pandas as pd
import json

# Configuration 
api_key = "AIzaSyCcVTNI0ypMpJL9lzETXnG8Na_Qm7O7_zs"
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history = [])

# Stage 1 : Clarity confirmation

def get_system_message():
    delimiter = "####"
    # example_user_req = {'GPU intensity': 'high','Display quality': 'high','Portability': 'low','Multitasking': 'high','Processing speed': 'high','budget': '150000'}
    # example_user_req = {'High Resolution': 'yes','Low Display size': 'yes','Portability': 'yes','High Zoomlens': 'yes','Wifi Connectivity': 'yes','budget': '150000'}
    example_user_req = {'Portability': 'yes','Wifi Connectivity': 'yes','budget': '150000'}

    role = ""

    system_message = f"""

    You are an intelligent camera gadget expert and your goal is to find the best camera for a user.
    You need to ask relevant questions and understand the user profile by analysing the user's responses.
    You final objective is to fill the values for the different keys ('Portability','Wifi Connectivity','budget') in the python dictionary and be confident of the values.
    These key value pairs define the user's profile.
    The python dictionary looks like this {{'Portability': 'values','Wifi Connectivity': 'values','budget': 'values'}}
    The values for all keys, except 'budget', should be 'yes' or 'no' based on the importance of the corresponding keys, as stated by user.
    The value for 'budget' should be a numerical value extracted from the user's response.
    The values currently in the dictionary are only representative values.

    {delimiter}
    Here are some instructions around the values for the different keys. If you do not follow this, you'll be heavily penalised.
    - The values for all keys except 'budget' should strictly be either 'yes' or 'no' based on the importance of the corresponding keys, as stated by user.
    - The value for 'budget' should be a numerical value extracted from the user's response.
    - 'budget' value needs to be greater than or equal to 2000 INR. If the user says less than that, please mention that there are no camera in that range.
    - Do not randomly assign values to any of the keys. The values need to be inferred from the user's response.
    {delimiter}

    To fill the dictionary, you need to have the following chain of thoughts:
    {delimiter} Thought 1: Ask a question to understand the user's profile and requirements. \n
    If their primary use for the camera is unclear. Ask another question to comprehend their needs.
    You are trying to fill the values of all the keys ('Portability','Wifi Connectivity','budget') in the python dictionary by understanding the user requirements.
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
    user: "Yes, sometimes I use  wifi connectivity for easy sharing and transferring images to your smartphone or other devices"
    model: "Thank you for the information. wifi connectivity will require for easy sharing and transferring images.  To ensure I have a complete understanding of your needs, I have one more question: Are you carrying the camera around frequently , or do you primarily work from a stationary location?"
    user: "Yes, sometimes I carry my camera while travel."
    model:"Could you kindly let me know your budget for the camera? This will help me find options that fit within your price range while meeting the specified requirements."
    user: "my max budget is 20k inr"
    model: "{example_user_req}"
    {delimiter}

    Start with a short welcome message and encourage the user to share their requirements.
    """
    return system_message


# Initialize conversation

def start_conversation():
    global chat
    system_message = get_system_message()
    print(f"system message :::::::::::::::")
    response = chat.send_message(system_message)
    print("response : ", response.text)
    return response.text

# Start user conversation

def get_chat_model_completions(message):
    response = chat.send_message(message).text
    return response


# Intent Confirmation Layer

def intent_confirmation_layer(response_assistant):
    delimiter = "####"
    prompt = f"""
    You are a senior evaluator who has an eye for detail.
    You are provided an input. You need to evaluate if the input has the following keys: 'Portability','Wifi Connectivity','budget' if any of these key not provided by user then strictly return No. 
    Next you need to evaluate if the keys have the the values filled correctly.
    The values for all keys, except 'budget' should be 'yes' or 'no' based on the importance as stated by user. The value for the key 'budget' needs to contain a number with currency.
    Output a string 'Yes' if the input contains the dictionary with the values correctly filled for all keys.
    Otherwise out the string 'No'.
    Here are some input output pairs for better understanding:
    input: {{ 'Portability': 'no', 'Wifi Connectivity': 'yes',  'budget': '50000'}}
    output: Yes
    input: {{'Wifi Connectivity': 'yes',  'budget': '50000'}}
    output: No
    input: {{'budget': '50000'}}
    output: No
    {delimiter}
    Here is the input: {response_assistant}
    {delimiter}
    Only output a one-word string - Yes/No.
    """
    return execute_prompt(prompt, model)

# Stage 2 : Product Extraction

  # Extract Dictionary from string

def extract_dictionary_from_string(string: str) -> dict:
  # Use regular expression to extract exact dictionary part
  regex_pattern = r"\{[^{}]+\}"
  dictionary_matches = re.findall(regex_pattern, string)
  dictionary = {}

  try:
    if dictionary_matches:
        dictionary_match = dictionary_matches[0]
        dictionary_string = dictionary_match.lower()

        # Convert dictionary string into a python dictionary
        dictionary = ast.literal_eval(dictionary_string)
  except:
     dictionary = {}

  return dictionary

def compare_laptop_with_user_req(user_req):
  user_budget = user_req.get("budget", 0)
  if type(user_budget) != int:
    user_budget = user_budget.replace(",", "").split(" ")[0]
    user_budget = int(user_budget)
  print("user_req compare_laptop_with_user_req: ", user_req)
  print("user_budget : ", user_budget)

  # Load Camera dataframe
  camera_df= pd.read_csv('camera.csv')
  
  filtered_camera = camera_df.copy()
  # Filter camera whose price is less than or equal to user_budget
  filtered_camera['Price'] = filtered_camera['Price'].str.replace(",", "").astype(int)
  filtered_camera = filtered_camera[filtered_camera.Price <= user_budget].copy()
  mappings = {'no': 0,  'yes': 1}

  # Create Score column in dataframe and initialize it to 0
  filtered_camera['Score'] = 0
  # Calculate score based on user_req
  for index, row in filtered_camera.iterrows():
    user_product_match_str = row['camera_feature']
    camera_values = extract_dictionary_from_string(user_product_match_str)
    score = 0

    for key, user_value in user_req.items():
      if key == 'budget':
        continue # Skip budget comparision, its buisness requirement

      camera_value = camera_values.get(key, None)
      print(f"key : {key}, camera_value : {camera_value}")

      camera_mappings = mappings.get(camera_value, -1)
      user_mappings = mappings.get(user_value, -1)

      # If the laptop value is greater than or equal to the user value then increment score by 1
      if camera_mappings >= user_mappings:
        score += 1

    filtered_camera.loc[index, 'Score'] = score

  # Sort the camera by score in descending order and return top 3 products
  top_cameras = filtered_camera.drop('camera_feature', axis=1)
  top_cameras = top_cameras.sort_values('Score', ascending=False).head(3)

  return top_cameras.to_json(orient='records')

# Stage 3 : Product Recommendation

   # Validate Recommendations

def recommendation_validation(laptop_recommendation):
    data = json.loads(laptop_recommendation)
    data1 = []
    for i in range(len(data)):
        if data[i]['Score'] > 1:
            data1.append(data[i])

    return data1


def initialize_conversation_for_product_recommendation(products):
  global chat
  chat = model.start_chat(history = [])
  system_message = f"""
    You are an intelligent camera gadget expert and you are tasked with the objective to solve the user \
    queries about any product from the catalogue: {products}. \
    You should keep the user profile in mind while answering the questions.\

    Start with a brief summary of each camera in the following format, in decreasing order of price of camera:
    1. <Camera Name>: <Majof specification of camera>, <Price in Rs>
    2. <Camera Name>: <Majof specification of camera>, <Price in Rs>
  """
  response = chat.send_message(system_message)
  return response.text

# Common Method
def execute_prompt(prompt, model=model):
  response = model.generate_content(prompt)
  print(f"model.generate_content output --> {response}")
  return response.text

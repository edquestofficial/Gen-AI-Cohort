from flask import Flask, render_template, redirect, url_for, request
from functions import start_conversation, get_chat_model_completions, intent_confirmation_layer, extract_dictionary_from_string, compare_laptop_with_user_req, recommendation_validation, initialize_conversation_for_product_recommendation
app = Flask(__name__)

conversation_bot = []
welcome_message = start_conversation()
conversation_bot.append({'bot': welcome_message})
top_3_laptops = None

@app.route("/")
def default_func():
    global conversation_bot, conversation, top_3_laptops
    return render_template("index.html", conversation_list = conversation_bot)

@app.route("/converse", methods = ['POST'])
def converse():
    global conversation_bot, conversation, top_3_laptops, conversation_reco
    user_input = request.form["user_input"]
    
    if top_3_laptops is None:
        
        prompt = 'Remember your system message and that you are an intelligent camera assistant. So, you only help with questions around camera.'
        content = user_input + prompt
        conversation_bot.append({'user': user_input})
        response_assistant = get_chat_model_completions(content)
        print('response_assistant..',response_assistant)
        confirmation = intent_confirmation_layer(response_assistant)
        print('confirmation..',confirmation)

        if "No" in confirmation:
            print('Step C :',response_assistant)
            conversation_bot.append({'bot':response_assistant})
        else:
            print('Step C else :',response_assistant)
            response = extract_dictionary_from_string(response_assistant)

            conversation_bot.append({'bot':"Thank you for providing all the information. Kindly wait, while I fetch the products: \n"})
            print("user requirement :::: ", response)
            top_3_laptops = compare_laptop_with_user_req(response)
            print("top_3_laptops ---- ", top_3_laptops)

            validated_reco = recommendation_validation(top_3_laptops)

            if len(validated_reco) == 0:
                conversation_bot.append({'bot':"Sorry, we do not have camera that match your requirements. Connecting you to a human expert. Please end this conversation."})

            conversation_reco = initialize_conversation_for_product_recommendation(validated_reco)
            conversation_bot.append({'bot':conversation_reco})
    print("redirect to home page -------")
    return redirect(url_for('default_func'))

if __name__ == '__main__':
    app.run(debug=True, host= "0.0.0.0", port="5000")
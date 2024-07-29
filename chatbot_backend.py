import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize the lemmatizer and define stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Define some predefined responses
responses = {
    "greeting": ["Hello! How can I assist you today with Freshbite?"],
    "hours": ["Our delivery hours are from 10 AM to 10 PM every day."],
    "location": ["Freshbite operates in Lahore, Karachi, Islamabad, and other major cities in Pakistan."],
    "menu": ["You can find our menu on our website or app. We offer a variety of cuisines to suit your taste!"],
    "payment": ["We accept payments through Stripe, credit/debit cards, and cash on delivery."],
    "contact": ["You can contact us at support@freshbite.pk or call our helpline at 123-456-7890."],
    "status": ["You can check the status of your order on our app or website under 'My Orders' section."],
    "order": ["To place an order, visit our website or app, browse the menu, and follow the checkout process."],
    "cancel": [
        "To cancel an order, please go to the 'My Orders' section on our app or website and select the order you wish to cancel."],
    "feedback": [
        "We appreciate your feedback! Please leave your feedback on our app or website under the 'Feedback' section."]
}


# Function to preprocess the user input
def preprocess_input(user_input):
    tokens = word_tokenize(user_input)
    tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens if
              token.isalnum() and token.lower() not in stop_words]
    return tokens


# Function to generate a response
def generate_response(user_input):
    tokens = preprocess_input(user_input)

    # Simple keyword-based matching
    if any(token in tokens for token in ["hello", "hi", "hey"]):
        return responses["greeting"][0]
    elif any(token in tokens for token in ["hour", "time", "open"]):
        return responses["hours"][0]
    elif any(token in tokens for token in ["location", "city", "cities", "where"]):
        return responses["location"][0]
    elif any(token in tokens for token in ["menu", "food", "cuisine"]):
        return responses["menu"][0]
    elif any(token in tokens for token in ["payment", "pay", "stripe"]):
        return responses["payment"][0]
    elif any(token in tokens for token in ["contact", "support", "help"]):
        return responses["contact"][0]
    elif any(token in tokens for token in ["status", "track", "order status"]):
        return responses["status"][0]
    elif any(token in tokens for token in ["cancel", "cancelation"]):
        return responses["cancel"][0]
    elif any(token in tokens for token in ["order", "place", "buy"]):
        return responses["order"][0]
    elif any(token in tokens for token in ["feedback", "review"]):
        return responses["feedback"][0]
    else:
        return "I'm sorry, I didn't understand that. Could you please rephrase?"


# Main function to run the chatbot
def chatbot():
    print("Welcome to Freshbite! How can I help you today?")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Chatbot: Thank you for using Freshbite! Have a great day!")
            break
        response = generate_response(user_input)
        print("Chatbot:", response)

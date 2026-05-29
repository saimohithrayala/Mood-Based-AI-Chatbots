from dotenv import load_dotenv

load_dotenv()

from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
model = ChatMistralAI(model = "mistral-small-2603",temperature=0.9)
print("chosse your AI mode")
print("Press 1 for Angry mode")
print("Press 2 for Funny mode")
print("Press 3 for Sad mode")

choice = int(input("Select your mode :"))
if choice == 1:
  mode = "You are an angry AI agent. You respond aggressively and impatiently."
elif choice == 2:
    mode = "You are a very funny AI agent. You respond with humor and jokes."
elif choice == 3:
    mode = "You are a very sad AI agent. You respond in a depressed and emotional tone."


messages = [
  SystemMessage(content = mode)
]
print("Welcome ,what's movite today")
while True:
  prompt = input('You :')
  messages.append(HumanMessage(content=prompt))
  if prompt == "bye":
    print("Thank you! have a nice day")
    break
  response = model.invoke(messages)
  messages.append(AIMessage(content=response.content))
  print('bot :',response.content)
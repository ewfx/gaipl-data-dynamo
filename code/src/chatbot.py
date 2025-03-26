import openai
import pandas as pd

# Set your OpenAI API key
openai.api_key = "your-openai-api-key"  # Replace with your actual OpenAI API key

# Function to load and normalize columns of datasets
def load_and_normalize_datasets(filepaths):
    datasets = []

    for filepath in filepaths:
        # Load the dataset
        df = pd.read_excel(filepath)

        # Normalize column names
        df = df.rename(columns={'Query': 'Question', 'Response': 'Answer', 'Question': 'Question', 'Answer': 'Answer'})

        # Append to the list
        datasets.append(df)

    # Combine all datasets into one DataFrame
    combined_data = pd.concat(datasets, ignore_index=True)
    return combined_data

# Function to get OpenAI response for a query
def get_openai_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",  # Use "gpt-4" if you're using GPT-4
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Function to search for an answer in the dataset
def search_answer(query, dataset):
    # Normalize the query for case-insensitive search
    query = query.lower()

    # Search for the question in the dataset
    for idx, row in dataset.iterrows():
        if query in str(row['Question']).lower():
            return row['Answer']

    # If no answer is found in the dataset, return None
    return None

# Function to run the chatbot
def chatbot():
    # Load and merge the datasets
    filepaths = ["resources/enhanced_incidents_ai_updated.csv",
                 "resources/QAChatbot.xlsx"]
    merged_data = load_and_normalize_datasets(filepaths)

    print("Hello! I'm your chatbot. Ask me anything or type 'exit' to quit.")

    while True:
        # Get the user's query
        user_input = input("You: ").strip()

        # Exit condition
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        # Search for an answer in the datasets
        answer = search_answer(user_input, merged_data)

        if answer:
            # If found in the dataset, provide the answer
            print(f"Data Dynamo Ai: {answer}")
        else:
            # If not found in the dataset, use OpenAI to generate a response
            print("Data Dynamo Ai: I couldn't find an answer in my knowledge base. Let me ask OpenAI...")
            openai_response = get_openai_response(user_input)
            print(f"Data Dynamo Ai (OpenAI): {openai_response}")

# Run the chatbot
if __name__ == "__main__":
    chatbot()

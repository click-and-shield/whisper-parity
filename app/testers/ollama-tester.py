from ollama import chat, ChatResponse

if __name__ == '__main__':
    response: ChatResponse = chat(model='llama3.2', messages=[
      {
        'role': 'user',
        'content': 'Do you have knowledge in science?',
      },
    ])
    print(response['message']['content'])
    # or access fields directly from the response object
    print(response.message.content)

import gradio as gr
import time

from openai import OpenAI

from keys import OPEN_AI_KEY
from prompts import LOAN_BANKER_PROMPT
from images import CASCADING_AI_LOGO

client = OpenAI(api_key=OPEN_AI_KEY)

assistant = client.beta.assistants.create(
                instructions=LOAN_BANKER_PROMPT, 
                model="gpt-4-1106-preview", 
                tools=[{"type": "retrieval"}]
            )

def run_thread(thread_id):
    run = client.beta.threads.runs.create(thread_id, assistant_id=assistant.id)
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    message = messages.data[0]
    message_contents = message.content


    print(message_contents[0].text.value)

    # Poll run status until it's completed, then we can process
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        print(run.status)
        time.sleep(1)

    messages = client.beta.threads.messages.list(thread_id=thread_id)
    message = messages.data[0]
    message_contents = message.content
    message_content = message_contents[0].text
    
    annotations = message_content.annotations

    # Iterate over the annotations and remove them for better output
    for annotation in annotations:
        message_content.value = message_content.value.replace(annotation.text, f'')

    message_value = message_content.value

    return message_value

global THREAD_ID

def upload_file(history, file):
    global THREAD_ID

    openai_file = client.files.create(file=open(file, 'rb'), purpose='assistants')

    # Create thread and process message from assistant
    thread = client.beta.threads.create()
    THREAD_ID = thread.id

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Please give me the decision for the candidate. Put the LOAN ELIGIBILITY before the explanation.",
        file_ids=[openai_file.id]
    )

    message_value = run_thread(thread.id)
    history = history + [((file.name, "Uploaded Bank Statement"), message_value)]

    return history

def add_text(history, text):
    global THREAD_ID
    try:
        _ = THREAD_ID
    except NameError:
        THREAD_ID = None

    chatbot_response = ""

    if THREAD_ID:
        message = client.beta.threads.messages.create(
            thread_id=THREAD_ID,
            role="user",
            content=text
        )

        chatbot_response = run_thread(THREAD_ID)
    else:
        chatbot_response = "There has not been a bank statement file uploaded yet. Please upload one before asking followup questions."

    history = history + [(text, chatbot_response)]
    return history, gr.Textbox(value="", interactive=True)

"""
def bot(history):
    response = "**That's cool!**"

    if type(history[-1][0]) == str:

    history[-1][1] = ""
    for character in response:
        history[-1][1] += character
        time.sleep(0.05)
        yield history
"""

with gr.Blocks() as demo:
    img = gr.Image(CASCADING_AI_LOGO, width=100, height=200, label="Bank Statement Reader", show_download_button=False)
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        bubble_full_width=False
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter followup questions for the candidate's eligibility for the uploaded bank statement",
            container=False,
        )
        btn = gr.UploadButton("Upload Bank Statement (.pdf)", file_types=[".pdf"], file_count="single")

        txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False)
        file_msg = btn.upload(upload_file, [chatbot, btn], [chatbot], queue=False)

demo.launch(share=True)
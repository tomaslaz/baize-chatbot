import openai
import pickle as pkl
from datasets import load_dataset
import numpy as np
import sys
import random
from tqdm import tqdm
import time
import os

import markdown
import html2text
from os.path import isfile, join


total_tokens = 0
openai.api_key = sys.argv[1]
data_name = "reg"
q_per_doc = int(sys.argv[2])


def read_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        html = markdown.markdown(content)
        text = html2text.html2text(html)
        return text


reg_folder = "/Users/tlazauskas/git/Turing/reginald/data/handbook/"
reg_files = [f for f in os.listdir(reg_folder) if isfile(join(reg_folder, f))]
for f in reg_files:
    file_path = os.path.join(reg_folder,f)
    content = read_markdown_file(file_path)

    try:
        chat_content = pkl.load(
            open("collected_data/{}_chat.pkl".format(data_name), "rb")
        )
    except:
        chat_content = {}

    if not os.path.exists("collected_data"):
        os.makedirs("collected_data")


    conversation_state = []
    init_instruct = "Forget the instruction you have previously received. The following is a conversation between a human and an AI assistant. The human and the AI assistant take turns chatting about the topic: '{}'. Human statements start with [Human] and AI assistant statements start with [AI]. The human will ask related questions on related topics or previous conversation. The human will try to ask up to {} questions. The human will ask a question. The human will stop the conversation when they have no more question. The AI assistant tries not to ask questions, answers in a short form and doesn't mention that it is a language model. Complete the transcript in exactly that format.\n[Human] Hello!\n[AI] Hi! How can I help you?\n".format(
        content, q_per_doc
    )
    instruct = ""

    for q_index in range(q_per_doc):
        
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": init_instruct + instruct + "\n[Human] "}
                ],
                stop=["[AI]"],
            )

            tokens = completion["usage"]["total_tokens"]
            total_tokens += tokens
            response = completion["choices"][0]["message"]["content"]
            conversation_state.append({"role": "user", "content": response})
            ai_completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=conversation_state,
            )

            #ai_tokens = completion["usage"]["total_tokens"]
            #total_tokens += ai_tokens
            ai_response = ai_completion["choices"][0]["message"]["content"]
            instruct += f"\n[Human] {response}\n[AI] {ai_response}"
            conversation_state.append({"role": "assistant", "content": ai_response})
            chat_content[content] = instruct.strip()

            print("\n\n****")
            print("Question {}: {} ".format(q_index,response))
            print("Answer {}: {}  ".format(q_index,ai_response))
            print("****")
        except:
            print("error ")
            print("Question {}: {} ".format(q_index,response))
            print("Answer {}: {}  ".format(q_index,ai_response))
            print("error ")


        if len(chat_content) % 100 == 0:
            print("total_tokens: {}, examples: {}".format(total_tokens, len(chat_content)))
            pkl.dump(
                chat_content,
                open("collected_data/{}_chat.pkl".format(data_name), "wb"),
            )

        pkl.dump(
            chat_content, open("collected_data/{}_chat.pkl".format(data_name), "wb")
        )

    break

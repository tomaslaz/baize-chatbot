# Standard library imports
import os
import pickle
import sys
from os.path import isfile, join
from typing import Dict, List

# Third-party imports
import html2text
import markdown
import openai

def read_markdown_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        html = markdown.markdown(content)
        text = html2text.html2text(html)
        return text



def process_file(file_path: str, q_per_doc: int) -> List[Dict[str, str]]:
    content = read_markdown_file(file_path)
    question_prompt = (
        "Forget the instruction you have previously received. "
        + "The following is a conversation between a human and an AI assistant. "
        + f"The human and the AI assistant take turns chatting about the topic: '{content}'. "
        + "Human statements start with [Human] and AI assistant statements start with [AI]. "
        + "The human will ask related questions on related topics or previous conversation. "
        + f"The human will try to ask up to {q_per_doc} questions. "
        + "The human will ask a question. "
        + "The human will stop the conversation when they have no more questions. "
        + "The AI assistant tries not to ask questions, answers in a short form and doesn't mention that it is a language model. "
        + "Complete the transcript in exactly that format.\n"
        + "[Human] Hello!\n[AI] Hi! How can I help you?\n[Human] "
    )
    answer_prompt_fragment = f"Use the information provided here '{content}' to answer"
    output = []

    for q_index in range(q_per_doc):
        try:
            question_generator = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": question_prompt
                    }
                ],
                stop=["[AI]"],
            )
            question = question_generator["choices"][0]["message"]["content"].strip()
            question = question.replace("?", "") + "?"

            answer_generator = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"{answer_prompt_fragment} '{question}'",
                    }
                ],
            )
            answer = answer_generator["choices"][0]["message"]["content"].strip()

            # Store chat content
            output.append({"question": question, "answer": answer})
            print("\n\n****")
            print(f"Question {q_index}: {question}")
            print(f"Answer {q_index}: {answer}")
            print("****")
        except Exception as exc:
            print(f"OpenAI error\n{str(exc)}")

    return output

if __name__ == "__main__":
    openai.api_key = sys.argv[1]
    q_per_doc = int(sys.argv[2])
    reg_folder = (
        sys.argv[3]
        if len(sys.argv) >= 3
        else "/Users/tlazauskas/git/Turing/reginald/data/handbook/"
    )
    data_name = "reg"

    # Load existing answers
    if not os.path.exists("collected_data"):
        os.makedirs("collected_data")
    try:
        output = pickle.load(
            open(f"collected_data/{data_name}_generated.pickle", "rb")
        )
    except:
        output = {}


    reg_files = [f for f in os.listdir(reg_folder) if isfile(join(reg_folder, f))]
    for f in reg_files:
        print(f"Now working on {f}")
        output[f] = process_file(os.path.join(reg_folder, f), q_per_doc)
        pickle.dump(
            output, open("collected_data/{}_generated.pickle".format(data_name), "wb")
        )


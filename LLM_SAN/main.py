# This is a sample Python script.
import copy

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from openai import OpenAI
import json
import pickle
import time
from response_processor import process_response, refine_relationship
OPENAI_KEY = ""

refinement_template = ""
with open("refinement_template.txt", 'r') as refinefile:
    refinement_template = refinefile.read()



def record_response(messages, completion):
    content = completion.choices[0].message.content
    print(content)
    messages.append({"role": "system",
                     "content": content})

    return content

def dump_conv(conv, filename):
    with open(filename, "wb") as obj:
        pickle.dump(conv, obj)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("start def san {}".format(time.time()))
    DIR = "casper_manual"
    save_location = DIR + '/' + "relation.json"
    client = OpenAI(api_key=OPENAI_KEY)
    dialog_location = "conv.txt"
    init_message = [
        {"role": "system","content": "You are a helpful assistant that understand basic logic and the semantics of words"}]

    with open("combined.txt", "r") as first_txt:
        first_question = first_txt.read()
        print(first_question)
        init_message.append( {"role": "user", "content": "{}".format(first_question)})
        # init_message = [
        #     {"role": "system",
        #      "content": "You are a helpful assistant"},
        #     {"role": "user", "content": "{}".format(first_question)}
        # ]
    start_time = time.time()
    completion = client.chat.completions.create(
        model="gpt-4",
        n=1,
        messages=init_message
    )
    response_time = time.time() - start_time
    token_num = completion.usage.completion_tokens
    print("response time {} and tokens {}".format(response_time, token_num))
    content = record_response(init_message, completion)
    dump_conv(init_message, dialog_location)
    parsed_text, relations, test_cases = process_response(content, DIR, save_location)
    old_relations = copy.deepcopy(relations)
    print("new test case {}".format(len(test_cases)))

    while test_cases:
        questions = refinement_template.format(queries = str([json.dumps(test_case.to_json()) for test_case in test_cases]))
        print(questions)
        init_message.append({"role": "user", "content": questions})
        dump_conv(init_message, dialog_location)

        start_time = time.time()
        completion = client.chat.completions.create(
            model="gpt-4",
            n=1,
            messages=init_message
        )

        content = record_response(init_message, completion)
        dump_conv(init_message, dialog_location)
        token_num = completion.usage.completion_tokens
        print("response time {} and tokens {}".format(response_time, token_num))
        parsed_text, relations, test_cases = refine_relationship(relations, content, DIR, save_location)
        print("new test case {}".format(len(test_cases)))

    print("end def san {}".format(time.time()))



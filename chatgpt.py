'''
Author: zhanwei xu
Date: 2023-07-31 21:53:56
LastEditors: zhanwei xu
LastEditTime: 2023-12-28 10:42:02
Description:
Copyright (c) 2023 by zhanwei xu, Tsinghua University, All Rights Reserved.
'''
from src.utils.FileReader import file_lines
from src.utils.TimeWrapper import wrapper_calc_time
import requests
import json
import numpy as np
from tqdm import tqdm
from apikey import OPENAI_API_KEY
UNK_idx = 0
PAD_idx = 1
EOS_idx = 2
SOS_idx = 3
USR_idx = 4
SYS_idx = 5
CLS_idx = 6


class ChatApi():
    def __init__(self, mode='gpt-3.5-turbo-0125'):
        # openai api url
        self.url = "https://api.gptapi.us/v1/chat/completions"
        self.message_json = {
            "model": mode,
            "messages": [
                {
                    "role": "user",
                    "content": "You are a helpful assistant."
                }
            ]
        }
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {OPENAI_API_KEY}"
        }
        print(f"self.headers: {self.headers}")

    def request_data(self, data):
        self.message_json["messages"][0]["content"] = data
        payload = json.dumps(self.message_json)
        # print(f"payload: {payload}")
        response = requests.request(
            "POST", self.url, headers=self.headers, data=payload, stream=True)
        if response.status_code == 200:
            result = json.loads(response.text)
            # print(f"response.text: {response.text}")
            res = result['choices'][0]['message']['content']
        else:
            res = ""
        return res, response.status_code


def strip_word(sentence, word):
    while sentence.startswith(' ') or sentence.startswith(':'):
        sentence = sentence.strip(' ').strip(':')
    if (sentence.startswith(word)):
        return sentence[len(word):].strip(' ')
    return sentence.strip(' ')


def chat_one_data(chat_api, instruction, data):
    while 1:  # try to get the formatted result(when Flag become False)
        try:
            # contruct the instruction
            input_data = data["context"]
            input_data = instruction + '"'+input_data+'"'
            # print(input_data) 
            data['LLM'] = {}
            for r in ['xReact', 'xIntent', 'xNeed', 'xWant', 'xEffect']:
                data['LLM'][r]=[]
                
            for _ in range(5):
                chat_out = None
                status_code = 200
                # try to get the response
                while 1:
                    try:
                        chat_out, status_code = chat_api.request_data(
                            input_data)
                    except Exception as e:
                        print(e)
                    if status_code == 200 :
                        break
                print("="*50)
                print(chat_out)
                print("="*50)
                chat_out_list = chat_out.replace("```","").replace("\n",'').split('|')
                # format the response from LLM
                for i,r in enumerate(['xReact', 'xIntent', 'xNeed', 'xWant', 'xEffect']):
                    data['LLM'][r].append(strip_word(chat_out_list[i], r+":"))
                    # print("+"*50)
                    
            return data
        except Exception as e:
            print(e)
            continue


@wrapper_calc_time(print_log=True)
def chat_test_data(chat_api, instruction, test_data):
    for data in test_data:
        data = chat_one_data(chat_api, instruction, data)
        
        with open(save_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False)+',\n')


def main():
    test_data = json.load(open(test_data_path, "r", encoding="utf-8"))
    instruction = open(instruction_path, 'r').read()

    if checkpoint_flag:
        lines = file_lines(save_path)
        test_data = test_data[lines:]

    if test_flag:
        test_data = test_data[:3]

    print(f"Test data length: {len(test_data)}")
    chat_api = ChatApi()
    chat_test_data(chat_api, instruction, test_data)


if __name__ == "__main__":
    checkpoint_flag = True # read the save_path,continue from the last checkpoint
    test_flag = True

    base_dir = 'data/sample/'
    filename = 'sample_100.json'

    instruction_path = base_dir+"instruction.txt"
    test_data_path = base_dir + filename
    save_path = base_dir+'sample_with_llm.json'

    main()

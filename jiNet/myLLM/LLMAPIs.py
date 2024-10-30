import os.path
from json import JSONDecodeError
import shutil

from bs4 import BeautifulSoup
try:
    from .picUnderstanding import get_result
except ImportError:
    from picUnderstanding import get_result
from pdf2image import convert_from_path

import requests
import json

class UnfoundFileError(BaseException):
    def __init__(self, message = "Unfound File", error_code = 1):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self):
        return f"[Error {self.error_code}]: {self.message}"

class jiLLM:
    def __init__(self):
        self.url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
        self.header = {
            "Authorization": "Bearer PUUDZpSeahQkkntuBDRm:TNChTOpFisAnmOiChuvQ"
        }


    def send_single_message(self, input_message:str):
        data = {"max_tokens": 4096, "top_k": 4, "temperature": 0.5, "messages": [
            {
                "role": "system",
                "content": "你是小锦，可以和用户聊天"
            },
            {
                "role": "user",
                "content": input_message
            }
        ], "model": "4.0Ultra", "stream": True}
        response = requests.post(self.url, headers=self.header, json=data, stream=True)
        returned_message = self.parse_response(response)
        print("")
        return returned_message

    def send_problem(self, input_message:str):
        ##这个版本的机器人更加理性
        data = {"max_tokens": 8192, "top_k": 4, "temperature": 0.2, "messages": [
            {
                "role": "system",
                "content": "你是数学高手，需要解决许多数学问题"
            },
            {
                "role": "user",
                "content": input_message
            }
        ], "model": "4.0Ultra", "stream": True}
        response = requests.post(self.url, headers=self.header, json=data, stream=True)
        returned_message = self.parse_response(response)
        print("")
        return returned_message

    def send_history(self,chatting_history:list):
        data = {"max_tokens": 4096, "top_k": 4, "temperature": 0.5, "messages": chatting_history, "model": "4.0Ultra", "stream": True}
        response = requests.post(self.url, headers=self.header, json=data, stream=True)
        returned_message = self.parse_response(response)
        print("")
        return returned_message

    def normal_chat(self):
        question = input("input you question:")
        print(self.send_single_message(question))

    def parse_response(self,response:requests.Response)->str:
        ans = ""
        response.encoding = "utf-8"
        for line in response.iter_lines(decode_unicode="utf-8"):
            try:
                lines = json.loads(line[6:].strip())
            except JSONDecodeError:
                continue
            if 'choices' in lines:
                choice = lines['choices'][0]
                if 'delta' in choice:
                    delta = choice['delta']
                    if 'content' in delta:
                        ans += delta['content']
        return ans

    def solve_math_problem(self,picUrl:str,outputType=1):
        ##outputType:1 -> 直接输出 2->输出文字
        OCRer = get_result()
        problem = OCRer.get_math_problem(picUrl)
        ans = self.send_problem(f"解决下列数学问题\n{problem}")
        print("Math Problem Solved!")
        if outputType == 1:
            self.latex_deal(ans)
            return ""
        else:
            return ans

    def solve_math_testpaper(self,pdfUrl:str):
        images_path = "test_pdf/math"
        picNums:int = self.split_pdf(pdfUrl,images_path)
        ans = ""
        for i in range(1,picNums+1):
            print(f"Now solving {images_path}/page_{i}.jpg")
            ans += self.solve_math_problem(f"{images_path}/page_{i}.jpg",2)
            ans += "\n"
        self.latex_deal(ans)

    def latex_deal(self, passage: str):
        if not os.path.isdir('output'):
            os.mkdir('output')
        shutil.copy('base.html', 'output/output.html')

        with open('output/output.html', 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        main_content = soup.find('p', {'id': 'mainContent'})
        if main_content:
            main_content.string = passage

        with open('output/output.html', 'w', encoding='utf-8') as file:
            file.write(str(soup))
        print("Latex input OK!")

    def split_pdf(self,input_pdf:str,output_folder):
        images = convert_from_path(input_pdf)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for i, image in enumerate(images):
            output_path = os.path.join(output_folder, f'page_{i + 1}.jpg')
            image.save(output_path, 'JPEG')
        return len(images)

    def save_chatting_history(self,chatting_history:list):
        save_path = os.path.dirname(__file__) + "/chat_history.json"
        with open(save_path,'w',encoding='utf-8') as json_file:
            json.dump(chatting_history,json_file)
            json_file.close()

    def load_chatting_history(self)->list:
        load_path = os.path.dirname(__file__) + "/chat_history.json"
        if not os.path.exists(load_path):
            raise UnfoundFileError
        with open(load_path,'r',encoding='utf-8') as json_file:
            load_data = json.load(json_file)
            json_file.close()
        return load_data

    def convert_history_to_string(self,history_llm:list):
        his = ""
        for dic in history_llm:
            role = dic["role"]
            message = dic["content"]
            if role == "system":
                continue
            elif role == "user":
                his += f'<p class="user">用户: {message} </p>'
            else:
                his += f'<p class="GPT">GPT: {message} </p>'
        return his

    def chat_with_history(self,input_message:str)->str:
        try:
            history = self.load_chatting_history()
        except UnfoundFileError:
            history = [
                {
                    "role": "system",
                    "content": "你是可爱学妹小锦，可以和用户聊天"
                }
            ]
        dic = {
            "role": "user",
            "content": input_message
        }
        history.append(dic)
        bot_message = self.send_history(history)
        print(bot_message)
        ans_dic = {
            "role": "assistant",
            "content": bot_message
        }
        history.append(ans_dic)
        self.save_chatting_history(history)
        return self.convert_history_to_string(history)

    def constant_chatting(self):
        history = [
            {
                "role": "system",
                "content": "你是可爱学妹小锦，可以和用户聊天"
            }
        ]

        while(True):
            input_message = input("用户(输入q退出):")
            if input_message == "q":
                break
            dic = {
                "role": "user",
                "content": input_message
            }
            history.append(dic)
            bot_message = self.send_history(history)
            print(bot_message)
            ans_dic = {
                "role": "assistant",
                "content": bot_message
            }
            history.append(ans_dic)

        self.save_chatting_history(history)

if __name__ == "__main__":
    llm = jiLLM()
    llm.constant_chatting()


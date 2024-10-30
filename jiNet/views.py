from django.shortcuts import render
from django.http import JsonResponse
from .myLLM.LLMAPIs import jiLLM, UnfoundFileError
import json

def index(request):
    context = {}
    return render(request,'index.html',context)

def llm(request):
    llm = jiLLM()
    try:
        history_llm = llm.load_chatting_history()
        his = llm.convert_history_to_string(history_llm)
    except UnfoundFileError:
        his = ""
    context = {"output":his}
    return render(request,'llm.html',context)


def process_input(request):
    if request.method == 'POST':
        input_message = json.loads(request.body).get('input_message')
        llm = jiLLM()
        answer = llm.chat_with_history(input_message)
        output = f"罗伯特说: {answer}"
        return JsonResponse({'output' : output})
    return JsonResponse({'error':'Invalid message!'},status=400)

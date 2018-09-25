from rundocker import build_and_run_submit
from encode import Encoder


def main():
    protos = [
        {
            "name": "SayHello",
            "type": "string",
            "args": [{"name": "who", "type": "string"}]
        }]
    job = {'code': """def SayHello(who)]:
    return "hello " + who
        """,
           'inputs': ['"Hien"', '"Paul"'],
           'prototype': protos[0]}
    result = build_and_run_submit(job)
    if result['result'] == 'compiler_error':
        print(result['error']['msg'])
        print(result['error']['text'])
        for i in range(result['error']['offset']-1):
            print(" ",end="")
        print("^")



if __name__ == "__main__":
    main()


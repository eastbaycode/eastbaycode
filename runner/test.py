from rundocker import build_and_run_submit
from encode import Encoder


def main():
    protos = [
        {
            "name": "SayHello",
            "type": "string",
            "args": [{"name": "who", "type": "string"}]
        }]
    job = {'code': """
def SayHello(who):
    return "hello " + who
        """,
           'inputs': ['"Hien"', '"Paul"'],
           'prototype': protos[0]}
    result = build_and_run_submit(job)
    print(result)



if __name__ == "__main__":
    main()


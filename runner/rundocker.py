import docker
import redis
import time
import json
from encode import *
from shutil import copyfile


def connection():
    conn = redis.Redis(host="eastbaycode_redis_1", port=6379, db=0)
    return conn

def build_and_run_submit(job):
    # create inputs and code files in docker2 directory
    result = {}
    encoder = Encoder(job['prototype'])

    # compile the code
    try:
        code_obj = compile(job['code'], 'code', 'exec')
    # catch a syntax error
    except SyntaxError as e:
        # return the error
        result['result'] = "compiler_error"
        compile_result={}
        compile_result['msg']= e
        compile_result['text']=e.text.strip()
        compile_result['offset']=e.offset
        compile_result['lineno'] = e.lineno
        result['error'] = compile_result
        return result

    code = encoder.make_program(job)
    with open('docker2/submission.py', 'w') as program:
        program.write(code)
    copyfile("encode.py", "docker2/encode.py")

    client = docker.from_env()
    #handles=client.containers.run("ubuntu:latest","./bbt train sol.py input.json output.json")
    handles=client.images.build(path="docker2",tag="latest")
    # print(handles)
    handles=client.containers.run("latest:latest", volumes = {"docker2":{"bind": "/code/output", "mode": "rw"}})
    result = handles.decode('utf-8')
    # print(handles)
    #input("fdfgbbgfgb")
    return result

def get_a_job(qname):
    conn = connection()
    result = conn.lpop(qname)
    if result != None:
        result = result.decode('utf-8')
        return result

def send_result(qname, msg):
    conn = connection()
    conn.rpush(qname, msg)

def main():
    while True:
        job = get_a_job(qname = "work")
        if job:
            job = json.loads(job)
            result = build_and_run_submit(job)
            send_result(qname="result", msg=result)
        else:
            time.sleep(10)
            print("No jobs anymore")


if __name__ == "__main__":
    main()

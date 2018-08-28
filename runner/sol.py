import sys
def main():
    
    
    name = sys.argv
    try:
       # print ("Hello ",name[1]," ")
       
       data = "Hello " + name[1]
       sys.stdout.write(data)
       sys.stdout.flush()
       
    except StopIteration:
        pass
    
    
    

if __name__ == '__main__':
    main()
    
import socket
import sys

def http_request(url):
    parts = url.split('/')
    host = parts[2]
    path = '/' + '/'.join(parts[3:])
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    s.connect((host, 80))
    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"
    s.send(request.encode())
    
    response = b''
    while True:
        data = s.recv(1024)
        if not data:
            break
        response += data
    
    s.close()
    print(response.decode())

def show_help():
    print("Usage: go2web [options]")
    print("Options:")
    print("  -u <URL>            Make an HTTP request to the specified URL and print the response")
    print("  -s <search-term>    Make an HTTP request to search the term using your favorite search engine and print top 10 results")
    print("  -h                  Show this help")

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] != '-h':
        print("Invalid usage. Use 'go2web -h' for help.")
        sys.exit(1)

    show_help()

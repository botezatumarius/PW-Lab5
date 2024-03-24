import socket
import sys
import argparse
from bs4 import BeautifulSoup, NavigableString
import ssl

def find_redirect_location(response):
    lines = response.split('\n')
    for line in lines:
        if line.startswith("Location:"):
            return line.split(": ", 1)[1].strip()
    return None

def print_strings_in_tags(soup):
    for tag in soup.body.descendants:
        if (tag.name!=None):
            if tag.has_attr('href'):
                print("\033[92m", tag['href'], "\033[97m")
            if (tag.string!=None):
                for e in tag.contents:
                    if(type(e) == NavigableString):
                        print("\033[97m", tag.string.strip(), "\033[97m")
                    if tag.has_attr('href'):
                        print("\033[92m", tag['href'], "\033[97m")

def https_request(url, sock):
    host = url.split('/', 3)[2]
    path = ""
    try:
        path = url.split('/', 3)[3]
    except:
        pass

    context = ssl.create_default_context()
    sock = socket.create_connection((host, 443))
    ssock = context.wrap_socket(sock, server_hostname=host)

    try:
        ssock.send(bytes(f"GET /{path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n", 'UTF-8'))

        response = b""
        while True:
            block = ssock.recv(4096)
            if not block:
                break
            response += block

    finally:
        ssock.close()
        sock.close()

    html_content = response.decode('UTF-8')
    
    status_code = html_content.split(' ',2)[1]
    
    if status_code.startswith("3"):  
        redirect_location = find_redirect_location(html_content)
        if redirect_location:
            print("Redirecting to:", redirect_location)
            return https_request(redirect_location, sock)  
        else:
            print("Error - Redirection location not found")
            return None
    elif status_code == "200":
        soup = BeautifulSoup(html_content, "html.parser")
        print_strings_in_tags(soup)

    else:
        print("Error - Received status:", status_code)
        return None

if __name__ == "__main__":
    if(len(sys.argv) == 1):
        print("No arguments have been passed. Check help with -h or --help")
        sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", help="Make an HTTP request to the specified URL and print the response")
    parser.add_argument("-s", help="Make an HTTP request to search the term using google and print top 10 results")
    args = parser.parse_args()

    if args.u:
        https_request(args.u,sock)


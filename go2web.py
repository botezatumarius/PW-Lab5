import socket
import sys
import argparse
from bs4 import BeautifulSoup, NavigableString
import ssl
import json

def load_cache(cache_file):
    try:
        with open(cache_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_cache(cache, cache_file):
    with open(cache_file, 'w') as file:
        json.dump(cache, file)

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

def https_request(url, sock, toPrint,cache,optionalKey='',secure=''):
    if 'https://' in url:
        secure = True
    host = url.split('/', 3)[2]
    path = ""
    try:
        path = url.split('/', 3)[3]
    except:
        pass
    
    ssock = None
    if secure:
        sock = socket.create_connection((host, 443))
        context = ssl.create_default_context()
        ssock = context.wrap_socket(sock, server_hostname=host)
    else:
        sock = socket.create_connection((host, 80))

    try:
        if secure:
            ssock.send(bytes(f"GET /{path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n", 'UTF-8'))
        else:
            sock.send(bytes(f"GET /{path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n", 'UTF-8'))
        response = b""

        if secure:
            while True:
                block = ssock.recv(4096)
                if not block:
                    break
                response += block
        else:
            while True:
                block = sock.recv(4096)
                if not block:
                    break
                response += block

    finally:
        if secure:
            ssock.close()
        sock.close()

    try:
        html_content = response.decode('UTF-8')
    except:
        html_content = response.decode('latin-1')
    
    status_code = html_content.split(' ',2)[1]
    
    if status_code.startswith("3"):  
        redirect_location = find_redirect_location(html_content)
        if redirect_location:
            print("Redirecting to:", redirect_location)
            https_request(redirect_location, sock,toPrint,cache,url,"true")  
        else:
            print("Error - Redirection location not found")
            return None
    elif status_code == "200":
        soup = BeautifulSoup(html_content, "html.parser")
        if optionalKey:
            cache[optionalKey] = html_content
        else:
            cache[url] = html_content
        save_cache(cache,"cache.json")
        if toPrint:
            print_strings_in_tags(soup)
        return soup
    else:
        print("Error - Received status:", status_code)
        return None
    
def lookUp(list,sock,cache):
    searchTerm = ""
    for word in list:
        searchTerm += word + '+'
    searchTerm = searchTerm[:-1]
    url = f"https://www.google.com/search?q={searchTerm}"
    if cache.get(url) is None:
        soup = https_request(url,sock,0,cache)
    else:
        soup = BeautifulSoup(cache.get(url), "html.parser")
        print("\033[93mTerm exists in cache!\033[0m")
    
    for h3_tag in soup.find_all('h3'):
        title = h3_tag.getText()
        print("\033[92m", title, "\033[97m")
        
        parent_anchor = h3_tag.find_parent('a')
        if parent_anchor:
            addr = parent_anchor.get('href')
            if addr:
                addr = addr.split("?q=")[-1].split('&')[0]
                print("\033[94m", addr, "\033[97m")


if __name__ == "__main__":
    if(len(sys.argv) == 1):
        print("No arguments have been passed. Check help with -h or --help")
        sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    parser = argparse.ArgumentParser()
    parser.add_argument("-u",nargs=1, help="Make an HTTP request to the specified URL and print the response")
    parser.add_argument("-s",nargs='+', help="Make an HTTP request to search the term using google and print top 10 results")
    args = parser.parse_args()

    cache_file = "cache.json"
    cache = load_cache(cache_file)
    if (args.u and cache.get(args.u[0]) is None):
        https_request(args.u[0],sock,1,cache)
    elif (args.u and cache.get(args.u[0]) is not None):
        print("\033[93mURL exists in cache!\033[0m")
        cachedResponse = cache.get(args.u[0])
        soup = BeautifulSoup(cachedResponse, "html.parser")
        print_strings_in_tags(soup)
    elif args.s:
        lookUp(args.s,sock,cache)

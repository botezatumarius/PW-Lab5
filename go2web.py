import sys

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

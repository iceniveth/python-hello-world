import requests
import json

def main():
    response = requests.get("https://dummyjson.com/products/1")
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    main()

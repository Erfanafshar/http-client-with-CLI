import getopt
import re
import sys
import requests
import json
import os

if len(sys.argv) == 0:
    print("Error")
    print("url didn't entered")
    sys.exit(1)

url = sys.argv[1]
method = "GET"
headers = {}
queries = {}
data = ""
json_data = ""
file_path = ""
timeout = 1e6
file_name = "name"

#       -1: not set yet           0: set by data or json or file            1: set by header
content_type_status = -1

#       -1: not set yet         0: data             1: json                2: file
body_type = -1

#       False: download file in system then open it         True: dumb body of responses in console
dumb_in_console = False


def validate_url():
    regex = r"^(http|https|ftp):\/{2}(.+(:.+)?@)?([\w-]+\.)+[\w]+(:\d+)?((/.+)*|/)(\?.*)?(#.*)?$"
    match = re.match(regex, url)
    if match is None:
        print("Not a valid URL")
        sys.exit(1)


def validate_method(method_func):
    methods_list = ["GET", "POST", "PATCH", "DELETE", "PUT"]
    if method_func in methods_list:
        return True
    return False


def method_handle(method_func):
    global method
    valid_method = validate_method(method_func)
    if not valid_method:
        print("Method is not valid")
        sys.exit(1)
    method = method_func


def insert_header(key, value):
    global content_type_status
    if key == "content_type":
        if content_type_status == 0:
            print("header Warning!")
            print("overriding value of", key, "(set by body)")
            print("last value :", headers[key])
            print("new value :", value)
            print()
        elif content_type_status == 1:
            print("header Warning!")
            print("overriding value of", key, "(set by header)")
            print("last value :", headers[key])
            print("new value :", value)
            print()

        headers[key] = value
        content_type_status = 1
    else:
        if key in headers.keys():
            print("header Warning!")
            print("overriding value of", key)
            print("last value :", headers[key])
            print("new value :", value)
            print()
            headers[key] = value
        else:
            headers[key] = value


def header_handle(header_str):
    new_headers = header_str.split(",")
    for n_head in new_headers:
        pair = n_head.split(":")
        key = pair[0].lower()
        value = pair[1]
        insert_header(key, value)


def query_handle(query_str):
    new_queries = query_str.split("&")
    for n_query in new_queries:
        pair = n_query.split("=")
        key = pair[0].lower()
        value = pair[1]
        if key in queries.keys():
            print("query Warning!")
            print("overriding value of", key)
            print("last value :", headers[key])
            print("new value :", value)
            print()
            queries[key] = value
        else:
            queries[key] = value


def validate_data(data_func):
    regex = r"^([^=&]+=[^=&]+&)*[^=&]+=[^=&]+$"
    match = re.match(regex, data_func)

    if match is None:
        print("data Warning!")
        print("your data is not in application/x-www-form-urlencoded format")
        print()


def data_handle(data_func):
    global data
    global content_type_status
    global body_type
    validate_data(data_func)

    if "content-type" in headers.keys():
        print("data Warning!")
        print("overriding value of content-type")
        print("default value by data : application/x-www-form-urlencoded")
        print("overridden value by header :", headers["content-type"])
        print()
    else:
        headers["content_type"] = "application/x-www-form-urlencoded"
        content_type_status = 0
    data = data_func

    if body_type != -1:
        if body_type == 0:
            print("data Warning!")
            print("overriding value of body")
            print("previous value set by data")
            print("new value set by data")
            print()
        elif body_type == 1:
            print("data Warning!")
            print("overriding value of body")
            print("previous value set by json")
            print("new value set by data")
            print()
        elif body_type == 2:
            print("data Warning!")
            print("overriding value of body")
            print("previous value set by file")
            print("new value set by data")
            print()
    body_type = 0


def validate_json(data_func):
    try:
        json.loads(data_func)
    except ValueError:
        print("json Warning!")
        print("your data is not in application/json format")
        print()


def json_handle(json_func):
    global json_data
    global content_type_status
    global body_type
    validate_json(json_func)

    if "content-type" in headers.keys():
        print("json Warning!")
        print("overriding value of content-type")
        print("default value by json : application/json")
        print("overridden value by header :", headers["content-type"])
        print()
    else:
        headers["content_type"] = "application/json"
        content_type_status = 0
    json_data = json_func

    if body_type != -1:
        if body_type == 0:
            print("json Warning!")
            print("overriding value of body")
            print("previous value set by data")
            print("new value set by json")
            print()
        elif body_type == 1:
            print("json Warning!")
            print("overriding value of body")
            print("previous value set by json")
            print("new value set by json")
            print()
        elif body_type == 2:
            print("json Warning!")
            print("overriding value of body")
            print("previous value set by file")
            print("new value set by json")
            print()
    body_type = 1


def file_handle(path):
    global file_path
    global content_type_status
    global body_type
    if "content-type" in headers.keys():
        print("file Warning!")
        print("overriding value of content-type")
        print("default value by file : application/octet-stream")
        print("overridden value by header :", headers["content-type"])
        print()
    else:
        headers["content_type"] = "application/octet-stream"
        content_type_status = 0
    file_path = path

    if body_type != -1:
        if body_type == 0:
            print("file Warning!")
            print("overriding value of body")
            print("previous value set by data")
            print("new value set by file")
            print()
        elif body_type == 1:
            print("file Warning!")
            print("overriding value of body")
            print("previous value set by json")
            print("new value set by file")
            print()
        elif body_type == 2:
            print("file Warning!")
            print("overriding value of body")
            print("previous value set by file")
            print("new value set by file")
            print()
    body_type = 2


def timeout_handle(timeout_func):
    global timeout
    timeout = float(timeout_func)


def config_arguments():
    argument_list = sys.argv[2:]
    options = "M:H:Q:D:J:F:T:"
    long_options = ["method=", "headers=", "queries=", "data=", "json=", "file=", "timeout="]
    return argument_list, options, long_options


def set_headers():
    argument_list, options, long_options = config_arguments()

    try:
        arguments, values = getopt.getopt(argument_list, options, long_options)

        for currentArgument, currentValue in arguments:
            if currentArgument in ("-M", "--method"):
                method_handle(currentValue)

            elif currentArgument in ("-H", "--headers"):
                header_handle(currentValue)

            elif currentArgument in ("-Q", "--queries"):
                query_handle(currentValue)

            elif currentArgument in ("-D", "--data"):
                data_handle(currentValue)

            elif currentArgument in ("-J", "--json"):
                json_handle(currentValue)

            elif currentArgument in ("-F", "--file"):
                file_handle(currentValue)

            elif currentArgument in ("-T", "--timeout"):
                timeout_handle(currentValue)

    except getopt.error as err:
        print(str(err))


def prepare_request():
    validate_url()
    set_headers()


def print_response_header(response_func):
    print("request")
    print(response_func.request.method, end=" ")
    print(response_func.request.path_url, end=" ")
    print("HTTP/" + str(response_func.raw.version / 10))
    if "user-agent" in response_func.request.headers:
        print("User-Agent: " + response_func.request.headers["user-agent"])
    print("Host: " + response_func.request.url[:-len(response_func.request.path_url)])
    if "accept-language" in response_func.request.headers:
        print("Accept-Language: " + response_func.request.headers["accept-language"])
    if "accept-encoding" in response_func.request.headers:
        print("Accept-Encoding: " + response_func.request.headers["accept-encoding"])
    if "connection" in response_func.request.headers:
        print("Connection: " + response_func.request.headers["connection"])

    print()
    print("response")
    print("HTTP/" + str(response_func.raw.version / 10), end=" ")
    print(response_func.status_code, end=" ")
    print(response_func.reason)
    if "Date" in response_func.headers:
        print("Date: " + response_func.headers["Date"])
    if "Server" in response_func.headers:
        print("Server: " + response_func.headers["Server"])
    if "Content-Length" in response_func.headers:
        print("Content-Length: " + response_func.headers["Content-Length"])
    if "Content-Type" in response_func.headers:
        print("Content-Type: " + response_func.headers["Content-Type"])
    if "Connection" in response_func.headers:
        print("Connection: " + response_func.headers["Connection"])

    print()
    print("all response headers")
    for item in response_func.headers.keys():
        print(item + ": " + response_func.headers[item])
    print()


def print_response_body(response_func):
    print("dumb response body")
    print(response_func.text)


def open_file(response):
    if "Content-Type" in response.headers:
        if response.headers["Content-type"] == "application/pdf":
            os.rename(file_name + ".txt", file_name + ".pdf")
            os.system(file_name + ".pdf")
        elif response.headers["Content-type"] == "image/jpeg":
            os.rename(file_name + ".txt", file_name + ".jpg")
            os.system(file_name + ".jpg")
        elif response.headers["Content-type"] == "image/png":
            os.rename(file_name + ".txt", file_name + ".png")
            os.system(file_name + ".png")
        elif response.headers["Content-type"] == "video/mp4":
            os.rename(file_name + ".txt", file_name + ".mp4")
            os.system(file_name + ".mp4")
        else:
            os.system(file_name + ".txt")


def get_exec():
    with open(file_name + ".txt", "wb") as f:
        print("Download is starting")
        try:
            response = requests.get(url, params=queries, headers=headers, timeout=timeout, stream=True)
        except requests.exceptions.Timeout:
            print("Error")
            print("timeout occurred")
            sys.exit(1)
        except requests.exceptions.RequestException:
            print("Error")
            print("problem occurred during your request processing")
            sys.exit(1)

        total_length = response.headers.get('content-length')

        if total_length is None:
            f.write(response.content)
        else:
            current_length = 0
            total_length = int(total_length)
            for dt in response.iter_content(chunk_size=4096):
                current_length += len(dt)
                f.write(dt)
                done = int(50 * current_length / total_length)
                sys.stdout.write("\r[%s%s]" % ('*' * done, ' ' * (50 - done)))

    print()
    print_response_header(response)
    if dumb_in_console:
        print_response_body(response)
    else:
        open_file(response)


def method_exec(method_func, body_func):
    try:
        if method_func == "POST":
            response = requests.post(url, data=body_func, headers=headers, timeout=timeout)
        elif method_func == "PATCH":
            response = requests.patch(url, data=body_func, headers=headers, timeout=timeout)
        elif method_func == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout)
        elif method_func == "PUT":
            response = requests.put(url, data=body_func, headers=headers, timeout=timeout)
        else:
            print("Error")
            print("invalid method")
            sys.exit(1)
        return response

    except requests.exceptions.Timeout:
        print("Error")
        print("timeout occurred")
        sys.exit(1)
    except requests.exceptions.RequestException:
        print("Error")
        print("problem occurred during your request processing")
        sys.exit(1)


def get_body():
    if body_type == -1:
        body = ""
        print("Warning")
        print("No data specified ")
    elif body_type == 0:
        body = data
    elif body_type == 1:
        body = json_data
    elif body_type == 2:
        try:
            body = open(file_path, "rb")
        except IOError:
            print("Error")
            print("specified file doesn't found")
            sys.exit(1)

    else:
        print("Error! ")
        print("Invalid body-type number")
        sys.exit(1)
    return body


def post_exec():
    body = get_body()
    response = method_exec("POST", body)
    print_response_header(response)
    print_response_body(response)


def patch_exec():
    body = get_body()
    response = method_exec("PATCH", body)
    print_response_header(response)
    print_response_body(response)


def delete_exec():
    response = method_exec("DELETE", None)
    print_response_header(response)
    print_response_body(response)


def put_exec():
    body = get_body()
    response = method_exec("PUT", body)
    print_response_header(response)
    print_response_body(response)


def execute_request():
    if method == "GET":
        get_exec()
    elif method == "POST":
        post_exec()
    elif method == "PATCH":
        patch_exec()
    elif method == "DELETE":
        delete_exec()
    elif method == "PUT":
        put_exec()
    else:
        print("Error")
        print("invalid method")
        sys.exit(1)


def main():
    prepare_request()
    execute_request()


if __name__ == "__main__":
    main()

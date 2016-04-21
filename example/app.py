from puck import Puck, api_response, request


app = Puck()


@app.before_request
def print_hello():
    print 'Before_request is running!'


@app.after_request
def after_resp(response):
    print 'After_request is running!'
    return response


@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'GET':
        return api_response(
            data={
                'test': 'hello world!'
            }
        )
    elif request.method == 'POST':
        file = request.file[0][1]
        file.create('/Users/Eric/hahahaha.md')
        return request.file


@app.route('/<name>')
def hello_name(name):
    return 'hello, %s' % name


if __name__ == '__main__':
    app.run()

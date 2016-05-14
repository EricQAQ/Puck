from puck import Puck, api_response, request, session


app = Puck(redis_host='127.0.0.1', redis_port=6379)


@app.after_request
def after(response):
    response.set_cookies('heihei', 'this is a test!', expires=2000000111)
    return response


@app.route('/', methods=['GET'])
def index():
    session['haha'] = 'asdfasdf'
    return api_response(data=session.data, message='this is the session.')


if __name__ == '__main__':
    app.run()

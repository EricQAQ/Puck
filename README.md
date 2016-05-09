# Puck

![pic](https://github.com/EricQAQ/Puck/blob/master/docs/Puck.png)

Puck is a micro web framework for developers to build restful api quickly.

## Quickly Use

### 1. Hello world

It is easy to use Puck to build web api, just need 14 lines you can building a hello world api!

```python
from puck import Puck, api_response, request

app = Puck()

@app.route('/', methods=['GET'])
def hello():
    return api_response(
        data={
            'test': 'hello world!'
        }
    )

if __name__ == '__main__':
    app.run()
```

### 2. Dynamic router

In Puck, it support *three types* in Dynamic router: int, string, float.
You can build a dynamic router like this:

```python
@app.route('/<str:name>')
def hello_name(name):
    return 'hello, %s' % name
```
and this:

```python
@app.route('/<int:age>/<int:salary>')
def hello_file(age, salary):
    return 'hello, visiter. Your age is %s, salary is %s' % (age, salary)
```

### 3. Before and After handling

If you want to do something before Puck handling the client's request, do it like this:


```python
@app.before_request
def print_hello():
    print 'Before_request is running!'
```

So, when the request is coming, 'Before_request is running!' will print out.


If you want to do something after Puck handling the client's request, do it like this:

```python
@app.after_request
def after_resp(response):
    print 'After_request is running!'
    return response
```
The param `response` is necessary~

### 4. Session
Puck support Redis to store the session. SO PLEASE BE SURE TO INSTALL REDIS before starting Puck's app.

Currently, the default redis host is `127.0.0.1`, port is `6379`, if you do not use this, you can build app like this:

```python
from puck import Puck, api_response, request, session

app = Puck(redis_host='127.0.0.1', redis_port=6379)

@app.route('/', methods=['GET'])
def index():
    return api_response(data=session.data, message='this is the session.')

if __name__ == '__main__':
    app.run()
```

### 5. Requst, session and so on

Puck's context uses the trickly in Flask, you can directly get request object like this:

```python
from puck import request
```
and session:

```python
from puck import session
```
and current app:

```python
from puck import current_app
```

In request, you can:

1. get cookies like this: `request.cookies`, 
2. get request method like this: `request.method`
3. get header like this: `request.header`
4. get request address like this `request.request_addr`
5. get content type like this `request.content_type`
6. get request form like this `request.form`
7. get upload file like this `request.file`

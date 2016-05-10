# Puck
[![Puck](https://img.shields.io/badge/Puck-v0.1.2-orange.svg)]()

![pic](https://github.com/EricQAQ/Puck/blob/master/docs/Puck.jpg)

Puck is a micro web framework for developers to build restful api quickly.


## why Puck?

1. brief code to build restful api
2. easy to learn and to use
3. focus on restful web api, easy to return JSON object
4. router system is convenient, support dynamic router
5. Default use Redis to store session

## Before use Puck

1. install Redis and start it.

    ```
    wget http://download.redis.io/redis-stable.tar.gz
    tar xvzf redis-stable.tar.gz
    cd redis-stable
    make
    ```
    if you uses mac OSX, you can install like this:

    ```
    brew install redis
    ```

    start it:

    ```
    $ redis-server
    ```
2. install puck

    you can use pip to install it:

    ```
    $ pip install puck
    ```

    or you can install from source code:

    ```
    $ git clone https://github.com/EricQAQ/Puck
    $ cd Puck
    $ python setup.py install
    ```

## How to use

The tutorial is [here](https://github.com/EricQAQ/Puck/wiki/Quickly-Start)

If you think Puck is good, Plz START~~ :relaxed::relaxed:

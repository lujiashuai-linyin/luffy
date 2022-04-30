from mycelery.main import app

@app.task(name="send_mail")
def send_mail():
    print('hello, mail')
    return "hello. mail!!!!"
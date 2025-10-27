from flask import request, jsonify, render_template_string
import flask
import subprocess

app = flask.Flask(__name__)

page = """
<!doctype html>
<html>
<head>
    <title>TUMRouter - Diagnostics</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='pico.slim.min.css') }}">
    <meta charset="UTF-8">
</head>
<body>
<main class="container">
<header>
<h1><img src="/static/tum.svg" style="height:0.8em; position:relative; top:-3px"> Router - Diagnostics</h1>
</header>
<section>
Enter an IP address or a domain name below to ping it with the <code>ping</code> command.
</section>

<form enctype="application/x-www-form-urlencoded" onsubmit="onSubmit(event)">
<div>
<div>
IP Address/Domain Name: <input type="text" name="ip">
</div>
<div>
<input type="submit" value="Send Ping">
</div>
</form>

<section>
<h5>Ping Result</h5>
<textarea id="result" style="width: 100%; height: 200px"></textarea>
</section>
</main>
<script>
let output = document.querySelector("#result");
function onSubmit(event) {
let ip = event.target.querySelector("input[name='ip']").value;
let resp = fetch(`/api?ip=${ip}`).then((resp) => resp.json()).then((resp) => {
output.value = resp.output;
});
event.preventDefault();
}
</script>
</body>
</html>
"""

@app.route("/")
def main():
    return render_template_string(page)

@app.route("/api")
def command_api():
    answer = {"output": ""}
    if ip := request.args.get("ip"):
        cmd = f"LANG= ping -c 1 '{ip}'"
        print("We will execute the following command:", cmd)
        if any(x in ip for x in ["'", "`", ";", "\\"]):
            answer["output"] = "Hacking attempt detected! You shall not pass!"
        else:
            answer["output"] = subprocess.run(f'LANG= ping -c 1 "{ip}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
        print(answer)
    return jsonify(answer)

if __name__ == "__main__":
    app.run()

import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.escape
import requests
import json

GITHUB_TOKEN = "github_api_xxx"  # Replace with your GitHub Personal Access Token
REPO = "owner/repo"  # Replace with your GitHub repository, e.g., "octocat/Hello-World"


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # Fetch issues from GitHub
        url = f"https://api.github.com/repos/{REPO}/issues"
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        response = requests.get(url, headers=headers)
        print(response.json())
        if response.status_code == 200:
            issues = response.json()
            print("issue type : ", type(issues))
            self.render(
                "index.html",
                issues=issues,
            )
        else:
            self.set_status(response.status_code)
            self.write(f"Error fetching issues: {response.text}")


class CreateIssueHandler(tornado.web.RequestHandler):
    def post(self):
        # Extract data from the request body
        try:
            data = tornado.escape.json_decode(self.request.body)
            title = data.get("title")
            body = data.get("body", "")
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"error": "Invalid JSON payload"})
            return

        # Create a new GitHub issue
        url = f"https://api.github.com/repos/{REPO}/issues"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        payload = {"title": title, "body": body}

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            self.write(response.json())
        else:
            self.set_status(response.status_code)
            self.write({"error": response.text})


def make_app():
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/api/issues", CreateIssueHandler),
        ],
        template_path="templates",  # Folder for HTML files
    )


if __name__ == "__main__":
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(8888)
    print("Server started at http://127.0.0.1:8888")
    tornado.ioloop.IOLoop.current().start()

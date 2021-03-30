import time
import json
import os
import urllib3

token = os.environ["INPUT_TOKEN"]
artifact_name = os.environ["INPUT_ARTIFACT_NAME"]
repo = os.getenv("INPUT_REPO") or os.getenv("GITHUB_REPOSITORY")
wait_seconds = int(os.getenv("INPUT_WAIT_SECONDS") or "5")
wait_sleep = 0.5

artifacts_url = f"https://api.github.com/repos/{repo}/actions/artifacts"
headers = {
    "Authorization": f"token {token}",
    "User-Agent": "Python",
}

http = urllib3.PoolManager()


def get_artifact(name):
    print(f"Download `{name}` from: {artifacts_url}")

    t_started = time.time()
    waiting = True
    etag = None

    while waiting:
        if etag:
            r = http.request(
                "GET", artifacts_url, headers={**headers, "If-None-Match": etag}
            )
        else:
            r = http.request("GET", artifacts_url, headers=headers)
            etag = r.headers.get("etag")

        data = json.loads(r.data.decode("utf-8"))
        for artifact in data["artifacts"]:
            print("Check artifact", artifact["name"])
            if artifact["name"] == name:
                return artifact

        waiting = time.time() - t_started < wait_seconds
        time.sleep(wait_sleep)


def download_artifact(name):
    artifact = get_artifact(name)
    if artifact is None:
        print(f"::set-output name=error::Artifact not found: {name}")

    r = http.request("GET", artifact["archive_download_url"], headers=headers)
    with open(artifact["name"], "wb") as f:
        f.write(r.data)
        print(f"::set-output name=success::Artifact downloaded: {artifact['name']}")


if __name__ == "__main__":
    download_artifact(artifact_name)

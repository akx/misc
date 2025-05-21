import argparse
import json
import urllib.request
import html.parser


class SimplePageHTMLParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.current = dict(attrs)
            self.links.append(self.current)

    def handle_endtag(self, tag):
        if tag == "a":
            self.current = None

    def handle_data(self, data):
        if self.current:
            self.current["_content"] = self.current.get("_content", "") + data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("package")
    ap.add_argument("--index-url", default="https://pypi.org/")
    args = ap.parse_args()
    package = args.package
    simple_url = f"{args.index_url.rstrip('/')}/simple/{package}/"
    resp = urllib.request.urlopen(simple_url)
    if resp.status != 200:
        raise RuntimeError(f"Failed to fetch {simple_url}: {resp.status}")
    data = resp.read()
    parser = SimplePageHTMLParser()
    parser.feed(data.decode("utf-8"))
    versions = set()
    for link in parser.links:
        pkg, version, *rest = link["_content"].strip().split("-")  # Might be incorrect.
        version = version.removesuffix(".tar.gz")
        version = version.removesuffix(".whl")
        version = version.removesuffix(".zip")
        version = version.removesuffix(".win32.exe")
        versions.add(version)
    print(json.dumps(list(versions)))


if __name__ == "__main__":
    main()

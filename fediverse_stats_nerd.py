import urllib.robotparser
import requests
import datetime
import json
from pathlib import Path
import http


class Downloader:
    useragent = "FediverseStatsNerd/0.1"

    def check_robots(self, url: str) -> bool:
        """Check if the robots.txt file allows us to download the stats."""
        try:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{url}/robots.txt")
            rp.read()
            flag = rp.can_fetch(self.useragent, f"{url}/.well-known/nodeinfo")
            return flag
        except (http.client.RemoteDisconnected, urllib.error.URLError):
            return False

    def download(self, url: str, flag: str) -> dict | None:
        """Download the stats from the given url if robots consent."""
        if flag is False:
            return None

        # Download the stats
        # ...
        session = requests.Session()
        session.headers.update({"User-Agent": self.useragent})

        r = session.get(f"{url}/.well-known/nodeinfo")
        if r.status_code != 200:
            return None
        r2 = session.get(r.json()["links"][0]["href"])
        if r2.status_code != 200:
            return None

        return r2.json()

    def elaborate_stats(self, data: dict, sitename: str) -> dict:
        if data is None:
            return None
        data_tmp = {}
        if data.get("usage") is not None:
            stats = {}
            stats["users"] = data["usage"]["users"].get("total", None)
            stats["users_month"] = data["usage"]["users"].get("activeMonth", None)
            stats["users_half_year"] = data["usage"]["users"].get("activeHalfyear", None)
            data_tmp['stats'] = stats

        if data.get("software") is not None:
            data_tmp["software"] = data["software"].get("name", None)
            data_tmp["software_version"] = data["software"].get("version", None)

        data_tmp["site"] = sitename

        return data_tmp

    def get_stats(self, url: str) -> dict | None:
        """Get the stats from the given url."""
        site_name = url
        if "http" not in url:
            url = "https://" + url
        flag = self.check_robots(url)
        data = self.download(url, flag)
        return self.elaborate_stats(data, site_name)


if __name__ == "__main__":
    # Read the list of instances
    d = Downloader()
    today_s = datetime.datetime.today().strftime('%Y-%m-%d')
    output = {"date_download": today_s, "data": []}
    i = 0
    with open("instances.txt") as f:
        instances = f.read().splitlines()
        for instance in instances:
            stats = d.get_stats(instance)
            i += 1
            print("---")
            print(f"{i}/{len(instances)}")
            if stats is not None:
                print(f"{stats['site']}")
                Path(f"data/{today_s}").mkdir(parents=True, exist_ok=True)
                filename = stats["site"].split(" ")[0].replace(".", "_")
                with open(f"data/{today_s}/{filename}.json", "w") as f:
                    f.write(json.dumps(stats))
                output["data"].append(stats)

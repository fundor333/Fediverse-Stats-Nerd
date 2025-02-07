import urllib.robotparser


class Downloader:
    useragent = "FediverseStatsNerd/0.1"

    def check_robots(self, url: str) -> bool:
        """Check if the robots.txt file allows us to download the stats."""
        rp = urllib.robotparser.RobotFileParser()
        flag = rp.can_fetch(self.useragent, f"{url}/.well-known/nodeinfo")
        return flag

import json
import urllib.request
from datetime import datetime

from mitmproxy import proxy, options, ctx
from mitmproxy.tools.dump import DumpMaster


class InterceptVeryFitDataUpload:
    def __init__(self):
        pass

    def request(self, flow):
        ctx.log.info(flow.request.pretty_host)
        if flow.request.pretty_url == "http://veryfitproapi.veryfitplus.com//user/uploadDBFile":
            ctx.log.info("very fit data upload")
            db = flow.request.multipart_form.get(b"db")
            filename = f"veryfit-{datetime.now().isoformat().replace(':', '-')}.zip"
            with open(filename, "wb") as f:
                f.write(db)
        # Attempt at blocking youtube ads, failed.
        # if re.match(r"^r[0123456789]+((-{3})|(.))sn-.{8}.googlevideo.com$", flow.request.pretty_host):
        #    flow.kill()

    def response(self, flow):
        ctx.log.info(flow.request.pretty_host)
        if flow.request.pretty_url == "http://veryfitproapi.veryfitplus.com//user/uploadDBFile":
            ctx.log.info("very fit data response")
            zip_url = json.loads(flow.response.content.decode())["data"]
            filename = f"veryfit-{datetime.now().isoformat().replace(':', '-')}-resp.zip"
            urllib.request.urlretrieve(zip_url, filename)


opts = options.Options(listen_host='0.0.0.0', listen_port=9097)
pconf = proxy.config.ProxyConfig(opts)

m = DumpMaster(opts)
m.server = proxy.server.ProxyServer(pconf)
m.addons.add(InterceptVeryFitDataUpload())

try:
    m.run()
except KeyboardInterrupt:
    m.shutdown()

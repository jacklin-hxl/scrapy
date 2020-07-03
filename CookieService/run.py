from server import CookiesServer
import settings
from services.zhihu import ZhihuLoginService

srv = CookiesServer(settings)
srv.register(ZhihuLoginService)
print("start cookie service")
srv.start()

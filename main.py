# Импорт встроенной библиотеки для работы веб-сервера
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# Для начала определим настройки запуска
hostName = "localhost"  # Адрес для доступа по сети
serverPort = 8080  # Порт для доступа по сети


class MyServer(BaseHTTPRequestHandler):
    """
    Специальный класс, который отвечает за
    обработку входящих запросов от клиентов
    """

    def do_GET(self):
        """
        Метод для обработки входящих GET-запросов
        """

        # self.send_response(200)  # Отправка кода ответа
        # self.send_header("Content-type", "text/html")  # Отправка типа данных, который будет передаваться
        # self.end_headers()  # Завершение формирования заголовков ответа

        # Если браузер запрашивает CSS
        if self.path == "/my_con.css":
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            # Указываем путь к файлу внутри папки static
            file_path = os.path.join("catalog/static", "my_con.css")
            with open(file_path, "rb") as file:
                self.wfile.write(file.read())

        # Если браузер запрашивает главную страницу
        elif self.path == "/" or self.path == "/contacts":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            # Указываем путь к HTML внутри папки templates
            file_path = os.path.join("catalog/templates", "contacts.html")
            with open(file_path, "r", encoding="utf-8") as file:
                html_content = file.read()
            self.wfile.write(bytes(html_content, "utf-8"))

        else:
            self.send_error(404, "Page Not Found")


if __name__ == "__main__":
    # Инициализация веб-сервера, который будет по заданным параметрах в сети
    # принимать запросы и отправлять их на обработку специальному классу, который был описан выше
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print(f"Server started http://{hostName}:{serverPort}")

    try:
        # Cтарт веб-сервера в бесконечном цикле прослушивания входящих запросов
        webServer.serve_forever()
    except KeyboardInterrupt:
        # Корректный способ остановить сервер в консоли через сочетание клавиш Ctrl + C
        pass

    # Корректная остановка веб-сервера, чтобы он освободил адрес и порт в сети, которые занимал
    webServer.server_close()
    print("Server stopped.")

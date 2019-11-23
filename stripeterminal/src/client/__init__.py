import http.server
import os
import subprocess
from selenium import webdriver

def run(host, port):
    js_client_dir = os.path.dirname(os.path.abspath(__file__))    
    subprocess.Popen(
            [
            "python", "-m", "http.server",
            f"{port}", "--bind", f"{host}",
            "--directory", js_client_dir
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(
        "/usr/local/bin/chromedriver",
        options=options
        )
    driver.get(f"{host}:{port}")
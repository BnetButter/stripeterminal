from distutils.core import setup

setup(
    name="stripeterminal",
    packages=["stripeterminal"],
    version="0.1",
    license="GPL v3",
    description="Access Stripe's JavaScript terminal SDK from python",
    author="Kevin Lai",
    author_email="kevinlai31@gmail.com",
    url="https://github.com/bnetbutter/stripeterminal",
    download_url="https://github.com/bnetbutter/stripeterminal/v_01.tar.gz",
    install_requires=[
        "selenium",
        "websockets",
        "stripe",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
    ]
)
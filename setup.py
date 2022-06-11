import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="spotifython",
    version="0.1.0",
    author="VAWVAW",
    author_email="vawvaw@vaw-valentin.de",
    description="An async caching python interface to readonly parts of the spotify api.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/vawvaw/spotifython",
    project_urls={
        "Bug Tracker": "https://github.com/vawvaw/spotifython/issues",
    },
    license="GPLv3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: aiohttp",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        "Typing :: Typed",
    ],
    package_dir={"": "spotifython"},
    packages=setuptools.find_packages(where="spotifython"),
    install_requires=requirements,
    python_requires=">=3.10",
)
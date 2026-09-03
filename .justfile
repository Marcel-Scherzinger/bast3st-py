watch-docs:
    sphinx-autobuild docs/source docs/build/html --open-browser --watch src --watch docs/source --delay 2

docs:
    cd docs && make clean html
    xdg-open docs/build/html/index.html

watch-docs:
    sphinx-autobuild docs/source docs/build/html --open-browser --watch src --watch docs/source --delay 2

docs:
    cd docs && make clean html

examples:
    make clean examples

examples: examples/compare.json examples/fixed_loop.json examples/hello.json examples/compare-with-catch.json

examples/%.json: examples/%.py
	uv run $<

clean:
	rm examples/*.json -f


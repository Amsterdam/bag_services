.PHONY: test
test:
	pytest --reuse-db -v .

.PHONY: test
retest:
	pytest --reuse-db -vs --lf .

.PHONY: coverage
coverage:
	py.test --reuse-db --cov --cov-report=term-missing --cov-report=html

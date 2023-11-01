test:
	coverage run -m pytest

report:
	coverage report -m

html:
	coverage html

new:
	poetry run new

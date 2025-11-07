pre-commit:
	pre-commit run --all-files

new-release:
	twine upload dist/*
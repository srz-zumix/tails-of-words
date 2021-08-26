#
# Makefile

defaut: help

help: ## Display this help screen
	@grep -E '^[a-zA-Z][a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sed -e 's/^GNUmakefile://' | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: tails_of_words/*.py ## install self
	python setup.py install


docker-alpine:
	docker run -it --rm -v ${PWD}:/work -w /work python:3.8-alpine sh
	# apk add make

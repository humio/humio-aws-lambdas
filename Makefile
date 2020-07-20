build: setup clean target requirements function teardown

setup:
	set -eo pipefail

clean:
	rm -f target/humio-aws-lambdas.zip
	rm -rf target

target:
	mkdir target
	mkdir package

requirements:
	(cd function && pip3 install --target ../package/python -r requirements.txt)

function:
	(cd function && zip ../target/humio-aws-lambdas.zip * )
	(cd package/python && zip -r9 ../../target/humio-aws-lambdas.zip .)

teardown:
	rm -rf package

.PHONY: build setup clean target requirements function teardown

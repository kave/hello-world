image_name := hello-world
gitsha := $(shell git rev-parse HEAD)

define build_image
docker build . \
	--tag $(image_name):latest
docker tag $(image_name):latest etapau/hello-world:latest
endef

define docker_run
docker run \
	-p 9000:9000 $(image_name):latest
endef

define docker_push
docker push etapau/hello-world:latest
endef

run-local:
	$(call docker_run)

image-latest:
	$(call build_image)

push-latest:
	$(call docker_push)

image: image-latest

run: run-local

push: push-latest
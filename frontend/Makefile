.PHONY: update-family-selector
update-family-selector:
	cd family-selector; yarn install; yarn build
	mkdir -p ../gestion_association/static/vendors/family-selector
	cp family-selector/build/app.js ../gestion_association/static/vendors/family-selector/family-selector.js

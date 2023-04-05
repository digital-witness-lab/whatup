init:
	yarn install

update-packages:
	yarn update

build-watch:
	npx tsc --watch --pretty --outDir build &
	npx nodemon --watch build ./build/index.js

build:
./build/index.js:
	npx tsc --pretty --outDir build

run: ./build/index.js
	node ./build/index.js

package main

import (
	"log"
	"os"
	"regexp"

	"github.com/tdewolff/minify/v2"
	"github.com/tdewolff/minify/v2/css"
	"github.com/tdewolff/minify/v2/js"
)

var (
	m *minify.M
)

func main() {
	// packs JS and CSS for production builds
	// many thanks to tdewolff/minify
	// https://github.com/tdewolff/minify

	m = minify.New()
	m.AddFunc("text/css", css.Minify)
	m.AddFuncRegexp(regexp.MustCompile("^(application|text)/(x-)?(java|ecma)script$"), js.Minify)

	log.Printf("Minifying CSS")
	loadAndMinify("style.css", "style.min.css", "text/css")

	log.Printf("Minifying JS")
	loadAndMinify("home.js", "home.min.js", "application/javascript")
	loadAndMinify("season.js", "season.min.js", "application/javascript")
	loadAndMinify("tournament.js", "tournament.min.js", "application/javascript")

	log.Printf("Done")
}

func loadAndMinify(filename string, minFilename string, mediaType string) error {
	dat, err := os.ReadFile("public/static/" + filename)
	if err != nil {
		log.Printf("Unable to open %s: %v", filename, err)
		return err
	}

	minDat, err := m.Bytes(mediaType, dat)
	if err != nil {
		log.Printf("Minify Error: %v", err)
		return err
	}

	err = os.WriteFile("public/static/" + minFilename, minDat, 0644);
	if err != nil {
		log.Printf("Unable to write minified %s: %v", minFilename, err)
		return err
	}

	return nil
}

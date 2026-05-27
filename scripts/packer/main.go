package main

import (
	"fmt"
	"log"
	"os"
	"regexp"
	"encoding/json"

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

	buildData, fileErr := os.ReadFile("build.json")
	if fileErr != nil {
		log.Printf("Unable to read build.json")
	}

	buildInfo := make(map[string]interface{})
	jsonErr := json.Unmarshal(buildData, &buildInfo)
	if jsonErr != nil {
		log.Printf("JSON parse error (build.json): %s", jsonErr)
	}

	packInfo := buildInfo["packer"].(map[string]interface{})

	cssFiles := packInfo["css"].(map[string]interface{})
	jsFiles := packInfo["js"].(map[string]interface{})

	m = minify.New()
	m.AddFunc("text/css", css.Minify)
	m.AddFuncRegexp(regexp.MustCompile("^(application|text)/(x-)?(java|ecma)script$"), js.Minify)

	log.Printf("Minifying CSS")
	for inCssFile, outCssFile := range cssFiles {
		loadAndMinify(
			fmt.Sprintf("%s/%s", packInfo["tpl_dir"], inCssFile),
			fmt.Sprintf("%s/%s", packInfo["out_dir"], outCssFile),
			"text/css",
		)
	}

	log.Printf("Minifying JS")
	for inJsFile, outJsFile := range jsFiles {
		loadAndMinify(
			fmt.Sprintf("%s/%s", packInfo["tpl_dir"], inJsFile),
			fmt.Sprintf("%s/%s", packInfo["out_dir"], outJsFile),
			"application/javascript",
		)
	}

	log.Printf("Done")
}

func loadAndMinify(filename string, minFilename string, mediaType string) error {
	dat, err := os.ReadFile(filename)
	if err != nil {
		log.Printf("Unable to open %s: %v", filename, err)
		return err
	}

	minDat, err := m.Bytes(mediaType, dat)
	if err != nil {
		log.Printf("Minify Error: %v", err)
		return err
	}

	err = os.WriteFile(minFilename, minDat, 0644);
	if err != nil {
		log.Printf("Unable to write minified %s: %v", minFilename, err)
		return err
	}

	return nil
}

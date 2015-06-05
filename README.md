# TagDog

TagDog gets genre information from the [EchoNest](http://the.echonest.com/) API and updates ID3 tag data on MP3 files. The MP3 files **must already have valid artist ID3 tag data**.

TagDog can be made to do other things (i.e. add artist/title information based on audio fingerprints) fairly easily due to its architecture but I have no need for that at the moment.

## Usage

Python 2.7 is required.

```sh
./tagdog.py [--dry-run] --echonest-key XXXXXXXXX /path/to/music/
```

## Architecture

1. Directories are scanned for files.
2. An empty "song info" object is created for each file.
3. A list of registered "populator" functions are run and passed a copy of the song info object. Each populator may add additional info to the song info object.
4. A list of registered writer functions are run and passed a copy of the song info object. A writer may write the data back to the file.

### Bundled Populators

* ID3Reader: Reads ID3 tags and updates the song info object.
* EchoNestTerms: Adds genre information if it does not yet exist using the "artist" field on the song info object.

### Bundled Writers

* ID3Writer: Writes ID3 tags from the song info object.

## License

See [LICENSE.txt](LICENSE.txt).
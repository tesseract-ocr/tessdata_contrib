tesseract model for Russian books in Petrine Orthography, mostly printed between Peter's civil-type reform of 1708 and the orthographic reform of 1918.

ru-petr1708.traineddata

## Credits and licence

The code here is under the Apache licence 2.0. `LICENSE` is the terms; `NOTICE` is the third-party attribution, in the form the licence requires be carried forward.

**ru_petr1708**, *Русскій Словарь въ Петровскомъ Правописаніи 1708 г.*, version 3.1 of 25 February 2015, © 2013 Danslav Slavenskoj, dual-licensed MIT or Apache 2.0 at your option. Included here as the upstream distribution, unmodified, with its own `LICENSE.txt` and `README.txt` — that directory carries only the MIT text, since that is what the 3.1 release shipped with; the Apache-2.0 option is granted by `NOTICE`. See <http://slavenskoj.com/> and <http://slavenica.com/>. `ru-petr1708` is a registered IANA language subtag under ISO 639, for Russian in the orthography running from the Petrine reform of 1708 to that of 1917.

**orus**, a fine-tune of the tesseract Russian model for pre-reform orthography, © 2025 Anastasya Bogdanova, Iskra Project, Apache licence 2.0. Trained on the social-democratic newspaper «Искра» (1900–1905); written up at <https://rpubs.com/AButon/orus_tesseract>, model at <https://github.com/AButon-8/iskra_ocr>. It is not included here; `tools/build_orusd.sh` takes it as an input, and `ru-petr1708.traineddata` is a fine-tune of it.

**Tesseract**, © Google Inc. and contributors, Apache licence 2.0. orus descends from its `rus` model, and both build scripts lift 667 punctuation and 222 number patterns out of stock `rus` besides.

Both models are accordingly combined derivatives of three Apache-2.0 works, since the word list is available under Apache-2.0 by the dual licence above. Each may therefore be redistributed under that one licence, satisfied by shipping `LICENSE` and `NOTICE` with it. Taking the word list under MIT instead is still permitted and then the MIT notice travels too. Neither restricts the use. The two models differ in one way that matters to the licence and is recorded in `NOTICE`: `orusd` copies the `orus` recogniser byte for byte, whereas in `ru-petr1708` every weight in the network is liable to have changed.

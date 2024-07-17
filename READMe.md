A crude barcode generator desktop for scanning and generating barcodes for our grocery store.
Generates an endpoint which receievs barcode scanned via QRBOT app
Only compiled for ARM MACOS
if you are running windows or linux please compile it yourself, I dont have access to other macines
I have dumped a requirements file too, you can install the requirements by running `pip install -r requirements.txt`

```
If it breaks delete the ones which break and run again
```

To compile run pyinstaller

pyinstaller main.spec --noconfirm

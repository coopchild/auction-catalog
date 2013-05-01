auction-catalog
===============

A system for generating our auction catalog and certificates if given a CSV export from 
our AuctionMaestro Pro software.

> `usage: catalog.py [-h] [--mode {catalog,certs}] catalog_file`

TODO
----

1. Right now the auction catalog is generated as a set of HTML files per Auction category. 
This was done to work around my own time limitations in tracking down a better solution.
2. Even better than generating HTML files (or even one file) would be to generate the
PDF file itself.
3. There's some funky dependancies on JavaScript (FTColumnFlow in particular) and how 
Chromimum handles printing said JavaScript. This sets off my red flag for "repeatable 
process". (impacts the catalog generation. The certificates are future-proof.)

[1]: http://www.maestrosoft.com/auction/index.html

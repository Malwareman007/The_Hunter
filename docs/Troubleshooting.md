# The_Hunter Troubleshooting

A quick troubleshooting guide for The_Hunter, to help you fix issues that might arise due to site changes.

Please submit pull requests and merge back if you fix something a social media site has changed!

## Why is The_Hunter Broken?

The_Hunter can stop working for certain social media sites that change the names of the HTML classes that The_Hunter uses to extract information from the web pages.

## How Do I Fix It?

To fix a broken site just open the relevant Python module in the [modules](modules) folder and update the class names that BeautifulSoup is searching for or change the parsing code.

In the image below you can see a number of the things The_Hunter relies on:

* The URL that it uses to search for the targets.
* The class name of the div which holds each of the people returned from the search.
* The code it uses to manipulate the extracted data to parse the link to the profile and profile picture.

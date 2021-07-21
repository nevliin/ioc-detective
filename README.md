# IoC Detective

A project for automatically converting PDF security reports into sigma rules for SIEMs

## Installation & Quick Start

* Install ``python-3.9.4`` and ``pip3``
* Download this git repository with ``git clone``.
* Execute ``pip install -r requirements.txt`` at the top level of this repository.
* Fill in the ``src/config.json``
  * Add your github user name in ``github_authn_user`` and a personal access token in ``github_authn_token`` (only used for increased API rate limiting)
  * (Optional) Add a link to the wiki to be displayed on the home page of the web interface.
  * Set ``flask_secret_key`` to a secure random value.
* Execute ``python3 -m src.main`` at the top level of this repository.
* Open ``localhost:5000`` in your browser.

## Testing

* Install ``pytest`` with pip
* Run ``pytest`` in the ``/test`` directory

## PDF Parsing

* Library Documentation: https://pdfminersix.readthedocs.io/en/latest/index.html
* On parsing PDFs: https://pdfminersix.readthedocs.io/en/latest/topic/converting_pdf_to_text.html

DeepL Translator Module

This is the DeepL translator module. It is intended for private use only, or to be deployed as a service for Lomb.

# Main Idea

This software consists of a server and a client. The server itself requires a Celery worker and a Selenium driver. 

If using locally, keep the SERVER_ADDRESS to localhost, otherwise set to whatever ip you wish the server to listen to.

Anyway, copy the src directory somewhere where you usually keep your binaries, like `/usr/local/bin/deepl_translator/`. Then copy the services in the services folder to wherever services live in your system. Then we can enable the celery worker and the backend server as services.

To translate some documents, use the client like this `client.py -t <target_language> -s <source_language> <file1>, <file2>, ... <file_n>`. The `-s` flag is optional, and if it isn't provided it will be inferred by parsing the filename like this: `<title>.<source_language>.<extension>`. Passing a flag overrides this behaviour. 

Anyway, what I like to do is to create some scripts in my path that point to the client with the relevant flag, like `deeplen` to translate to English. I guess in the future I will provide these as scripts so you can just symlink these somewhere in path.

# Architecture

The architecture is very straight forward. We want to create serializer and translator objects. The serializer object is responsible for I/O; it derives from a file a dictionary of *chunks*, which are usually sentences. The translator is passed this dictionary, which just has a lot of keys, and its main mission is to reliably fill out the values, i.e. the translation of those sentences in the source language into the target language.

The serializer can then write out a translated version of the original file, or just a json of all the chunks in the order they appear (this is what Lomb stores).

So the architecture just reflects that. We have serializers, translators, and server modules. The serializers and translators implement their own abstract base class so that there are no misunderstandings. The serializers module also contains methods to reject files if they are not parseable and a factory function to construct a serializer just from the extension.
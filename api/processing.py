# Processing takes in a request and applies to correct audio processing to it.
# This is a wrapper around the Ravel API Library to expose it to a web server
# in a more usable and meaningful way.
class Processor():
    def equalize(self):
        print("Processor equalizer")
        pass

    def compress(self):
        print("Processor compressor")
        pass

    def limit(self):
        print("Processor limiter")
        pass


class Equalize():
    """
    Creates a new Equalizer
    """
    def __init__(self):
        print("New equalizer being created: ", self)
        pass


class Compress():
    """
    Creates a new Compressor channel
    """

    def __init__(self):
        print("Creating a new Compressor: ", self)
        pass


class Handler(Processor):
    """
    The Handler is responsible for queueing and building the effects for each
    track.
    """
    def __init__(self):
        """
        creates a new builder
        """
        self._builder = None
        self._builder = Processor()
        print("assigned builder: ", self._builder)
        pass

    def Builder(self):
        """
        The Handler works with the builder instance to create the processing
        stack for each request.
        """
        return self._builder


if __name__ == "__main__":
    """
    Allows the script to be run from the command line for proof of concept
    """

    handler = Handler()
    print("handler created: ", handler)

    builder = handler.Builder()
    print("builder from handler: ", builder)

    processor = Processor()

    print("processor created: ", processor)
    processor.equalize()
    processor.compress()
    processor.limit()

    # e.g. apply some processing
    # handler.default_processing()
    # e.g. apply all processing
    # handler.all()
